# Research: subset-b-003541

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.h

## Purpose

`smu_v15_0_8_ppt.h` declares the SMU 15.0.8 power-play table surface and metrics schemas. It exposes topology limits for XGMI links, GFX clocks, XCCs, VCN/JPEG engines, AIDs/MIDs, and HBM stacks; the `PPTable_t` structure; and `smu_v15_0_8_set_ppt_funcs()` for installing ASIC-specific SMU callbacks. Under `SWSMU_CODE_LAYER_L2` it uses the common SMU metrics metaprogramming macros to declare packed GPU, GPU-board temperature, and baseboard temperature metric classes.

## Important APIs, Types, And Functions

The public type is `PPTable_t`, which caches socket power limits, graphics/fabric/GL2/UCLK/SOC/LCLK/VCN clocks, thermal/CTF limits for MID/AID/XCD/HBM, public serial numbers, PPT1 limits, and an `init` flag. The main macro APIs are `SMU_15_0_8_METRICS_FIELDS`, `SMU_15_0_8_GPUBOARD_TEMP_METRICS_FIELDS`, and `SMU_15_0_8_BASEBOARD_TEMP_METRICS_FIELDS`, each consumed by `DECLARE_SMU_METRICS_CLASS`. The metrics include temperatures, power, PCIe/XGMI counters, activity accumulators, firmware timestamps, clock arrays, JPEG/VCN busy percentages, and board/baseboard sensor fields.

## Control Flow, State, And Persistence

This header has no runtime control flow. Its generated inline class initializers zero-fill with `0xff`, encode metric attribute/unit/type metadata, set the metrics table header, and count fields. State persists only in consumers: `PPTable_t` is a driver cache, while metrics snapshots mirror firmware-owned tables and platform sensors.

## Dependencies And Integration Points

The file depends on `smu_cmn.h` and the AMDGPU metrics attribute/type/unit definitions when layer L2 is enabled. It integrates with the SMU 15.0.8 PPT implementation, sysfs/metrics export paths, power/thermal limit handling, topology-aware monitoring, and firmware table copy paths in `smu_cmn.c`.

## Risks And Test Signals

Risks are schema drift against firmware metrics layout, wrong array bounds for multi-die products, and stale `PPTable_t` defaults being treated as initialized. Tests should cover SMU 15.0.8 build coverage, metrics table size/revision checks, sensor export on multi-AID/XCC/HBM hardware, and firmware table compatibility during probe/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c

## Purpose

`smu_cmn.c` implements shared SWSMU helpers: SMU v1 mailbox transport, response decoding, common-to-ASIC mapping translation, feature enablement, table transfers, metrics caching, power-management policy descriptions, DPM level formatting, PCIe helper indexes, and firmware version querying. It is the central glue between AMDGPU power-management code and ASIC-specific `ppt_funcs`.

## Important APIs, Types, And Functions

The transport API is `smu_msg_v1_ops`, with `smu_msg_v1_send_msg`, `smu_msg_v1_wait_response`, `smu_msg_v1_decode_response`, and debug-mailbox send support. Public wrappers include `smu_cmn_send_smc_msg_with_param`, `smu_cmn_send_smc_msg`, debug variants, `smu_msg_wait_response`, and `smu_msg_send_async_locked`. Mapping and feature helpers include `smu_cmn_to_asic_specific_index`, `smu_cmn_feature_is_supported`, `smu_cmn_feature_is_enabled`, `smu_cmn_get_enabled_mask`, `smu_cmn_feature_update_enable_state`, `smu_cmn_set_pp_feature_mask`, and `smu_cmn_disable_all_features_with_exception`. Table helpers include `smu_cmn_update_table_read_arg`, `smu_cmn_write_watermarks_table`, `smu_cmn_write_pptable`, `smu_cmn_get_metrics_table`, and `smu_cmn_get_combo_pptable`.

## Control Flow, State, And Persistence

SMU message flow validates mappings and argument counts, filters VF-only commands, locks the mailbox, applies RAS priority filtering, checks firmware hang/init state, pre-polls for previous completion, writes args/message registers, optionally returns for async commands, post-polls, decodes the response, updates `smc_fw_state` on fatal protocol errors, and reads output registers. Table updates copy through the shared driver table buffer, flush or invalidate HDP as direction requires, then issue the firmware transfer message. Metrics reads cache table data for roughly one millisecond unless bypassed. Persistent state includes cached firmware versions, feature bits in firmware, SMU table buffers, metrics cache timestamp, custom pstate fields, and firmware hang/runtime state.

## Dependencies And Integration Points

The file depends on AMDGPU MMIO helpers, `amdgpu_smu.h`, `soc15_common.h`, RAS FED status, reset/halt handling, PCI probing, sysfs emit helpers, and ASIC-specific maps installed in `smu_context`. It is used by PPT implementations, sysfs power controls, metrics export, SMC table programming, display/audio power logic, and RAS-priority command paths.

## Risks And Test Signals

Risks include mailbox deadlock from incorrect lock-held usage, response timeout misclassification, command filtering hiding VF failures, feature-map mismatches, cache coherency bugs around table copies, and unsafe command attempts during RAS fatal error. Test signals include SMU message success/failure injection, async wait behavior, VF command filtering, RAS FED priority behavior, table round trips, metrics cache refresh, suspend/resume, firmware hang detection, and DPM/PCIe sysfs formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.h

## Purpose

`smu_cmn.h` declares the shared SWSMU helper API implemented in `smu_cmn.c` and defines metrics initialization/macrogen helpers used by SMU code layers. It also publishes SMU interrupt context IDs, PWM mode constants, PCIe speed helpers, and the v1 message-ops instance.

## Important APIs, Types, And Functions

Important declarations cover SMC message send/wait, debug message send, mapping translation, feature support/enabled queries, feature masks, table transfer, VRAM copy, metrics table reads, PPT/table writes, MP1 state programming, audio-function detection, policy description, backend workload-mask conversion, DPM/PCIe level printing, custom-level reset, PCIe generation/width indexes, and firmware version checks. Macros such as `smu_cmn_init_soft_gpu_metrics`, `smu_cmn_init_partition_metrics`, `smu_cmn_init_baseboard_temp_metrics`, and `smu_cmn_init_gpuboard_temp_metrics` initialize exported metric structures with headers and default `0xff` contents.

