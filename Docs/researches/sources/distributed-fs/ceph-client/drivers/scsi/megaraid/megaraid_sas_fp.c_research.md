# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fp.c

## Purpose

`megaraid_sas_fp.c` implements the driver-side RAID fast-path address mapping for MegaRAID SAS Fusion controllers. It converts firmware RAID maps into a driver-normalized map, validates the map, computes logical-drive to physical-drive placement for even and uneven spans, prepares RAID region-lock context for I/O, and supports RAID1/10 read load balancing. It is the geometry and placement companion to `megaraid_sas_fusion.c`: Fusion command construction calls `MR_BuildRaidContext()` here before deciding whether an I/O can be sent as fast-path physical disk I/O or must be routed as LD firmware I/O.

The file is not persistent storage by itself. Its important state lives in per-adapter `fusion_context` allocations: double-buffered firmware maps, double-buffered driver maps, `log_to_span` uneven-span caches, and `load_balance_info` arrays. Firmware supplies authoritative maps through DCMDs; this file translates those maps into CPU-endian, driver-friendly state and updates transient counters for runtime path selection.

## Important APIs, Types, And Functions

Public helper APIs exported to the rest of the driver include `MR_LdRaidGet()`, `MR_ArPdGet()`, `MR_LdSpanArrayGet()`, `MR_PdDevHandleGet()`, `MR_GetLDTgtId()`, `MR_TargetIdToLdGet()`, `MR_ValidateMapInfo()`, `MR_BuildRaidContext()`, `mr_update_span_set()`, `mr_update_load_balance_params()`, and `get_updated_dev_handle()`. These functions all operate on `struct MR_DRV_RAID_MAP_ALL`, `struct IO_REQUEST_INFO`, and `struct RAID_CONTEXT`/`RAID_CONTEXT_G35` definitions from `megaraid_sas_fusion.h`.

`MR_PopulateDrvRaidMap()` is the first major stage. It accepts the active map id and copies one of three possible firmware layouts into the normalized driver map:

- dynamic descriptor-table maps when `instance->max_raid_mapsize` is set;
- extended 256-VD maps when `instance->supportmax256vd` is set;
- legacy flexible-array maps otherwise.

It initializes `ldTgtIdToLd` to invalid, copies device handles, target mappings, array maps, and LD span maps, and sets `totalSize` to the value expected by validation. Dynamic maps use descriptor table entries of type `RAID_MAP_DESC_TYPE_DEVHDL_INFO`, `RAID_MAP_DESC_TYPE_TGTID_INFO`, `RAID_MAP_DESC_TYPE_ARRAY_INFO`, and `RAID_MAP_DESC_TYPE_SPAN_INFO`.

`MR_ValidateMapInfo()` calls `MR_PopulateDrvRaidMap()`, checks `totalSize` against the expected layout size, optionally rebuilds uneven-span lookup data with `mr_update_span_set()`, optionally refreshes RAID1 load-balance flags with `mr_update_load_balance_params()`, converts LD RAID capability bits to CPU endian, and updates `instance->ld_ids_prev`/`instance->ld_ids_from_raidmap`. A successful return enables `fusion->fast_path_io` in the caller.

Geometry helpers include `MR_GetSpanBlock()` for classic even-span row-to-span mapping, `mr_spanset_get_span_block()` for uneven spans, `get_row_from_strip()`, `get_strip_from_row()`, `get_arm_from_strip()`, and `get_arm()`. They use firmware span block quads, strip offsets, row widths, and RAID level rules to translate LD strips/rows into physical span, arm, and disk block values. `mega_mod64()` and `mega_div64_32()` wrap `do_div()` for 64-bit arithmetic in kernel code.

`MR_GetPhyParams()` handles normal even-span physical placement. `mr_spanset_get_phy_params()` handles uneven-span placement using the cached `log_to_span` data. Both fill `io_info->devHandle`, `io_info->pd_interface`, `io_info->pdBlock`, `io_info->span_arm`, and `io_info->pd_after_lb`; they also set RAID context `span_arm` and, for unavailable PDs, force region-lock behavior or fall back to alternate RAID1 mirror arms where possible.

`mr_get_phy_params_r56_rmw()` prepares Ventura/Aero RAID5/6 division-offload write context. It computes logical arm, data arm, P/Q parity arms, row LBA, and `r56_arm_map`, then marks `raid_flags` with `MR_RAID_FLAGS_IO_SUB_TYPE_R56_DIV_OFFLOAD`.

`MR_BuildRaidContext()` is the central API used by Fusion command building. It parses the logical drive target, calculates start/end strip and row, region-lock start/length, fast-path eligibility, timeout, config sequence, RAID LUN pointer, and physical parameters. It returns true when a RAID context was built, while `io_info->fpOkForIo` carries whether fast-path physical I/O is actually allowed for this request.

`mr_update_span_set()` derives per-LD `LD_SPAN_SET` records from firmware span quads. It caches log LBA ranges, span row ranges, data strip ranges, data row ranges, span row data width, strip offsets per span, and diff values for each quad element. `mr_update_load_balance_params()` marks only optimal RAID1 logical drives as load-balance capable, constrained by the module parameter `lb_pending_cmds`.

