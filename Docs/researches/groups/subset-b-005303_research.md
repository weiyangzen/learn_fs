# Research: subset-b-005303

Work item `subset-b-005303` covers the Fusion MegaRAID SAS fast-path mapping and command path files under `sources/distributed-fs/ceph-client/drivers/scsi/megaraid/`. Each file section is bounded with the reconciliation markers required by the research cron splitter.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fp.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.c

## Purpose

`megaraid_sas_fusion.c` is the Fusion-generation MegaRAID SAS controller implementation. It owns adapter initialization, DMA resource allocation, IOC init, interrupt and reply-queue handling, SCSI I/O request construction, management DCMD passthrough, RAID/JBOD map synchronization, SCSI task management, online controller reset, watchdog/fault handling, and crash-dump collection. It plugs these operations into `megasas_instance_template_fusion` so the common `megaraid_sas` driver core can call the Fusion-specific implementation.

The file bridges Linux SCSI/block-layer commands to the controller's MPI2-style request descriptor interface. It uses the fast-path geometry helpers from `megaraid_sas_fp.c` and the wire/data structures from `megaraid_sas_fusion.h`.

## Important APIs, Types, And Functions

Adapter reset and interrupt APIs include `megasas_adp_reset_wait_for_ready()`, `megasas_enable_intr_fusion()`, `megasas_disable_intr_fusion()`, `megasas_clear_intr_fusion()`, `megasas_read_fw_status_reg_fusion()`, and `megasas_adp_reset_fusion()`. These manipulate PCI registers through `instance->reg_set`, protect PCI config access during reset, and handle Fusion reset write sequences.

Command and DMA allocation APIs include `megasas_alloc_fusion_context()`, `megasas_free_fusion_context()`, `megasas_alloc_cmds_fusion()`, `megasas_free_cmds_fusion()`, `megasas_alloc_request_fusion()`, `megasas_alloc_reply_fusion()`, `megasas_alloc_rdpq_fusion()`, `megasas_create_sg_sense_fusion()`, and `megasas_allocate_raid_maps()`. They allocate the `fusion_context`, IO request frames, request descriptors, reply descriptor queues, RDPQ arrays, chain frames, sense buffers, command objects, firmware maps, and driver maps.

Initialization APIs include `megasas_fusion_update_can_queue()`, `megasas_configure_queue_sizes()`, `megasas_alloc_ioc_init_frame()`, `megasas_ioc_init_fusion()`, and `megasas_init_adapter_fusion()`. `megasas_ioc_init_fusion()` builds the IOC init payload, negotiates driver capabilities, posts the init frame, checks firmware status, and detects features like atomic descriptors.

Map synchronization APIs include `megasas_sync_pd_seq_num()` for JBOD/system-PD sequence maps, `megasas_get_ld_map_info()` for LD RAID maps, `megasas_get_map_info()` for validated fast-path map activation, and `megasas_sync_map_info()` for pended map-change notification.

I/O construction APIs include `megasas_build_and_issue_cmd_fusion()`, `megasas_build_io_fusion()`, `megasas_build_ldio_fusion()`, `megasas_build_ld_nonrw_fusion()`, `megasas_build_syspd_fusion()`, `megasas_make_sgl()`, `megasas_make_sgl_fusion()`, `megasas_make_prp_nvme()`, `megasas_set_pd_lba()`, `megasas_stream_detect()`, `megasas_set_raidflag_cpu_affinity()`, and `megasas_prepare_secondRaid1_IO()`. These functions prepare `MPI2_RAID_SCSI_IO_REQUEST` frames, RAID contexts, request descriptors, SGLs/PRPs, CDBs, MSI-X routing, and dual-command RAID1 writes.

Completion APIs include `complete_cmd_fusion()`, `megasas_complete_r1_command()`, `map_cmd_status()`, `megasas_blk_mq_poll()`, `megasas_irqpoll()`, `megasas_complete_cmd_dpc_fusion()`, and `megasas_isr_fusion()`. They drain reply descriptors, map firmware statuses to SCSI results, unmap DMA, return commands, update outstanding counters, and call `scsi_done()`.

Management and task-management APIs include `build_mpt_mfi_pass_thru()`, `build_mpt_cmd()`, `megasas_issue_dcmd_fusion()`, `megasas_issue_tm()`, `megasas_task_abort_fusion()`, `megasas_reset_target_fusion()`, and `megasas_check_mpio_paths()`. They tunnel MFI frames over Fusion passthrough and send MPI2 task management requests for abort and target reset.