## Control Flow, State, And Persistence

The header itself has no runtime control flow except the inline `pcie_gen_to_speed()` lookup. Its macros impose initialization behavior on metrics objects by typechecking the expected revisioned structure, clearing to `0xff`, and filling header metadata. Persisted state is owned by callers: SMU contexts, firmware tables, feature masks, and exported metrics buffers.

## Dependencies And Integration Points

It includes `amdgpu_smu.h` and is gated for SWSMU code layers L2 through L4. It integrates with PPT implementations, sysfs power/feature controls, GPU metrics export, firmware table transfer, fan/PWM handling, SMU interrupt handling, and common SMU message transport.

## Risks And Test Signals

Risks include declaration/implementation drift, incorrect code-layer guards, metric revision mismatch, and PCIe helper indexing outside the `link_speed` table if callers pass invalid generations. Test signals are allmodconfig or AMDGPU builds, sparse/typecheck coverage for metrics macros, sysfs feature mask read/write, metrics initialization revision checks, and DPM/PCIe output tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_internal.h

## Purpose

`smu_internal.h` defines layer-L1 convenience wrappers around `smu->ppt_funcs`. It lets higher-level SMU code call ASIC-specific hooks through consistent macro names while providing default returns when a hook or function table is absent.

## Important APIs, Types, And Functions

The core macro is `smu_ppt_funcs(intf, ret, smu, args...)`, which returns `-EINVAL` if `ppt_funcs` is missing, calls the hook if present, or returns the supplied default. Wrappers cover microcode/table/power initialization, PPT setup/write, feature masks, GFXOFF, SMC sensors, display config, BTC, watermarks, thermal alerts, performance levels, PCIe parameters, power source, I2C, IDs, thermal throttling logs, fan/config table hooks, WBRF hooks, UCLK shadowing, and RAS SMU-driver extraction.

## Control Flow, State, And Persistence

The macros are call-through dispatch only. They do not store state, but they gate access to persistent SMU/firmware and driver state owned by the invoked PPT implementation. Default return values are part of the behavior: some missing hooks are benign `0`, while unsupported data paths return `-EINVAL`, `-EOPNOTSUPP`, or `false`.

## Dependencies And Integration Points

It includes `amdgpu_smu.h` and is compiled only for `SWSMU_CODE_LAYER_L1`. It integrates with all ASIC PPT implementations through `struct pptable_funcs`, and with SMU initialization, display, power, thermal, feature, metrics, and RAS plumbing.

## Risks And Test Signals

Risks are silent success defaults masking absent required hooks, wrong default error codes changing caller fallback, and macro type errors being harder to inspect than functions. Test signals include build coverage across ASIC PPTs, probe paths on ASICs with partial hook tables, feature/sysfs operations for missing hooks, and runtime checks that required hooks are installed before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/Makefile

## Purpose

This Makefile is the top-level AMDGPU RAS build aggregator. It selects the RAS manager directory, adds include paths for `rascore` and the manager, and includes the subordinate Makefiles that append object files into `AMD_GPU_RAS_FILES`.

## Important APIs, Types, And Functions

The relevant variables are `AMD_GPU_RAS_MGR`, defaulting to `ras_mgr`; `RAS_LIBS`, containing the manager and `rascore`; and `AMD_RAS`, a list of included Makefiles resolved under `AMD_GPU_RAS_FULL_PATH`. It also appends include paths through `subdir-ccflags-y`.

## Control Flow, State, And Persistence

Build-time control flow is simple: if no manager override is supplied, use `ras_mgr`; compute two library Makefile paths; include them. It persists no runtime state, but it determines which RAS implementation objects enter the AMDGPU module.

## Dependencies And Integration Points

It depends on outer AMDGPU Kbuild variables `AMD_GPU_RAS_FULL_PATH` and `AMD_GPU_RAS_PATH`. It integrates with `ras_mgr/Makefile`, `rascore/Makefile`, and the parent driver Makefile that consumes `AMD_GPU_RAS_FILES`.

## Risks And Test Signals

Risks are incorrect path variables, missing include paths for cross-directory headers, and future manager overrides not matching the object layout. Test signals include kernel builds with RAS enabled, clean builds after directory renames, and object list inspection to confirm both manager and core RAS objects are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/Makefile

## Purpose

`ras_mgr/Makefile` lists the AMDGPU-facing unified RAS manager objects and appends them to the global `AMD_GPU_RAS_FILES` build list.

## Important APIs, Types, And Functions

The object list includes `amdgpu_ras_sys.o`, `amdgpu_ras_mgr.o`, `amdgpu_ras_eeprom_i2c.o`, `amdgpu_ras_mp1_v13_0.o`, `amdgpu_ras_cmd.o`, `amdgpu_virt_ras_cmd.o`, `amdgpu_ras_process.o`, and `amdgpu_ras_nbio_v7_9.o`. `RAS_MGR` prefixes those names with `$(AMD_GPU_RAS_PATH)/ras_mgr/`.

## Control Flow, State, And Persistence

There is no runtime behavior. Build state is accumulated by appending `RAS_MGR` into `AMD_GPU_RAS_FILES`, which makes the manager, virtualization bridge, system callback table, EEPROM adapter, MP1/NBIO adapters, command handlers, and event processing compile into AMDGPU.

## Dependencies And Integration Points

It depends on the top-level RAS Makefile and parent AMDGPU Kbuild variables. It integrates with `rascore` headers and objects, the AMDGPU IP block list, SR-IOV support, SMU/MP1 firmware messaging, NBIO interrupt registration, and EEPROM I2C support through the objects it selects.

## Risks And Test Signals

Risks are omitting a required object after adding a header or exported function, stale object names after file moves, and manager/core object order assumptions. Test signals include full AMDGPU build, modpost unresolved-symbol checks, and link coverage for VF and non-VF RAS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.c

## Purpose

`amdgpu_ras_cmd.c` implements AMDGPU-specific RAS command handling on top of the generic `rascore` command dispatcher. It validates and prepares error injection, reports safe framebuffer ranges, translates framebuffer addresses, routes VF commands to the virtualization path, and waits for reset-safe command execution.

## Important APIs, Types, And Functions