`megasas_get_best_arm_pd()` and `get_updated_dev_handle()` implement RAID1 read load balancing. They choose between mirror arms using pending command counts and last-accessed block proximity, update `io_info->span_arm`/`pd_after_lb`, increment the chosen PD pending counter, and return the selected device handle.

## Control Flow And Integration

The normal map path starts in `megaraid_sas_fusion.c`: a DCMD fetches the firmware LD map into `fusion->ld_map[map_id & 1]`, then `megasas_get_map_info()` calls `MR_ValidateMapInfo()`. Validation populates `fusion->ld_drv_map[map_id & 1]`; if successful, Fusion command building may use fast path. On config changes, `megasas_sync_map_info()` pends a map-update command and the active `instance->map_id` toggles through the double-buffered map arrays.

The normal I/O path enters `MR_BuildRaidContext()` from `megasas_build_ldio_fusion()`. The caller has already parsed the SCSI CDB into an LD target, starting LBA, block count, and direction. `MR_BuildRaidContext()` maps the LD target id to an LD index, loads RAID properties, checks whether uneven-span support is needed, computes region-lock information, tests firmware-advertised fast-path capability bits, and, when fast path is allowed, calls either the even-span or uneven-span physical-parameter helper. Fusion then decides whether to emit `MPI2_FUNCTION_SCSI_IO_REQUEST` fast-path I/O or `MEGASAS_MPI2_FUNCTION_LD_IO_REQUEST` LD I/O.

Read I/O that is not fast-path capable may still call the physical-parameter functions strip by strip. That keeps context and error handling informed even when final execution is firmware-routed. RAID5/6 write offload is a special early path for adapters with `fusion->r56_div_offload`: after region lock fields are built, `mr_get_phy_params_r56_rmw()` sets the division-offload fields and returns.

The RAID1 load-balance path is intentionally split. This file marks LDs as eligible during map validation. At I/O build time, Fusion checks `fusion->load_balance_info[device_id].loadBalanceFlag` and `io_info.isRead`; if both are true, it calls `get_updated_dev_handle()` and later completion decrements the selected PD's pending counter.

## State And Persistence Behavior

Persistent controller configuration is owned by firmware. This file maintains volatile mirrors and derived caches only:

- `fusion->ld_drv_map[2]` contains driver-normalized RAID maps.
- `fusion->log_to_span` contains derived uneven-span lookup tables.
- `fusion->load_balance_info` contains load-balance flags, per-PD pending counters, and last-accessed block positions.
- `instance->ld_ids_prev` and `instance->ld_ids_from_raidmap` snapshot LD ids visible in the last validated map.
- `io_info` is per-command scratch state and is not retained after command construction, except selected values copied into the Fusion command and RAID context.

The module parameter `lb_pending_cmds` is read-only from sysfs permissions (`0444`) but can be set at module load. The function clamps out-of-range values back to `LB_PENDING_CMDS_DEFAULT`.

## Dependencies

This file depends heavily on the structures and constants in `megaraid_sas_fusion.h`, including RAID maps, span maps, request info, RAID context layouts, region-lock types, span/arm masks, and PD invalid constants. It also depends on `megaraid_sas.h` for `struct megasas_instance`, adapter type constants, target id macros, and controller state fields. Kernel dependencies include DMA-safe endian conversion helpers, `do_div()`, atomics, module parameters, SCSI command types, and PCI device logging.

## Risks And Edge Cases

The primary risks are geometry correctness and stale map handling. A bad target-to-LD mapping, span quad, row width, endian conversion, or `span_arm` calculation can send fast-path I/O to the wrong physical disk/LBA. The code has some guardrails, such as size validation, invalid span checks, zero divisor logging, invalid PD detection, and fallback from fast path when `devHandle` remains invalid, but it trusts firmware-provided map contents beyond those checks.

Uneven-span support is complex. `get_row_from_strip()`, `get_strip_from_row()`, `get_arm_from_strip()`, and `mr_spanset_get_span_block()` rely on the derived `LD_SPAN_SET` ranges being strictly consistent with firmware quads. Off-by-one errors around `data_strip_end`, `data_row_end`, or strip offsets would affect only certain span layouts and may be hard to reproduce.

RAID1 load balancing mutates shared per-PD counters and last-block data. The pending counters are atomic, but `last_accessed_block` is a plain `u64` update, so it is a heuristic rather than strictly synchronized state. Completion must correctly decrement pending counts for the selected PD; missed decrements would bias future arm choices.

Large or cross-row I/O affects region-lock length. Incorrect region-lock start/length can either reduce concurrency unnecessarily or, worse, under-lock overlapping parity or mirror updates. RAID5/6 division-offload writes are also sensitive to correct P/Q/logical-arm encoding.

## Test Signals

Useful validation signals include successful `megasas_get_map_info()` enabling `fusion->fast_path_io`, no "map info structure size" or invalid span logging, stable I/O across RAID0/1/5/6 and uneven-span virtual drives, no data miscompare under fast-path reads/writes, correct fallback to LD I/O when PD handles are invalid, and balanced RAID1 read completions without stuck `scsi_pending_cmds`. Targeted tests should cover 6/10/12/16-byte read/write CDBs, single-strip and multi-strip I/O, row boundary crossings, degraded RAID1 mirror reads, RAID5/6 writes with and without division offload, map updates during I/O, and module-load values for `lb_pending_cmds` outside and inside the valid range.