Reset/fault APIs include `megasas_wait_for_outstanding_fusion()`, `megasas_reset_reply_desc()`, `megasas_refire_mgmt_cmd()`, `megasas_return_polled_cmds()`, `megasas_reset_fusion()`, `megasas_fusion_start_watchdog()`, `megasas_fusion_stop_watchdog()`, `megasas_fault_detect_work()`, `megasas_fusion_crash_dump()`, and `megasas_fusion_ocr_wq()`.

## Control Flow And Integration

Probe-time initialization enters through the instance template's `.init_adapter = megasas_init_adapter_fusion`. The function reads firmware queue-depth capabilities, calculates host and controller queue sizes, derives maximum chain frame sizes from scratchpad bits, allocates IOC init memory, MFI commands, Fusion commands, request/reply descriptors, sense and SG buffers, issues IOC init, reads controller info, allocates RAID maps, fetches and validates the LD map, and pends map synchronization if fast-path mapping succeeds.

Normal SCSI I/O enters `.build_and_issue_cmd = megasas_build_and_issue_cmd_fusion`. The function first enforces LDIO and firmware outstanding thresholds, gets the tag-indexed `megasas_cmd_fusion`, obtains a request descriptor, calls `megasas_build_io_fusion()`, assigns the SMID, optionally creates a peer command for RAID1 fast-path writes, increments per-device busy accounting, and posts one or two descriptors through `megasas_fire_cmd_fusion()`.

`megasas_build_io_fusion()` resets reusable frame fields, copies the SCSI CDB, sets initial CDB length, dispatches by `megasas_cmd_type()` to LD read/write, LD non-read/write, system-PD read/write, or system-PD non-read/write builders, constructs SGLs, stores the SGE count in the appropriate RAID context layout, sets SCSI read/write control flags, installs sense buffer address, and links the SCSI command to the Fusion command.

`megasas_build_ldio_fusion()` is the main LD hot path. It parses 6/10/12/16-byte read/write CDBs into LBA and transfer length, calls `MR_BuildRaidContext()` when a validated RAID map exists, chooses MSI-X index, applies Ventura RAID1 write and bandwidth-limiting rules, updates stream-detection and CPU-affinity hints, and then chooses fast-path physical I/O or LD firmware I/O. Fast path rewrites the CDB to PD LBA with `megasas_set_pd_lba()`, sets `MPI2_FUNCTION_SCSI_IO_REQUEST`, installs physical devhandle and LUN, may perform RAID1 read load balancing through `get_updated_dev_handle()`, and records alternate mirror handles for dual-command RAID1 writes. Non-fast-path LD I/O uses `MEGASAS_MPI2_FUNCTION_LD_IO_REQUEST` and target id as devhandle.

Completion is reply-descriptor driven. `megasas_isr_fusion()`, blk-mq polling, irq_poll, or the DPC all call `complete_cmd_fusion()`. It reads descriptors from `fusion->reply_frames_desc[MSIxIndex]` using `fusion->last_reply_idx`, looks up the command by SMID, switches on request `Function`, completes task management completions, maps SCSI status for fast-path and LD I/O, handles RAID1 peer completion aggregation, completes MFI passthrough commands, marks reply descriptors unused, updates the reply-post host index register, and restores queue depth as needed.

Online controller reset enters `megasas_reset_fusion()`. It serializes with `reset_mutex`, handles crash-dump forced-fault mode for I/O/DCMD timeout, disables interrupts and irq_poll, drains outstanding completions, returns or requeues pending SCSI commands on failure, attempts adapter reset and IOC init up to bounded retries, refires or completes management commands, reloads RAID/JBOD maps, resets stream-detection state, re-enables interrupts and irq_poll, refreshes target properties, restarts SR-IOV heartbeat, reconfigures crash-dump settings, and either returns the adapter to operational state or kills the HBA.

## State And Persistence Behavior

The dominant state container is `struct fusion_context`, allocated in `megasas_alloc_fusion_context()` and attached to `instance->ctrl_context`. It owns command arrays, DMA pools, request frames, reply descriptors, RDPQ tracking, map buffers, load-balance caches, span caches, IOC init memory, and feature flags. `struct megasas_instance` contributes global adapter state: queue depths, outstanding counters, map ids, reset flags, heartbeat state, crash-dump buffers, interrupt maps, and SCSI host configuration.