Public functions are `amdgpu_ras_handle_cmd()` and `amdgpu_ras_submit_cmd()`. Static handlers are `amdgpu_ras_inject_error`, `amdgpu_ras_get_ras_safe_fb_addr_ranges`, and `amdgpu_ras_translate_fb_address`, mapped in `amdgpu_ras_cmd_maps`. Helper flow includes XGMI-specific power policy preparation/restoration, local-to-global XGMI address conversion, and bank/SOC physical address translation through rascore UMC helpers.

## Control Flow, State, And Persistence

Submission initializes `cmd_res` and `output_size`, sends VF commands to `amdgpu_virt_ras_handle_cmd`, rejects disabled rascore access, waits up to 60 seconds while the GPU is in reset, tries AMDGPU-local handlers, falls back to `rascore_handle_cmd`, records `cmd_res`, and validates output size. UMC injection rejects already retired addresses, out-of-VRAM or above-52-bit addresses, converts multi-node XGMI addresses, temporarily disables XGMI power-down for XGMI injections, and restores policy unless an interrupt was triggered.

## Dependencies And Integration Points

The file depends on AMDGPU RAS manager state, XGMI topology, DPM policy APIs, SR-IOV virtualization command handling, rascore command structs, and UMC translation routines. It is the manager-side command bridge used by ioctl or internal callers through `amdgpu_ras_mgr_handle_ras_cmd`.

## Risks And Test Signals

Risks include accepting malformed `input_size`, failing to restore XGMI/DF policies, racing reset state, copying output only on exact size match in callers, and address translation mistakes on multi-node systems. Test signals include injection command tests for UMC/GFX/XGMI, invalid address rejection, retired-address rejection, reset-wait timeout, VF command routing, safe range output for memory partitions, and SOC-to-bank translation round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.h

## Purpose

`amdgpu_ras_cmd.h` declares the AMDGPU-specific extension command namespace and request/response structures for translating a memory file descriptor into a GPU memory range.

## Important APIs, Types, And Functions

It defines `enum amdgpu_ras_cmd_id` from `RAS_CMD_ID_AMDGPU_START`, currently including `RAS_CMD__TRANSLATE_MEMORY_FD`, and structures `ras_cmd_translate_memory_fd_req` and `ras_cmd_translate_memory_fd_rsp`. Public functions are `amdgpu_ras_handle_cmd()` and `amdgpu_ras_submit_cmd()`.

## Control Flow, State, And Persistence

The header has no runtime control flow. Its packed command structures are ABI-like data exchanged through `ras_cmd_ctx`; command execution state is stored in that context and in rascore/manager state.

## Dependencies And Integration Points

It includes `ras.h` and depends on the generic command ID ranges, device handles, and command context from `ras_cmd.h`. It integrates with manager command submission, VF forwarding, and possible userspace or firmware-facing RAS command interfaces.

## Risks And Test Signals

Risks are command ID collisions, request/response layout drift, and ABI alignment changes. Test signals include compile coverage, command size validation, userspace ABI tests for any memory-fd translation implementation, and unknown-command fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.c

## Purpose

`amdgpu_ras_eeprom_i2c.c` adapts rascore EEPROM persistence to AMDGPU I2C EEPROM hardware. It discovers the RAS table address from VBIOS or MP1 IP defaults and implements paged I2C transfers for RAS bad-page EEPROM records.

## Important APIs, Types, And Functions

The exported object is `amdgpu_ras_eeprom_i2c_sys_func`, with `.eeprom_i2c_xfer = ras_eeprom_i2c_xfer` and `.update_eeprom_i2c_config = ras_eeprom_i2c_config`. Constants describe EEPROM memory address regions `0x0` and `0x40000`, 19-bit address to 7-bit I2C address conversion, 256-byte page size, and two-byte EEPROM offsets.

## Control Flow, State, And Persistence

Configuration first asks atom firmware for a RAS ROM address, normalizes the wire-format address into a 19-bit memory address, or falls back to `0x40000` for selected MP1 13.0.x ASICs. Transfer code loops over the requested range, computes the I2C device address and two-byte offset, limits writes so they do not cross a page boundary, allows reads up to `U16_MAX`, issues a two-message `i2c_transfer`, and sleeps 10 ms after writes for EEPROM internal programming. Persistence is the EEPROM-backed RAS table.

## Dependencies And Integration Points

It depends on AMDGPU atom firmware helpers, `ras_eeprom` control, the configured I2C adapter from the RAS manager, Linux I2C APIs, and MP1 IP version detection. It is plugged into `ras_eeprom_config` by `amdgpu_ras_mgr_init_eeprom_config`.

## Risks And Test Signals

Risks include wrong EEPROM base address, I2C adapter quirks not honored beyond max lengths stored elsewhere, partial transfer accounting, page-boundary write errors, and fixed sleep latency. Test signals include VBIOS-address and fallback-address platforms, EEPROM read/write/reset table tests, bad-page persistence across reboot, I2C fault injection, and page-boundary transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.h

## Purpose

`amdgpu_ras_eeprom_i2c.h` exposes the AMDGPU I2C EEPROM system-function table to the RAS manager.

## Important APIs, Types, And Functions

The only public symbol is `extern const struct ras_eeprom_sys_func amdgpu_ras_eeprom_i2c_sys_func;`, which provides EEPROM transfer and configuration callbacks.

## Control Flow, State, And Persistence

The header has no runtime control flow or storage. Persistence is supplied by the implementation through the physical EEPROM table.

## Dependencies And Integration Points

It includes `ras.h` for `struct ras_eeprom_sys_func` and is consumed by `amdgpu_ras_mgr.c` when populating `ras_core_config.eeprom_cfg`.

## Risks And Test Signals

Risks are declaration/definition drift and missing object selection in `ras_mgr/Makefile`. Test signals are build/link coverage and successful EEPROM callback installation during RAS manager creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.c

## Purpose

`amdgpu_ras_mgr.c` is the AMDGPU unified RAS manager IP block. It creates and configures `ras_core_context`, wires AMDGPU system callbacks into rascore, initializes software/hardware RAS services, handles interrupts, manages event sequence numbers, dispatches RAS commands, and coordinates reset-time pause/resume behavior.

## Important APIs, Types, And Functions

It exports `ras_v1_0_ip_block`, `amdgpu_ras_mgr_get_context`, `amdgpu_enable_uniras`, `amdgpu_uniras_enabled`, interrupt handlers, ECC update, GPU reset, event sequence generation, EEPROM safety checks, NPS query, retired-address checks, RMA status, command handling, pre/post reset hooks, and bad-page row lookup. Internal configuration helpers install ACA topology, EEPROM I2C, MP1 v13.0, NBIO v7.9, PSP, and UMC config.

## Control Flow, State, And Persistence

Software init disables unified RAS by default, enables it for selected MP0 IP or debug ACA mode, allocates `amdgpu_ras_mgr`, creates rascore with IP versions and callbacks, initializes RAS processing, rascore software state, event manager, and VF virtualization state. Hardware init delegates to VF remote RAS or rascore, marks `ras_is_ready`, and enables unified RAS. Interrupt flow gates on readiness, generates DE/poison-consumption/fatal sequence numbers, and enqueues event work through `amdgpu_ras_process`. Persistent state includes manager readiness, event counters per hive or device, bad-page thresholds, rascore submodules, VF command state, and reset flags.

## Dependencies And Integration Points

The manager depends on AMDGPU reset, XGMI hives, PSP RAS TA context, EEPROM I2C, MP1/NBIO adapters, rascore modules, SR-IOV, UMC bad-page handling, SMU/DPM bad-page threshold controls, and the AMDGPU IP block lifecycle.

## Risks And Test Signals

Risks include enabling on unsupported IP versions, not unwinding all allocations on partial init failure, incorrect hive event-manager ownership, readiness gating differences between VF and PF, bad-page threshold misconfiguration, and command buffer size assumptions. Test signals include probe/remove, VF/PF init, MP1/NBIO unsupported-version handling, interrupt dispatch for UMC and non-UMC blocks, reset pre/post hooks, command submission, EEPROM safety watermark behavior, and XGMI multi-node sequence numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.h

## Purpose

`amdgpu_ras_mgr.h` declares the AMDGPU unified RAS manager interface, interrupt metadata, manager state, and IP block descriptor.

## Important APIs, Types, And Functions

`enum ras_ih_type` classifies none, block-controller, consumer-client, and fatal-error interrupt sources. `struct ras_ih_info` carries a block ID plus either an AMDGPU IV entry or PASID/reset callback payload. `struct amdgpu_ras_mgr` stores `adev`, `ras_core`, delayed bad-page work, event manager, VF command state, last poison-consumption sequence number, readiness, pause state, and completion. The header declares manager lifecycle/query, interrupt dispatch, ECC update, reset, command, NPS, retired-address, RMA, and reset hook functions.

## Control Flow, State, And Persistence

The header has no runtime flow, but it defines the manager state machine: `ras_is_ready` gates public operations; `is_paused` and `ras_event_done` coordinate reset with event processing; delayed work periodically retires bad pages; sequence tracking prevents duplicate poison-consumption handling.

## Dependencies And Integration Points

It includes `ras.h` and `amdgpu_ras_process.h`, and is used by RAS manager implementation, NBIO/MP1 adapters, command handlers, sys callbacks, virtualization command code, and interrupt producers.

## Risks And Test Signals

Risks include union misuse in `ras_ih_info`, stale readiness checks, and incorrect lifetime of `virt_ras_cmd` or delayed work. Test signals include compile coverage, interrupt payload tests, reset pause/resume tests, VF/PF path tests, and manager context null checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.c

## Purpose

`amdgpu_ras_mp1_v13_0.c` adapts rascore MP1 operations to AMDGPU SMU firmware messages for MP1 v13.0-era ASICs. It queries valid MCA bank counts, dumps bank registers, sends firmware EEPROM commands, and reports firmware RAS EEPROM feature enablement.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_mp1_sys_func_v13_0`. Static functions are `mp1_v13_0_get_valid_bank_count`, `mp1_v13_0_dump_valid_bank`, `mp1_v13_0_eeprom_send_msg`, and `mp1_v13_0_get_ras_enabled_mask`. `pmfw_eeprom_msgs` maps rascore EEPROM command enums to `SMU_MSG_*` opcodes.

## Control Flow, State, And Persistence

All hardware operations try to take `adev->reset_domain->sem` with `down_read_trylock`; failure returns `-RAS_CORE_GPU_IN_MODE1_RESET`. Bank count chooses CE or non-CE query messages. Bank dump computes doubleword offsets for each 64-bit ACA register and issues two SMU reads. EEPROM sends forward firmware EEPROM commands through `amdgpu_smu_ras_send_msg`. Feature query sets `RAS_CORE_FW_FEATURE_BIT__RAS_EEPROM` if `SMU_FEATURE_HROM_EN_BIT` is enabled.

## Dependencies And Integration Points

It depends on `amdgpu_smu.h`, reset-domain locking, SMU RAS message helpers, and rascore MP1 callbacks. It is installed by `amdgpu_ras_mgr_init_mp1_config` for MP1 IP versions 13.0.6, 13.0.12, and 13.0.14.

## Risks And Test Signals

Risks include message enum drift, invalid EEPROM command indexes, reset lock starvation, partial 64-bit register reads, and feature-mask false negatives during reset. Test signals include bank count/dump tests under normal and reset conditions, firmware EEPROM command coverage, HROM feature detection, and ACA update paths that consume dumped MCA registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.h

## Purpose

`amdgpu_ras_mp1_v13_0.h` declares the MP1 v13.0 AMDGPU RAS system-function table.

## Important APIs, Types, And Functions

The only public symbol is `extern const struct ras_mp1_sys_func amdgpu_ras_mp1_sys_func_v13_0;`.

## Control Flow, State, And Persistence

The header has no runtime behavior. It allows manager configuration to bind rascore MP1 operations to the v13.0 implementation.

## Dependencies And Integration Points

It includes `ras.h` for `struct ras_mp1_sys_func` and is consumed by `amdgpu_ras_mgr.c`.

## Risks And Test Signals

Risks are missing object linkage or version-selection drift in the manager. Test signals include build coverage and successful callback installation for supported MP1 versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_mp1_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c

## Purpose

`amdgpu_ras_nbio_v7_9.c` registers NBIO v7.9 RAS interrupt sources with AMDGPU IRQ handling. The process and set callbacks are intentionally dummy because the relevant BIF-ring interrupt path is disabled due to a known hardware issue.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_nbio_sys_func_v7_9`. It installs IRQ source functions for `ras_controller_irq` and `ras_err_event_athub_irq`, then registers IDs `NBIF_7_4__SRCID__RAS_CONTROLLER_INTERRUPT` and `NBIF_7_4__SRCID__ERREVENT_ATHUB_INTERRUPT` under `SOC15_IH_CLIENTID_BIF`.