Most state is volatile and rebuilt at probe or OCR. The firmware remains the source of truth for controller configuration, LD maps, PD sequence maps, and capability bits. Driver persistence across reset consists of preserving software allocations where possible, refiring eligible management commands, returning SCSI commands to the mid-layer, and refreshing firmware-derived maps after IOC init.

Several double-buffering schemes are important:

- `fusion->ld_map[2]` and `fusion->ld_drv_map[2]` alternate by `instance->map_id & 1`.
- `fusion->pd_seq_sync[2]` alternates by `instance->pd_seq_map_id & 1`.
- RDPQ reply queues are split into chunks so groups of queue descriptors stay within required 4 GB DMA boundaries.

Outstanding counts are held in atomics such as `fw_outstanding`, `ldio_outstanding`, per-device balanced-mode busy counters, load-balance PD pending counters, and blk-mq poll busy flags. Reset flags `MEGASAS_FUSION_IN_RESET` and `MEGASAS_FUSION_OCR_NOT_POSSIBLE` gate ISR and reset behavior.

Crash dump state uses `instance->crash_dump_buf` as firmware DMA input and `instance->crash_buf[]` vmalloc buffers as host-side copies. `fw_crash_state`, `fw_crash_buffer_size`, `drv_buf_index`, and `drv_buf_alloc` track availability for user-space collection.

## Dependencies

This file depends on `megaraid_sas_fusion.h` for all Fusion wire formats and context structures, `megaraid_sas.h` for common driver state and MFI command definitions, and `megaraid_sas_fp.c` APIs for RAID map validation and LD-to-PD mapping. It integrates with Linux PCI, DMA pools/coherent DMA, SCSI mid-layer, blk-mq polling, irq_poll, delayed workqueues, timers, DMI, endian helpers, atomics, mutexes, and kernel logging.

External driver functions include `megasas_complete_cmd()`, `megasas_transition_to_ready()`, `megasas_get_ctrl_info()`, `megasas_get_target_prop()`, `megasas_set_dynamic_target_properties()`, `megasas_setup_jbod_map()`, `megasas_set_crash_dump_params()`, `megasas_get_snapdump_properties()`, `megaraid_sas_kill_hba()`, `megasas_check_and_restore_queue_depth()`, MFI command allocation/return/issue helpers, and SR-IOV heartbeat helpers.

## Risks And Edge Cases

Resource allocation has strict DMA boundary requirements. Sense buffers, request frames, reply queues, and RDPQ chunks must not cross 4 GB boundaries for supported controllers. The code retries with alignment pools or reduces queue depth in some cases, but allocation failure paths must avoid leaks and partially initialized pointer use.

The I/O hot path reuses preallocated frames by tag. Any field not reset in `megasas_build_io_fusion()` or `megasas_return_cmd_fusion()` can leak stale context into later commands. This is especially sensitive for `RaidContext`, `ChainOffset`, EEDP fields, peer SMIDs, `r1_alt_dev_handle`, SGL flags, and stream-detection bits.

Fast-path routing correctness depends on the RAID map validation and geometry code. Bugs in `MR_BuildRaidContext()`, CDB rewriting, or devhandle selection can misdirect physical I/O. The fallback path must disable fast path when maps are unavailable, PD handles are invalid, or read-ahead/stream policies require LD I/O.

RAID1 fast-path writes issue two commands for one SCSI command. Completion only finishes the SCSI command after both peer commands complete, and it chooses error status from the failing peer when needed. Peer SMID, alternate devhandle, outstanding counter, and command return ordering are all correctness-critical.

Completion and reset concurrency is delicate. Reply queues may be drained by ISR, irq_poll, blk-mq poll, DPC, reset, and synchronized IRQ paths. `access_irq_context()` and per-queue `busy_mq_poll` reduce concurrent consumers, but reset must disable interrupts, synchronize IRQs, drain completions, and return commands without double completion.

OCR is high risk because it mutates nearly every state domain: outstanding commands, firmware state, maps, management command ownership, queue depths, stream caches, heartbeat timers, target properties, and crash-dump settings. A failed reset kills the HBA. SR-IOV VF behavior has special heartbeat and settle-time paths that differ from PF reset.