## Control Flow, State, And Persistence

`nbio_v7_9_init_ras_controller_interrupt` and `nbio_v7_9_init_ras_err_event_athub_interrupt` assign the `amdgpu_irq_src_funcs`, set `num_types = 1`, and call `amdgpu_irq_add_id`. The actual `.set` and `.process` functions return success without programming hardware or dispatching events.

## Dependencies And Integration Points

It depends on AMDGPU IRQ registration, NBIO register/IRQ source headers, and rascore NBIO callback wiring. The manager selects this implementation for NBIO IP versions 7.9.0 and 7.9.1.

## Risks And Test Signals

Risks are dummy handlers hiding future hardware enablement, registering wrong client/source IDs, and assuming BIF-ring interrupts remain disabled. Test signals include IRQ registration during probe, no spurious processing, unsupported-version rejection, and platform validation when NBIO RAS interrupt routing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.h

## Purpose

`amdgpu_ras_nbio_v7_9.h` declares the NBIO v7.9 AMDGPU RAS system-function table.

## Important APIs, Types, And Functions

The public symbol is `extern const struct ras_nbio_sys_func amdgpu_ras_nbio_sys_func_v7_9;`.

## Control Flow, State, And Persistence

The header has no runtime behavior. It is a binding point for manager NBIO configuration.

## Dependencies And Integration Points

It relies on consumers already knowing `struct ras_nbio_sys_func` from `ras.h` and is included by `amdgpu_ras_mgr.c` and the NBIO implementation.

## Risks And Test Signals

Risks are type visibility assumptions and missing object linkage. Test signals include build coverage and correct manager callback selection for NBIO 7.9.x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.c

## Purpose

`amdgpu_ras_process.c` coordinates asynchronous RAS event processing around interrupts, bad-page retirement, poison consumption, and GPU reset pause/resume.

## Important APIs, Types, And Functions

Public functions initialize/finalize processing, handle UMC, unexpected, and consumption interrupts, bracket event processing with `amdgpu_ras_process_begin/end`, and run pre/post reset hooks. The delayed work function `ras_process_retire_page_dwork` periodically calls `ras_umc_handle_bad_pages`.

## Control Flow, State, And Persistence

Init clears `is_paused`, initializes a completion, and sets up delayed work. The work item skips RMA devices, delays if reset or recovery is active, otherwise retires bad pages and reschedules every 100 ms on success. UMC interrupts enqueue rascore processing as poison creation. Unexpected interrupts mark FED and request a mode1 GPU reset. Consumption interrupts either invoke VF poison handler or build a `ras_event_req`, obtain a poison-consumption seqno while filtering duplicate stale seqnos, and enqueue processing. Pre-reset pauses new processing, waits up to 1200 ms for current event completion, and flushes retirement work; post-reset resumes and schedules work.

## Dependencies And Integration Points

It depends on the RAS manager context, rascore process queue, UMC bad-page handling, AMDGPU reset/recovery state, SR-IOV poison hooks, and sequence-number FIFOs.

## Risks And Test Signals

Risks include delayed work running after teardown, completion timeout during reset, duplicate or stale poison sequence numbers, missed VF poison callbacks, and bad-page retirement rescheduling too aggressively. Test signals include interrupt enqueue tests, reset while RAS events are active, RMA skip behavior, delayed-work cancellation at fini, VF poison handling, and duplicate seqno handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.h

## Purpose

`amdgpu_ras_process.h` declares the AMDGPU RAS event-processing interface used by the manager and interrupt dispatch paths.

## Important APIs, Types, And Functions

It forward-declares `enum ras_ih_type` and declares init/fini, UMC/unexpected/consumption interrupt handlers, process begin/end callbacks, and pre/post reset hooks.

## Control Flow, State, And Persistence

The header has no control flow. Its functions operate on manager-owned delayed work, pause flags, completion state, and rascore event queues.

## Dependencies And Integration Points

It depends on `struct amdgpu_device` and is included by `amdgpu_ras_mgr.h` and implementation files that enqueue or pause RAS work.

## Risks And Test Signals

Risks are signature drift and callers using the process API before manager init. Test signals include build coverage and null/invalid manager context tests around reset and interrupt paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_sys.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_sys.c

## Purpose