NVMe PRP construction is another boundary-sensitive area. `megasas_make_prp_nvme()` splits scatterlist entries into PRP entries, inserts PRP list pointers at page boundaries, and relies on `max_chain_frame_sz` being large enough. Incorrect page-size assumptions or oversized SGLs can corrupt chain frames.

## Test Signals

Probe tests should show successful IOC init, correct queue-depth logging, successful controller info read, RAID map validation, and no DMA allocation boundary errors. I/O tests should cover LD fast path, LD firmware path, system PD path, non-read/write commands, NVMe fast path with PRPs, chained SGLs, T10 PI/EEDP read/write CDBs, RAID1 read load balancing, RAID1 dual fast-path writes, stream-detected read-ahead fallback, and multi-queue MSI-X routing.

Completion tests should verify residual counts and sense data for check-condition paths, `DID_IMM_RETRY` on config sequence mismatch, bad-target mapping for offline/missing devices, correct decrement of `fw_outstanding` and `ldio_outstanding`, no double completion during irq_poll/ISR races, and correct reply-post host index updates.

Reset tests should inject SCSI I/O timeout, MFI DCMD timeout, firmware fault, crash-dump available, failed IOC init, map fetch failure, SR-IOV heartbeat timeout, and management commands active during OCR. Passing signals are returned or requeued SCSI commands, no stuck outstanding counters, refreshed maps, re-enabled interrupts, restarted heartbeat where applicable, and adapter state restored to `MEGASAS_HBA_OPERATIONAL` or clean HBA kill on unrecoverable failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.h

## Purpose

`megaraid_sas_fusion.h` defines the Fusion controller ABI and in-driver data structures used by `megaraid_sas_fusion.c`, `megaraid_sas_fp.c`, and the common MegaRAID SAS code. It describes MPI2/MegaRAID request and reply frames, RAID context layouts for pre-Ventura and Ventura/G35 controllers, RAID map layouts from firmware, driver-normalized map layouts, SGL/PRP structures, task-management frames, load-balance and uneven-span caches, command objects, and the `fusion_context` that owns Fusion runtime resources.

This header is the contract that makes the driver command path and map path agree on field offsets, endian types, bit masks, and controller feature flags. Many structures directly mirror firmware DMA formats, so layout stability and endian correctness are central.

## Important Types And Constants

Core controller constants include `MEGA_MPI2_RAID_DEFAULT_IO_FRAME_SIZE`, `MEGASAS_MPI2_FUNCTION_PASSTHRU_IO_REQUEST`, `MEGASAS_MPI2_FUNCTION_LD_IO_REQUEST`, `MFI_FUSION_ENABLE_INTERRUPT_MASK`, `MEGASAS_FUSION_MAX_RESET_TRIES`, `MAX_MSIX_QUEUES_FUSION`, RDPQ chunk sizing, reset bits, and chain-frame sizing masks. Request descriptor flags define LD I/O, MFA passthrough, no-lock, fast-path I/O, high-priority, and SCSI I/O descriptor types.

`struct RAID_CONTEXT` is the older MegaRAID-specific I/O context placed where SGLs would normally begin in the MPT frame. It carries timeout, region-lock flags, virtual disk target id, row LBA, lock length, firmware status, RAID flags, SGE counts, config sequence, span/arm, and priority.

`struct RAID_CONTEXT_G35` is the Ventura/G35 layout. It replaces several byte fields with `nseg_type`, `routing_flags`, and a `flow_specific` union used for RAID5/6 RMW indices, RAID1 peer SMIDs, or R5/6 arm maps. It also packs stream-detected and SGE-count bits in a union. Inline helpers `set_num_sge()`, `get_num_sge()`, and `is_stream_detected()` manipulate this format.

`union RAID_CONTEXT_UNION` lets request frames expose either RAID context layout at the same offset. Span/arm and RAID5/6 arm-map masks define how physical arm and span are packed into firmware-visible fields.

MPI2 and SGL definitions include `MPI25_IEEE_SGE_CHAIN64`, `MPI2_SGE_SIMPLE_UNION`, `MPI2_SGE_CHAIN_UNION`, IEEE simple/chain SGE formats, `union MPI2_SGE_IO_UNION`, `union MPI2_SCSI_IO_CDB_UNION`, `MPI2_RAID_SCSI_IO_REQUEST`, `MPI2_IOC_INIT_REQUEST`, and PRP/NVMe SGE flag constants. These are used for normal SGLs, chained SGLs, NVMe PRP lists, IOC init, and T10 PI/EEDP CDB embedding.

Request/reply descriptor types include `union MEGASAS_REQUEST_DESCRIPTOR_UNION` and `union MPI2_REPLY_DESCRIPTORS_UNION`, with variants for default, high-priority, SCSI I/O, target, RAID accelerator, and MFA descriptors. `union desc_value` and `union desc_word` are convenience views for low/high descriptor words.

Task management structures include `MPI2_SCSI_TASK_MANAGE_REQUEST`, `MPI2_SCSI_TASK_MANAGE_REPLY`, `MR_TASK_MANAGE_REQUEST`, `MR_TM_REQUEST`, `MR_TM_REPLY`, task type constants, and response-code constants. They support abort task and target reset paths in the Fusion implementation.

RAID map structures include `MR_DEV_HANDLE_INFO`, `MR_ARRAY_INFO`, `MR_QUAD_ELEMENT`, `MR_SPAN_INFO`, `MR_LD_SPAN`, `MR_SPAN_BLOCK_INFO`, `MR_CPU_AFFINITY_MASK`, `MR_IO_AFFINITY`, `MR_LD_RAID`, `MR_LD_SPAN_MAP`, `MR_FW_RAID_MAP`, `MR_FW_RAID_MAP_ALL`, `MR_FW_RAID_MAP_EXT`, `MR_FW_RAID_MAP_DYNAMIC`, `MR_RAID_MAP_DESC_TABLE`, `MR_DRV_RAID_MAP`, and `MR_DRV_RAID_MAP_ALL`. These describe firmware legacy, extended, and dynamic map formats plus the normalized driver-side map. Static assertions verify flexible-array overlap offsets for the wrapped layouts.

Runtime helper state includes `struct IO_REQUEST_INFO` for per-I/O geometry and fast-path decisions, `struct megasas_cmd_fusion` for one Fusion command, `struct LD_LOAD_BALANCE_INFO` for RAID1 mirror selection, `LD_SPAN_SET`/`LD_SPAN_INFO` for uneven-span derived ranges, `STREAM_DETECT`/`LD_STREAM_DETECT` for sequential I/O hints, `rdpq_alloc_detail` for reply queue chunk ownership, `MR_PD_CFG_SEQ` and `MR_PD_CFG_SEQ_NUM_SYNC` for JBOD sequence maps, and `struct fusion_context` for all Fusion resources attached to an adapter.

Public prototypes at the end expose Fusion lifecycle and map functions: `megasas_free_cmds_fusion()`, `megasas_ioc_init_fusion()`, `megasas_get_map_info()`, `megasas_sync_map_info()`, `megasas_release_fusion()`, `megasas_reset_reply_desc()`, `megasas_check_mpio_paths()`, and `megasas_fusion_ocr_wq()`.

## Control Flow And Integration

The command path allocates one `megasas_cmd_fusion` per MPT/Fusion command. Each command points to a DMA-backed `MPI2_RAID_SCSI_IO_REQUEST`, optional chain frame, sense buffer, request descriptor, associated SCSI command, and sync-command index for tunneled MFI commands. `fusion_context->cmd_list` maps SMID/tag indexes to these command objects, and completion uses reply SMID values to recover the command.

The I/O frame layout is centered on `struct MPI2_RAID_SCSI_IO_REQUEST`: devhandle, function, sense address, SGL flags, data length, CDB, RAID context union, and SGL storage. `megaraid_sas_fusion.c` fills this structure and posts a `MEGASAS_REQUEST_DESCRIPTOR_UNION` to the inbound queue. Firmware writes completion information into the RAID context and posts a `MPI2_REPLY_DESCRIPTORS_UNION` entry.

The map path uses firmware layouts as DMA inputs and `MR_DRV_RAID_MAP_ALL` as the normalized output. `megaraid_sas_fp.c` consumes `MR_LD_RAID`, `MR_LD_SPAN_MAP`, `MR_ARRAY_INFO`, and `MR_DEV_HANDLE_INFO` to calculate fast-path placement. Dynamic maps use descriptor tables to locate the arrays inside a variable-size firmware buffer.