`amdgpu_ras_sys.c` implements the AMDGPU `ras_sys_func` callback table consumed by rascore. It provides event notification, timestamps, sequence numbers, GPU status, device identity, reset locking, interrupt detection, and PSP/TA memory lookup.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_sys_fn`. Callback implementations include fatal event detection, poison-consumption notification, sequence number generation with XGMI hive sharing, event notifier dispatch, UTC timestamp, GPU status checks, device/system info, reset-domain lock control, RAS interrupt detection, and GPU memory block lookup for PSP ring/command/fence/firmware/RAS TA command memory.

## Control Flow, State, And Persistence

Event notification switches on rascore event IDs: bad pages schedule retirement work; poison consumption invokes PASID notification; reserve page calls AMDGPU page reservation; fatal errors call the global RAS ISR, generate UE seqno, and reset; update events notify DPM; RMA logs and reports reasons; reset events call manager reset; begin/end events bracket processing. Sequence generation uses the XGMI hive event manager when present, reuses fatal seqno during recovery, otherwise increments atomic sequence counters and event counts. Memory lookup maps logical rascore memory types to existing PSP BOs and validates addresses.

## Dependencies And Integration Points

It depends on AMDGPU RAS, reset, XGMI hive event state, DPM bad-page/RMA notifications, ras_log_ring, PSP memory fields, and manager process hooks. It is the rascore-to-driver boundary for side effects.

## Risks And Test Signals

Risks include null hive handling, event-notifier data type mismatches, fatal seqno reuse bugs, reset-lock imbalance, stale PSP memory pointers, and unimplemented put-memory semantics. Test signals include each notifier event, XGMI and non-XGMI sequence numbering, reset lock try/block paths, PSP memory validation, RMA logging, PASID callback invocation, and fatal interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.c

## Purpose

`amdgpu_virt_ras_cmd.c` implements VF-side remote unified RAS command support. It marshals `ras_cmd_ctx` commands through firmware-reserved shared VRAM, provides local wrappers for CPER and ECC queries, handles auto-updated block ECC buffers, and tracks remote unified RAS capability.

## Important APIs, Types, And Functions

Public functions initialize/finalize VF command state, run hardware init/fini, handle commands, pre/post reset, set/query remote unified RAS support, check retired-address validity, and convert retired addresses. Static helpers locate shared command memory, send remote ioctl commands, fetch batch trace overviews/records, generate CPER records from remote traces, register auto-update buffers, and serve block ECC status from shared memory.

## Control Flow, State, And Persistence

Remote command flow locks `remote_access_lock`, resolves the appropriate shared buffer, clears it, copies a command header, calls `amdgpu_virt_send_remote_ras_cmd` with GPA and length, then copies output back if sizes permit. CPER snapshot refreshes batch-trace overview; CPER record generation pulls remote batch records and writes generated CPER data to a userspace pointer. Block ECC status initializes an auto-update command in shared memory on first use, then reads cached per-block counts. HW init obtains RAS capability and binds the block ECC shared buffer; HW fini clears it; pre-reset disables auto-update state.

## Dependencies And Integration Points

It depends on SR-IOV firmware-reserved telemetry memory, AMDGPU virtualization remote command helpers, rascore command ABI, ras_log_ring and CPER generation, manager context, and memory reservation metadata. It is selected by `amdgpu_ras_submit_cmd` on VFs.

## Risks And Test Signals

Risks include incorrect CPU-to-GPA translation, shared buffer size/align errors, stale auto-update data after reset, user-copy failures, batch cache desynchronization, and command result confusion between transport `ret` and `cmd_res`. Test signals include VF remote command round trips, CPER snapshot/record reads, block ECC auto-update, reset pre/post behavior, invalid shared-memory reservation handling, address validity/retired conversion, and concurrent command serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.h

## Purpose

`amdgpu_virt_ras_cmd.h` declares VF-side remote unified RAS command state and operations.

## Important APIs, Types, And Functions

Types include `remote_batch_trace_mgr`, `amdgpu_virt_shared_mem`, `vram_blocks_ecc`, and `amdgpu_virt_ras_cmd`. They store cached batch trace state, shared-memory CPU/GPA/size triples, auto-updated block ECC state, remote support flag, and a remote access mutex. Public APIs cover SW/HW init/fini, command handling, reset hooks, remote support toggles, address validity, and retired-address conversion.

## Control Flow, State, And Persistence

The header defines the state used to serialize remote commands and cache remote RAS data across calls. Shared-memory data persists in reserved VRAM until reset, fini, or explicit clearing.

## Dependencies And Integration Points

It includes `ras.h` and depends on `struct amdgpu_device`, rascore command structures, log batch types, and SR-IOV telemetry layout from AMDGPU virtualization code.

## Risks And Test Signals

Risks include lifetime errors for `virt_ras_cmd`, mutex use before init, stale `remote_uniras_supported`, and shared-memory buffer misuse. Test signals include VF init/fini, reset clearing, concurrent remote command tests, and capability toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/ras_sys.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/ras_sys.h

## Purpose

`ras_sys.h` provides AMDGPU-facing logging, register access, instance mapping, and wait/radix helper macros for the RAS manager and rascore adapter layer.

## Important APIs, Types, And Functions

Logging macros `RAS_DEV_ERR/WARN/INFO/DBG` route through `dev_*` when a device is available or `printk` otherwise. `RAS_DEV_RREG32_SOC15` and `RAS_DEV_WREG32_SOC15` wrap SOC15 register access with AMDGPU offsets. `RAS_GET_INST` and `RAS_GET_MASK` translate logical instances/masks through `adev->ip_map` when available. Inline helpers wrap radix-tree deletion by iterator and `wait_event_interruptible_timeout`. The header declares `amdgpu_ras_sys_fn`.

## Control Flow, State, And Persistence

Macros branch on whether a device pointer or IP map callback exists. Register macros perform immediate MMIO reads/writes; wait helper blocks on the supplied waitqueue until the condition or timeout. Persistent state is hardware register state and driver logs, not header-owned memory.

## Dependencies And Integration Points

It includes Linux printk/device/mempool headers and `amdgpu.h`. It is included throughout manager and rascore code to avoid direct AMDGPU dependencies inside generic rascore where possible.

## Risks And Test Signals

Risks include unsafe casts of `void *dev` to `amdgpu_device`, wrong SOC15 offset construction, logging format mismatches, and condition callback misuse in wait helper. Test signals include build coverage, register access smoke tests on supported IPs, logical-to-physical instance mapping tests, and RAS log output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/ras_sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/Makefile

## Purpose

`rascore/Makefile` lists the generic RAS core object files and appends them to the AMDGPU RAS object list.

## Important APIs, Types, And Functions

`RAS_CORE_FILES` includes rascore modules for core lifecycle, MP1, ACA, EEPROM, UMC, command handling, GFX, process queue, NBIO, log ring, CPER, PSP, and firmware EEPROM support. `RAS_CORE` prefixes the files with `$(AMD_GPU_RAS_PATH)/rascore/`, then appends to `AMD_GPU_RAS_FILES`.

## Control Flow, State, And Persistence

There is no runtime behavior. The Makefile controls whether the generic rascore implementation is linked into AMDGPU.

## Dependencies And Integration Points

It depends on outer Kbuild variables and is included by the top-level RAS Makefile. Its object set backs the manager's `ras_core_context` lifecycle and command/ACA/UMC/EEPROM/PSP features.

## Risks And Test Signals

Risks are missing objects for declared APIs, stale file names, and accidental omission of paired versioned modules. Test signals include full build, modpost unresolved symbol checks, and feature-specific link coverage for ACA, CPER, firmware EEPROM, and UMC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras.h

## Purpose

`ras.h` is the central rascore public header. It defines RAS block/error/event/status enums, system callback interfaces, configuration structures, `ras_core_context`, and the exported rascore lifecycle and service APIs.

## Important APIs, Types, And Functions

Important enums include GPU health/status, firmware feature flags, RAS block IDs, ECC error types, sequence-number types/FIFOs, notify events, GPU status bits, and firmware EEPROM commands. Callback tables include `ras_mp1_sys_func`, `ras_eeprom_sys_func`, `ras_nbio_sys_func`, `ras_psp_sys_func`, and `ras_sys_func`. State/config types include `ras_ecc_count`, `ras_bank_ecc`, submodule configs, `ras_core_config`, and `ras_core_context`. Public APIs cover create/destroy, SW/HW init/fini, readiness, seqno generation/FIFO access, ECC update/query, GPU status helpers, IRQ/fatal handling, NPS, block names, timestamp conversion, status enablement, address translation, GPU memory, reset locks, event notifications, device info, and NPS page conversion.

## Control Flow, State, And Persistence

The header defines the rascore state machine. `ras_core_context` owns config, ACA, EEPROM and firmware EEPROM controls, PSP/UMC/NBIO/GFX/MP1/process/command/log-ring modules, system callbacks, poison support, RMA/initialized/enabled flags, sequence FIFOs with spinlock, and firmware feature bits. Persistent RAS data includes EEPROM bad pages, log-ring records, sequence state, bad-page retirement state, and submodule ECC counters.

## Dependencies And Integration Points

It includes rascore submodule headers and is used by manager code, command handlers, ACA parsers, EEPROM/UMC/PSP modules, and system adapter headers. It is the generic interface boundary between rascore and AMDGPU-specific plumbing.

## Risks And Test Signals

Risks include circular includes, ABI-like struct drift for command/log users, enum ID mismatches with TA firmware, race-prone seqno FIFOs, and callback tables not fully populated. Test signals include rascore lifecycle tests, all submodule init/fini ordering, command interface ABI validation, ECC query/update paths, reset lock correctness, and firmware EEPROM feature negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.c

## Purpose

`ras_aca.c` implements rascore Accelerator Check Architecture handling. It reads MCA/ACA banks through MP1 callbacks, matches banks to RAS blocks, parses ECC counts, logs raw register data, updates per-block counters, records bad UMC banks, and exposes ECC query/clear operations.

## Important APIs, Types, And Functions

Public APIs include `ras_aca_sw_init/fini`, `ras_aca_hw_init/fini`, `ras_aca_update_ecc`, `ras_aca_get_block_ecc_count`, `ras_aca_clear_block_new_ecc_count`, `ras_aca_clear_all_blocks_ecc_count`, `ras_aca_mark_fatal_flag`, and `ras_aca_clear_fatal_flag`. Key internals include bank dumping, block matching/parsing, duplicate UE filtering during fatal handling, sequence-number selection, log-ring insertion, bad-bank EEPROM/UMC recording, and per-socket/AID/XCD counter aggregation.

## Control Flow, State, And Persistence

`ras_aca_update_ecc` locks `bank_op_lock`, skips duplicate UE fatal reads, queries bank count, creates a log batch, dumps each bank register array, finds the matching block, parses counts, assigns a CE/UE/DE/poison seqno, logs raw ACA registers, updates counters under `aca_lock`, and records UMC deferred errors to firmware EEPROM or UMC bad-page caches. SW init validates topology bounds and initializes per-block socket/AID/XCD dimensions. HW init selects an IP function table by ACA IP version and binds block info. Persistent state includes per-block accumulated counts, new-count fields, fatal-read mark, log-ring events, EEPROM records, and pending bad-bank lists.

## Dependencies And Integration Points

It depends on rascore MP1 bank dump/count callbacks, `ras_aca_v1_0` block parsers, UMC bad-page logging, firmware EEPROM, log ring, sequence-number APIs, and rascore config topology. It feeds command queries and event processing.

## Risks And Test Signals

Risks include null `aca_blk` use if no block matches, topology bounds errors, duplicate fatal handling hiding real UE data, wrong count aggregation for GFX XCDs, failure to destroy batch tags on errors, and bad-page logging differences between reset and runtime. Test signals include CE/UE/DE bank dump tests, unmatched bank behavior, GFX per-XCD aggregation, fatal duplicate UE tests, UMC deferred bad-page persistence, clear-new and clear-all commands, and unsupported ACA IP handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.h

## Purpose

`ras_aca.h` defines generic ACA data structures, topology limits, register indices, ECC counters, block metadata, and the public ACA API.

## Important APIs, Types, And Functions

It defines socket/AID/XCD/block maximums, ACA error masks, `enum ras_aca_reg_idx`, bank register storage, hardware IP IDs, decoded bank info, per-bank/per-count/per-XCD/per-AID/per-socket/per-block ECC state, bank hardware ops, block info, block handle, IP function table, and `struct ras_aca`. Public functions cover SW/HW init/fini, ECC count query/clear, ECC update, and fatal flag mark/clear.

## Control Flow, State, And Persistence

The header has no implementation flow. It defines how ACA state persists inside `ras_core_context`: counters are split into new and total CE/UE/DE counts, GFX can store per-XCD counts, and locks protect counter and bank operations.

## Dependencies And Integration Points

It includes `ras.h` and is consumed by ACA core, ACA v1.0 parsers, command handlers, and manager rascore config. Hardware-specific files populate `aca_block_info` and `ras_aca_ip_func`.

## Risks And Test Signals

Risks include fixed maximums not matching future topology, block IDs used as array indexes, signed `UNKNOWN = -1` handling, and parser callbacks not filling all required bank info. Test signals include topology validation, block-info binding, counter aggregation, and static analysis for array bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.c

## Purpose

`ras_aca_v1_0.c` implements ACA v1.0 bank matching and parsing for UMC, GFX, SDMA, MMHUB, and XGMI RAS blocks. It decodes MCA IPID/status/syndrome fields into block identity and CE/UE/DE counts.

## Important APIs, Types, And Functions

The exported object is `ras_aca_func_v1_0`. Important helpers decode bank info, match hardware IP/mcatype, match GFX XCD banks, match SDMA/MMHUB banks by SMU syndrome error codes, classify UMC deferred/uncorrectable/correctable conditions, and parse default, UMC, and XGMI banks. Static `aca_block_info` entries define names, ras block IDs, hardware IPs, supported masks, and parser callbacks.

## Control Flow, State, And Persistence

Bank matching compares `IPID` hardware ID and MCA type against the v1.0 table, with additional instance/syndrome filters for GFX, SDMA, and MMHUB. Parsing decodes socket and die IDs from IPID instance fields, derives XCD ID for GFX/SMU banks, copies status/IPID/address into `aca_bank_ecc`, and sets one or more CE/UE/DE counts based on status flags and MISC0 error count. UMC poison/deferred errors are separated from UE/CE when poison mode is supported.

## Dependencies And Integration Points

It depends on bitfield macros from `ras_aca_v1_0.h`, rascore poison mode, block IDs from `ras.h`, and the generic ACA engine in `ras_aca.c`. It is selected by ACA IP version 1.0.0.

## Risks And Test Signals

Risks include hard-coded SMU syndrome codes, incorrect unified die/socket decoding, special-case GFX XCD mapping, UMC status classification differences across firmware, and XGMI extended error-code filtering. Test signals include synthetic bank register decode tests, real CE/UE/DE injections for each block, multi-socket/AID/XCD validation, poison-mode UMC behavior, and unsupported or unknown HWIP rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.h

## Purpose

`ras_aca_v1_0.h` defines ACA v1.0 register bitfield extractors, status/IPID/MISC/SYND access macros, known external error codes, SMN MCA base constants, and the exported v1.0 ACA IP function table.

## Important APIs, Types, And Functions

Macros extract status validity, overflow, UC/CE/UE/deferred/poison/scrub, address LSB, error code/ext code, IPID MCA type/hardware ID/instance IDs, MISC0 valid/overflow/error count, and syndrome error information. It declares `extern const struct ras_aca_ip_func ras_aca_func_v1_0`.

## Control Flow, State, And Persistence

The header has no runtime flow. Its macros define how persistent hardware MCA register snapshots are decoded by `ras_aca_v1_0.c`.

## Dependencies And Integration Points

It includes `ras.h` for types and bit helpers and is consumed by ACA v1.0 parser and generic ACA code. The SMN constants are used to identify SMU MCA instances for GFX, SDMA, and MMHUB matching.

## Risks And Test Signals

Risks include wrong bit ranges, generation-specific constants being reused on incompatible hardware, and count/status macros not matching firmware documentation. Test signals include register decode unit tests, generated-register diffs, and validation against injected ACA bank dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_aca_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.c

## Purpose

`ras_cmd.c` implements the generic rascore command dispatcher and handlers for ECC status, bad pages, counter reset, CPER and batch trace retrieval, PSP error injection, interface info, address translation, and device handle management.

## Important APIs, Types, And Functions

Public APIs are `ras_cmd_init/fini`, `rascore_handle_cmd`, `ras_cmd_query_interface_info`, `ras_cmd_translate_soc_pa_to_bank`, `ras_cmd_translate_bank_to_soc_pa`, and `ras_cmd_get_dev_handle`. Static handlers include block ECC status, grouped bad-page reads, clear bad-page info, reset all error counts, CPER snapshot/records, batch trace snapshot/records, and TA-backed error injection. `ras_cmd_maps` maps command IDs to handlers.

## Control Flow, State, And Persistence

Init creates a per-device command handle by XORing the rascore pointer with a magic value. Dispatch linearly searches the command map and returns unknown-command when absent. ECC status queries ACA totals. Bad pages are grouped in pages of 32 records from UMC/EEPROM caches. Clearing bad pages resets firmware or I2C EEPROM then UMC cached data. Counter reset clears ACA and logged UMC ECC. CPER and trace reads snapshot log-ring batches, gather trace records, generate CPER into temporary buffers, and copy to userspace pointers. Injection converts generic block/error IDs to TA IDs and calls PSP RAS TA. Address translation delegates to UMC translation.

## Dependencies And Integration Points

It depends on ACA, UMC, EEPROM/firmware EEPROM, log ring, CPER generation, PSP RAS TA, userspace copy helpers, and command ABI definitions in `ras_cmd.h`. Manager code may wrap or fall back to these handlers.

## Risks And Test Signals

Risks include user pointer copy failures, output buffer overrun if callers ignore `output_size`, command input-size mismatches, stale dev handles, bad-page grouping edge cases, CPER generation partial-buffer behavior, and TA enum drift. Test signals include each command ID, invalid input size/data cases, grouped bad-page pagination, CPER buffer-too-small paths, batch trace max-count limits, injection success/failure, and bank/SOC address round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.h

## Purpose

`ras_cmd.h` defines the generic RAS command ABI used inside rascore, AMDGPU manager wrappers, VF remote forwarding, and user-visible command buffers. It enumerates command IDs, response codes, address types, and packed request/response payloads.

## Important APIs, Types, And Functions

Important constants are command version 6.0 in the implementation, max input size 256, max GPUs 32, max bad pages per group 32, max safe ranges 64, max trace/batch counts 300, and max retired address count 32. `struct ras_cmd_ctx` is the central packed command envelope with version, command, result, input/output sizes, fixed input buffer, and flexible output buffer. Payloads cover device handles, block ECC, injection, devices info, bad pages, interface info, safe framebuffer ranges, framebuffer address translation, link topology, CPER snapshot/records, batch traces, auto-update, address validity, retired address conversion, and all-block ECC.

## Control Flow, State, And Persistence

The header has no implementation flow, but its structs govern command marshalling and persistence in shared command buffers. `ras_cmd_mgr` stores the device handle and rascore context. Request/response structures are `#pragma pack(push, 8)`, making layout stability important for cross-component communication.

## Dependencies And Integration Points

It includes `ras.h`, `ras_eeprom.h`, `ras_log_ring.h`, and `ras_cper.h`. It is consumed by rascore handlers, AMDGPU-specific command wrappers, VF remote command code, CPER/log-ring code, and potential ioctl layers.

## Risks And Test Signals

Risks include ABI layout drift, spelling-stable response constants such as `ERROR_UKNOWN_CMD`, unchecked flexible-array sizes, command ID range collisions, and struct packing differences. Test signals include compile-time size checks, command fuzzing for input/output sizes, VF shared-buffer compatibility, CPER and batch trace ABI tests, and cross-version interface query validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.h -->