The reset path uses constants and structures from this header to reset descriptors (`ULLONG_MAX` unused markers), refill IOC init fields, rebuild maps, and mark reset status. Request descriptor flags and function codes determine whether outstanding Fusion commands represent SCSI I/O, LD I/O, passthrough MFI commands, or task management commands.

## State And Persistence Behavior

This header defines volatile in-memory and DMA state; it does not itself persist data. Firmware owns durable controller state. The driver stores firmware-derived snapshots in DMA buffers (`ld_map`, `pd_seq_sync`) and normalized non-DMA maps (`ld_drv_map`). `fusion_context` fields describe allocation sizes and queue depths so resources can be reused across normal I/O and rebuilt during OCR.

Endian annotations are part of the state contract. Firmware-facing numeric fields are commonly `__le16`, `__le32`, `__le64`, or `__be16`/`__be32` for SCSI EEDP CDB fields. Driver code must explicitly convert when reading or writing these fields.

The header also defines feature and policy bits that affect runtime state: fast-path capability, read-ahead capability, PI modes, cache bypass capability, region-lock request types, CPU affinity masks, write mode, LD state, stream detection, and RAID5/6 division-offload subtype.

## Dependencies

The header assumes Linux kernel type definitions, endian annotations, flexible-array helpers, static assertions, DMA address types, atomics, completions, SCSI command forward declarations, and MegaRAID common types from `megaraid_sas.h` included by users. It is tightly coupled to firmware ABI expectations, especially fixed offsets in `MPI2_RAID_SCSI_IO_REQUEST`, `RAID_CONTEXT`, `RAID_CONTEXT_G35`, request descriptors, reply descriptors, and RAID map layouts.

It also depends on constants defined elsewhere for adapter type, crash dump sizing, SCSI host state, target indexing, and common MFI command handling. The source files using this header supply those through their include of `megaraid_sas.h`.

## Risks And Edge Cases

The main risk is ABI drift. Any change to structure packing, field order, endian type, bitfield order, or fixed-size constants can break firmware communication. The big-endian bitfield branches in RAID capability, CPU affinity, and task-management flags must remain consistent with firmware layout. The static assertions around trailing overlap protect two map wrappers, but many other structures rely on implicit layout discipline.

Flexible and variable-size structures require careful allocation. `MR_FW_RAID_MAP`, `MR_FW_RAID_MAP_DYNAMIC`, `MR_PD_CFG_SEQ_NUM_SYNC`, `MR_DRV_RAID_MAP`, and `MPI2_RAID_SCSI_IO_REQUEST` all have flexible or overlayed trailing data. Callers must use the correct size for firmware generation, adapter capability, and queue depth; under-allocation can corrupt adjacent memory, while over-reading firmware-provided descriptor counts can copy beyond valid map data.

Bit packing is correctness-critical. `span_arm`, `r56_arm_map`, `routing_flags`, `raid_flags`, `nseg_type`, stream-detected bits, SGE counts, and descriptor `RequestFlags` are interpreted by firmware. A wrong shift or endian conversion can route I/O to the wrong path, disable locking, choose the wrong controller CPU, or misreport SGL length.

The driver-normalized map increases maximum dimensions to dynamic sizes (`MAX_LOGICAL_DRIVES_DYN`, `MAX_API_ARRAYS_DYN`, `MAX_RAIDMAP_PHYSICAL_DEVICES_DYN`). Code that still assumes legacy 64-LD or 256-PD limits can mismatch these structures. Conversely, firmware maps that report counts above the allocated limits must be rejected before copying.

## Test Signals

Compile-time signals include no structure-offset assertion failures, no flexible-array warnings, and clean builds on little-endian and big-endian configurations. Runtime signals include successful IOC init with correct request frame size, successful fast-path map validation across legacy, extended, and dynamic RAID maps, correct SGE counts for main and chained SGLs, correct NVMe PRP flags, task management replies decoded correctly, and reply descriptors returning valid SMIDs.

Regression tests should exercise adapters below and above `INVADER_SERIES`/`VENTURA_SERIES`, RDPQ and non-RDPQ reply modes, 64-bit and non-64-bit DMA capability negotiation, more-than-256 JBOD support, dynamic map descriptors, RAID1 peer SMID completion, stream-detection bit setting/clearing, and T10 PI CDB/EEDP fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.h -->
