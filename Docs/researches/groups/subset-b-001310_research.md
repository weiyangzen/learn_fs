# subset-b-001310 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h

## Purpose
`ObjectID.h` is the legacy AMD display BIOS object-id contract used by the non-DC amdgpu display stack. It defines the bit layout and numeric constants for graphics object types, encoder object ids, connector object ids, router ids, generic objects, enumeration ids, full packed object identifiers, and object capability/table ids.

The file has no executable logic. Its purpose is ABI-style coordination with ATOM BIOS object tables and display code that decodes connector and encoder topology. The constants are consumed by connector, encoder, DisplayPort, CRTC, and DCE paths to identify things such as internal UNIPHY encoders, DACs, HDMI and DP bridge chips, LVDS/eDP panels, MXM routes, and hotplug/I2C capability records.

## Important APIs, types, and functions
- Graph object type macros define the high nibble of the packed id: `GRAPH_OBJECT_TYPE_GPU`, `ENCODER`, `CONNECTOR`, `ROUTER`, `DISPLAY_PATH`, and `GENERIC`.
- Object id macros define low-byte ids for encoder classes including internal LVDS/TMDS/DAC/DVO/UNIPHY variants, external SDVO/TMDS/HDMI/DP bridges, and legacy bridge chips such as `TRAVIS`, `NUTMEG`, `ALMOND`, and `ANX9805`.
- Connector object ids describe physical connector classes: DVI-I/DVI-D single and dual link, VGA, composite, S-video, YPbPr, HDMI type A/B, LVDS, DisplayPort, eDP, MXM, LVDS/eDP, and USB-C.
- `OBJECT_ID_MASK`, `ENUM_ID_MASK`, `OBJECT_TYPE_MASK`, and their shifts define the packed 16-bit object format used in BIOS tables.
- `CONSTRUCTOBJECTFAMILYID()` builds a family id from a graph object type and object id.
- The numerous `ENCODER_*_ENUM_ID*`, `CONNECTOR_*_ENUM_ID*`, `ROUTER_*`, and `GENERICOBJECT_*` macros precompose graph type, enum number, and object id into BIOS-compatible 16-bit identifiers.
- Capability macros such as `GRAPHICS_OBJECT_CAP_I2C`, `GRAPHICS_OBJECT_CAP_TABLE_ID`, and table ids for I2C command, hotplug detection interrupt, and encoder output protection label object records.

## Control flow
There is no runtime control flow. The only compile-time flow is an include guard and optional `_X86_` `#pragma pack(1)` / `#pragma pack()` pair around the definitions. Display code includes this header and compares or extracts id fields from values read out of BIOS object tables.

The important data path is external: BIOS table parser reads an object id, code masks it with `OBJECT_ID_MASK` and shifts with `OBJECT_ID_SHIFT` to get a raw encoder/connector id, then DCE and connector code switch on constants such as `ENCODER_OBJECT_ID_INTERNAL_UNIPHY*`, `ENCODER_OBJECT_ID_INTERNAL_KLDSCP_DAC*`, `CONNECTOR_OBJECT_ID_DISPLAYPORT`, or `CONNECTOR_OBJECT_ID_eDP`.

## State and persistence behavior
The header defines stable constants only. No kernel memory is allocated, no state is mutated, and no values are persisted by this file. The persistence requirement is external: the numeric values must remain stable because they match firmware table encodings and are baked into BIOS data.

## Dependencies and integration points
The file is integrated through amdgpu display components that include `ObjectID.h` directly or indirectly. Search hits show use in `amdgpu_connectors.c`, `amdgpu_encoders.c`, `atombios_dp.c`, `atombios_crtc.c`, and DCE generation files such as `dce_v8_0.c` and `dce_v10_0.c`.

It also overlaps conceptually with `drivers/gpu/drm/amd/display/include/grph_object_id.h`, which serves newer DC display code. Any change must respect both the ATOM BIOS object layout and legacy display paths still using this header.

## Risks and edge cases
The primary risk is ABI drift. Renumbering or deleting constants would make BIOS object parsing choose the wrong connector or encoder path. The duplicate value for `ENCODER_OBJECT_ID_ALMOND` and `ENCODER_OBJECT_ID_NUTMEG` is intentional legacy baggage and should not be "cleaned up" without checking all BIOS consumers.

Packed id construction is also easy to misuse: object id, enum id, and graph type occupy different bit fields, so callers must not compare a raw low-byte `*_OBJECT_ID_*` value with a full `*_ENUM_ID*` value. Comments mention deleted entries, obsolete Radeon/Kaleidoscope classes, and old external encoders; preserving gaps is safer than compacting them.

## Test signals
Useful signals are display bring-up on legacy DCE ASICs, correct connector type mapping in `xrandr`/DRM connector properties, HPD handling for DP/eDP/HDMI, and successful encoder routing on systems with ATOM BIOS object tables. Compile-time signals include all legacy display files building after including this header and no switch fall-through to unknown connector/encoder ids in DCE and ATOM BIOS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ObjectID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c

## Purpose
`aldebaran.c` implements Aldebaran-specific reset-control plumbing, centered on MODE2 reset. It registers reset handlers for Aldebaran devices, selects the reset method, suspends and restores the right IP blocks, launches resets across XGMI-connected devices, reloads firmware after reset, resumes RAS and topology state, and exposes init/fini entry points for `adev->reset_cntl`.

The file is targeted at ASIC reset recovery rather than normal device initialization. It has special handling for MP1 13.0.2 devices connected to the CPU through XGMI, multi-AID systems, and XGMI hives where multiple physical nodes should reset in parallel.

## Important APIs, types, and functions
- `aldebaran_reset_init()` allocates and attaches `struct amdgpu_reset_control`, sets `async_reset`, `get_reset_handler`, initializes reset work, and installs `aldebaran_rst_handlers`.
- `aldebaran_reset_fini()` frees the reset control.
- `aldebaran_get_reset_handler()` selects the active reset method. If no method is specified, it chooses MODE2 for the CPU-connected MP1 13.0.2 case, otherwise defers to `amdgpu_asic_reset_method()`.
- `aldebaran_mode2_handler` is the `struct amdgpu_reset_handler` for MODE2 and wires prepare, perform, restore, and direct reset callbacks.
- `aldebaran_mode2_suspend_ip()` ungates power/clock state and suspends GFX, SDMA, and sometimes IH IP blocks in reverse IP-block order.
- `aldebaran_mode2_perform_reset()` marks devices as actively MODE2 resetting, runs `amdgpu_dpm_mode2_reset()`, parallelizes multi-node XGMI reset through `system_dfl_wq`, waits for work completion, and clears active reset state.
- `aldebaran_mode2_restore_ip()` reinitializes COMMON/IH/GFXHUB, reloads selected GFX and SDMA microcode through PSP, resumes RLC, waits for SMU reset completion, resumes GFX/SDMA blocks, runs late init, and regates clocks/power.
- `aldebaran_mode2_restore_hwcontext()` applies reset-recovery init level, clears RAS error state, calls restore IP, re-registers the GPU instance, reruns RAS late-init, resumes RAS, updates XGMI topology, resumes IRQ reset helpers, and runs IB ring tests.

## Control flow
Initialization installs a reset control with two handlers: Aldebaran MODE2 and XGMI reset-on-init. During recovery, the reset framework asks `get_reset_handler()` for a handler. The selector fills `reset_context->method` if it was `AMD_RESET_METHOD_NONE`, then scans the registered handlers.

For MODE2, prepare first suspends the affected HW context unless running as an SR-IOV VF. The suspend mask starts with GFX and SDMA, adds IH when `adev->aid_mask` indicates multi-AID, and drops SDMA from the suspend mask for multi-AID SDMA versions because those are handled differently.

The perform stage validates the reset-device list and hive requirements for MP1 13.0.2. It locks each device reset control, sets `active_reset`, and resets all devices in the reset list. Multi-node XGMI devices are reset asynchronously using their reset work, while single-node devices reset inline. The function then flushes queued work, reads each device's `asic_reset_res`, unlocks the reset controls, and clears `active_reset`.

The restore stage loops over every reset device. Each device is moved to `AMDGPU_INIT_LEVEL_RESET_RECOVERY`, restored through `aldebaran_mode2_restore_ip()`, then brought back into default state only after RAS resume, optional XGMI topology update, IRQ reset helper resume, and IB ring tests succeed.

## State and persistence behavior
The file mutates runtime reset state in `adev->reset_cntl`, `reset_context`, `adev->asic_reset_res`, reset work queues, per-device `reset_lock`, `active_reset`, IP block status flags, init level, RAS error state, topology state, and GPU instance registration. It also reloads firmware from `adev->firmware.ucode[]`, but it does not persist data across boots.

The reset path intentionally preserves device-level recovery ordering. It clears RAS errors after reset, reestablishes GART and firmware state, and marks late init completed for relevant blocks. Failed IB tests convert recovery to `-EAGAIN` and store the result in `tmp_adev->asic_reset_res`, signaling higher reset logic that another recovery attempt may be needed.

## Dependencies and integration points
The implementation depends on the amdgpu reset framework, DPM/SMU mode2 reset calls, PSP firmware loading, GFXHUB and RLC callbacks, IP-block suspend/resume/later-init helpers, RAS, IRQ reset helpers, IB ring tests, XGMI hive topology management, PCI bus mastering control, and Linux workqueues.

It integrates directly with `amdgpu_device_gpu_recover()` and reset domains through the `amdgpu_reset_control` object. It also relies on `amdgpu.h` macros for IP versions, clock/power gating, init levels, and GPU instance registration.

## Risks and edge cases
Reset concurrency is the highest risk. The code queues parallel reset work for XGMI devices, then flushes each work item and reads `asic_reset_res`; missed locking or stale `active_reset` could corrupt simultaneous reset decisions. Returning `-EALREADY` from `queue_work()` is treated as a reset failure, so duplicate work submission has visible recovery impact.

The firmware reload list is manually filtered to SDMA, MEC, RLC restore lists, and RLC G firmware. Missing a required ucode id or changing firmware ids without updating this list can produce post-reset hangs. The MP1 13.0.2 path requires a hive context, and returning `-EINVAL` prevents recovery with an incorrect reset context.

Multi-AID handling changes both the IP suspend mask and IH inclusion. Any new Aldebaran-like IP layout needs careful review of `aldebaran_get_ip_block_mask()`, SDMA skip logic, and restore ordering.

## Test signals
Strong signals are successful MODE2 reset recovery on Aldebaran, especially XGMI multi-node systems; successful PSP reload of GFX/SDMA/RLC firmware; `SMU_EVENT_RESET_COMPLETE` received; GFX and SDMA IP late init passing; RAS late init and resume passing; topology update success; and `amdgpu_ib_ring_tests()` passing after reset. Negative-path tests should cover missing reset lists, missing hive context for MP1 13.0.2, missing COMMON/IH blocks, and firmware reload failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h

## Purpose
`aldebaran.h` is the public local header for Aldebaran ASIC reset support. It exposes the reset-control lifecycle entry points implemented in `aldebaran.c` and imports `amdgpu.h` for the `struct amdgpu_device` declaration and related driver types.

## Important APIs, types, and functions
- `int aldebaran_reset_init(struct amdgpu_device *adev);` allocates and installs Aldebaran reset control state.
- `int aldebaran_reset_fini(struct amdgpu_device *adev);` tears down that reset control state.
- The include guard `__ALDEBARAN_H__` prevents duplicate inclusion.

## Control flow
There is no executable control flow in this header. Compile-time flow is limited to the include guard. Runtime control enters through callers that invoke `aldebaran_reset_init()` during device setup and `aldebaran_reset_fini()` during teardown.

## State and persistence behavior
The header itself stores no state. The declared functions mutate `adev->reset_cntl` and related reset-control runtime state in the implementation. No persistent state is defined here.

## Dependencies and integration points
The header depends on `amdgpu.h`, making it part of the main amdgpu internal API surface rather than a standalone forward-declaration header. It is included by `aldebaran.c` and by ASIC setup code that wires Aldebaran reset support into the broader driver.

## Risks and edge cases
The main risk is broad include coupling. Including `amdgpu.h` pulls in many subsystem headers, so this header should stay narrow and avoid adding unrelated declarations. Prototype mismatches with `aldebaran.c` would break reset setup at compile time.

## Test signals
Compile-time success and successful call sites for `aldebaran_reset_init()`/`aldebaran_reset_fini()` are the primary signals. Runtime validation is covered through Aldebaran reset tests described for `aldebaran.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran_reg_init.c

## Purpose
`aldebaran_reg_init.c` initializes SOC15 register base offset tables for Aldebaran. It maps each hardware IP type and instance to the generated base-address arrays from `aldebaran_ip_offset.h`, so generic register access macros can compute offsets for GC, HDP, MMHUB, ATHUB, NBIO, MP0/MP1, DF, OSSSYS, SDMA, SMUIO, THM, UMC, and VCN blocks.

## Important APIs, types, and functions
- `int aldebaran_reg_base_init(struct amdgpu_device *adev)` is the sole exported function in this file.
- It fills `adev->reg_offset[HWIP][instance]` for every `i < MAX_INSTANCE`.
- It depends on generated symbols such as `GC_BASE.instance[i]`, `HDP_BASE.instance[i]`, `MMHUB_BASE.instance[i]`, `SDMA0_BASE.instance[i]`, and `VCN_BASE.instance[i]`.

## Control flow
The function loops from instance zero to `MAX_INSTANCE - 1`. For each instance, it assigns a pointer to the generated per-instance base table for every supported hardware IP. It returns `0` unconditionally once the table is populated.

There is no validation or dynamic detection in this file. The comment notes that hardware has more IP blocks than the driver initializes here, and only blocks needed by the driver are wired.

## State and persistence behavior
The function mutates `adev->reg_offset`, a runtime lookup table used throughout amdgpu register-access paths. The values are pointers to static generated offset tables, not copied data. No persistent state is stored.

## Dependencies and integration points
The file includes `amdgpu.h`, `soc15.h`, `soc15_common.h`, and `aldebaran_ip_offset.h`. It integrates with SOC15 register helpers and macros such as `RREG32`, `WREG32`, and IP-specific offset calculations that depend on `adev->reg_offset`.

## Risks and edge cases
Incorrect pointer assignments cause broad register misaddressing. A wrong IP base can corrupt unrelated hardware state, while a missing IP base can break register access later in initialization. Because the loop assumes every generated `*_BASE.instance[i]` has at least `MAX_INSTANCE` entries, generated header changes must preserve that contract.

The function does not gate by actual hardware harvesting or present IP instances. Consumers must still avoid accessing non-existent IP blocks, and this routine should remain a base-table initializer rather than a presence detector.

## Test signals
Useful signals include successful Aldebaran boot, correct SOC15 register reads for each initialized HWIP, clean IP block initialization logs, no MMIO faults from computed register offsets, and functional GFX/SDMA/MMHUB/UMC/VCN paths. Regression tests should compare known register offsets against generated base tables for at least instance zero and multi-instance SDMA/UMC cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran_reg_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h

## Purpose
`amdgpu.h` is the central private header for the amdgpu kernel driver. It aggregates subsystem headers, declares global module parameters, defines central structures such as `struct amdgpu_device`, exposes ASIC callback contracts, declares core device/KMS/reset/ACPI APIs, and provides the register-access macros used by much of the driver.

Because almost every amdgpu subsystem includes or is included by this header, it acts as an internal integration contract for memory management, display, rings, firmware, interrupts, power management, virtualization, RAS/ACA/CPER, KFD, reset, ACPI, and user queue support.

## Important APIs, types, and functions
- Global module parameters include memory limits, scheduling controls, VM settings, display/DC options, power/RAS flags, reset method, MES, SmartShift, partitioning, WBRF, and KFD-related knobs.
- `struct amdgpu_device` is the driver-wide state object. It embeds PCI/DRM devices, ASIC identity, BIOS state, MMIO and doorbell state, GMC/GART/VM managers, memory manager/writeback, display, rings and schedulers, IRQ, powerplay/PM, IP block structs, firmware, PSP, UMC/DF/SMUIO/MCA/ACA/CPER, reset state, suspend/runtime PM state, RAS/debug flags, isolation state, UID/UMA state, and the trailing `struct amdgpu_kfd_dev`.
- `struct amdgpu_asic_funcs` defines ASIC-specific operations for BIOS access, register reads, VGA state, resets, clocks, PCIe lanes/usage, HDP cache management, BACO, stable pstate, video codec query, extended SMN addressing, and register-state export.
- Reset-related types include `enum amd_reset_method`, reset masks, init levels, `struct amdgpu_pcie_reset_ctx`, and reset helper prototypes.
- Memory and scheduling types include `struct amdgpu_sa_manager`, `struct amdgpu_wb`, `struct amdgpu_fpriv`, `struct amdgpu_mqd_prop`, `struct amdgpu_mqd`, and UMA carveout structures.
- Register macros include `RREG32`, `WREG32`, KIQ/no-KIQ variants, PCIe/SMC/UVD/DIDT/GC_CAC/audio endpoint accessors, field helpers, BIOS byte readers, and ASIC callback wrappers.
- Public internal prototypes cover device init/fini, reset/recovery, VRAM/MMIO access, KMS driver hooks, ACPI helpers, GPU instance registration, PCI error recovery, clock/power gating, bus-status checking, and UID access.

## Control flow
The header itself has compile-time flow: include guards, configuration-dependent declarations or stubs, and inline helpers. Runtime flow is defined by its contracts. Device load code populates `struct amdgpu_device`, assigns `asic_funcs`, initializes IP blocks, then calls functions declared here for hardware init, KMS, ACPI, reset, and power management.

Register access macros route through lower-level functions such as `amdgpu_device_rreg()`, `amdgpu_device_wreg()`, KIQ register accessors, PCIe register functions, and ASIC callbacks. ASIC wrapper macros call through `adev->asic_funcs`, sometimes with null checks for optional callbacks.

Configuration sections define behavior when optional features are absent. For example, without `CONFIG_ACPI`, ACPI functions are inline stubs returning harmless defaults or `-EINVAL`; without `CONFIG_VGA_SWITCHEROO`, ATPX helpers are no-ops; suspend-specific helpers default to false without suspend support.

## State and persistence behavior
`struct amdgpu_device` is the authoritative runtime state for a GPU instance. It persists for the life of the DRM device and owns or references almost all subsystem state: VM hubs, IP blocks, firmware, PSP context, display manager, reset domain, ACPI notifier, RAS lists, PCI saved state, work items, locks, xarrays, counters, and KFD state.

Persistent hardware/firmware data appears as loaded BIOS bytes, saved PCI state, firmware descriptors, RAS/CPER-related runtime accounting, and module parameter choices, but the header does not itself perform persistence. Its atomic counters track reset count, VRAM loss, bytes moved, evictions, page faults, and memory pinning across runtime operations.

## Dependencies and integration points
The header integrates the Linux kernel, DRM, TTM, KFD, AMD shared, display, memory, firmware, interrupt, RAS, CPER, and IP-block layers. Its include list is intentionally broad because `struct amdgpu_device` embeds many subsystem structs by value.

Major integration points are the DRM/KMS driver entry points, TTM/GEM BO management, SOC/IP register helpers, reset framework, ACPI ATIF/ATCS support, VGA switcheroo/ATPX, KFD HSA bridge, MES/user queues, RAS/ACA/CPER error handling, and power-management interfaces.

## Risks and edge cases
This header has high blast radius. Adding includes, fields, or macros can affect build times, circular dependencies, structure layout, and configuration-specific builds. The trailing `struct amdgpu_kfd_dev kfd` is explicitly noted as last because it contains a flexible-array-member-like `dev_pagemap`; moving it can break layout assumptions.

Register macros assume an `adev` variable exists in scope, which is convenient but fragile. ASIC wrapper macros dereference callback pointers, and only some wrappers check for optional callbacks. Call sites must ensure `adev->asic_funcs` is populated and the specific operation is supported.

State ordering matters in `struct amdgpu_device`: locks protect specific members, reset and suspend flags interact with workqueues and PCI error recovery, and many embedded subsystem structs are initialized in staged IP-block order. Configuration stubs must preserve behavior expected by callers on non-ACPI, non-HSA, or non-suspend builds.

## Test signals
Strong test signals are full amdgpu builds across multiple Kconfig combinations, successful probe/remove on discrete and APU devices, reset recovery, suspend/resume and runtime PM, KMS open/close/ioctls, TTM memory pressure, KFD initialization, RAS/ACA query paths, and register read/write smoke tests. Static signals include no circular include regressions, no missing stubs for disabled configs, and no warnings around macro callback access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c

## Purpose
`amdgpu_aca.c` implements Accelerator Check Architecture support for amdgpu RAS. It collects valid ACA banks from SMU firmware, filters them by hardware IP, dispatches them to registered ACA handles, parses and caches error counts, emits RAS event logs, optionally generates CPER records, exposes per-handle sysfs reads under the RAS group, and provides debugfs dump/debug-mode controls.

The code is a bridge between SMU-reported machine-check-style bank registers and amdgpu RAS accounting. It supports UE, CE, and deferred error flows and lets hardware-specific handle owners provide validation and parser callbacks.

## Important APIs, types, and functions
- `amdgpu_aca_init()`, `amdgpu_aca_fini()`, and `amdgpu_aca_reset()` initialize, clean up, and reset ACA manager state.
- `amdgpu_aca_set_smu_funcs()` installs the SMU callback table used to count banks, fetch banks, parse error codes, and set debug mode.
- `amdgpu_aca_add_handle()` and `amdgpu_aca_remove_handle()` register per-IP `struct aca_handle` objects, initialize their error caches, and add/remove `ras/aca_<name>` sysfs files.
- `amdgpu_aca_get_error_data()` is the main RAS query entry point. It updates banks from SMU, logs deferred errors where appropriate, drains the selected handle's error cache into `struct ras_err_data`, and clears cached bank errors after reporting.
- Bank collection helpers include `aca_smu_get_valid_aca_count()`, `aca_smu_get_valid_aca_banks()`, `aca_banks_add_bank()`, and `aca_banks_release()`.
- Dispatch and cache helpers include `aca_bank_is_valid()`, `aca_dispatch_banks()`, `aca_bank_parser()`, `aca_error_cache_log_bank_error()`, `aca_log_aca_error()`, and `aca_log_aca_error_data()`.
- `aca_bank_info_decode()` decodes IPID fields into hwid, mcatype, die id, and socket id.
- `aca_bank_check_error_codes()` delegates to SMU `parse_error_code()` and checks against an allowed list.
- Debug helpers create `aca_debug_mode`, `aca_ue_dump`, and `aca_ce_dump` when debugfs is enabled.

## Control flow
ACA starts with `amdgpu_aca_init()`, which initializes the handle manager and UE update flag. Hardware-specific RAS blocks call `amdgpu_aca_add_handle()` with an `aca_info` descriptor. If ACA is enabled through runtime state or `debug_enable_ras_aca`, the handle is added to the manager list, gets error-cache lists and locks, and receives a sysfs attribute.

When RAS queries errors, `amdgpu_aca_get_error_data()` checks the handle, validates the requested error type against the handle mask, maps UE to `ACA_SMU_TYPE_UE` and CE/deferred to `ACA_SMU_TYPE_CE`, then calls `aca_banks_update()`. That function checks whether UE banks should be updated, asks SMU for a valid bank count, fetches each bank, dumps registers to RAS event logs, filters out non-UMC poison UEs, appends banks to a temporary list, dispatches banks to matching handles, and generates CPER records. Dispatch invokes each handle's parser when the bank matches its hardware IP or is a deferred bank routed to UMC.

After update, `__aca_get_error_data()` drains deferred error cache unless the user explicitly asked for deferred only, then drains the requested error cache. Draining adds CE/UE/DE counts to `ras_err_data` per decoded socket/die and removes cache entries so the sysfs query is effectively read-and-clear.

Debugfs dump flows call the same update path with a handler that prints decoded bank info and register values before logging them into the normal error cache.

## State and persistence behavior
ACA runtime state lives under `adev->aca`. It owns the handle manager list, SMU function table, UE update atomic flag, and enable state. Each registered handle owns an error cache with per-error-type lists protected by mutexes. Cache entries accumulate counts by socket and die, not by every decoded field; `find_bank_error()` only keys on `socket_id` and `die_id`.

The cache is transient. It is cleared when RAS/sysfs reads drain entries, when handles are removed, or when ACA is finalized. `amdgpu_aca_reset()` clears the UE update flag. UE updates are throttled during RAS interrupt recovery through `ue_update_flag` so the same UE bank is not counted repeatedly before reset clears the SMU valid MCA count.

## Dependencies and integration points
The implementation depends on Linux list/mutex/sysfs/debugfs/seq_file helpers, amdgpu RAS accounting and event logging, CPER generation, SMU ACA callbacks supplied by ASIC-specific power-management code, UMC/GFX/SDMA RAS blocks that register handles, and `struct ras_query_context` event ids.

It integrates with `amdgpu_ras_aca_sysfs_read()` for sysfs reads, `amdgpu_ras_set_aca_debug_mode()` for debug mode writes, and `amdgpu_cper_generate_*_record()` when CPER output is enabled.

## Risks and edge cases
The cache key only uses socket and die, so multiple banks on the same socket/die are aggregated. That is useful for RAS counts but loses bank-specific detail after logs are emitted. Deferred errors are routed to UMC handles regardless of IP match; incorrect deferred classification can shift ownership.

UE update suppression depends on `amdgpu_ras_intr_triggered()` and the atomic flag. A missed reset of the flag can undercount later UEs; missing suppression can double count persistent valid banks. `aca_smu_get_valid_aca_banks()` filters poison UEs for non-UMC banks, so changes in SMU semantics could hide real non-UMC poison reports.

Sysfs attributes are only removed if `adev->dev->kobj.sd` exists. The code must handle teardown ordering where the RAS sysfs group is already gone. Debugfs dump paths both print and mutate caches by calling the normal parser, so reads can affect later query results.

## Test signals
Useful signals include successful handle registration/removal, presence and removal of `ras/aca_<name>` sysfs files, correct CE/UE/DE counts in RAS queries, read-and-clear cache behavior, CPER records generated when enabled, debugfs dumps showing expected bank registers, debug-mode toggling through SMU, and no duplicate UE counts across a single recovery. Fault-injection tests should cover missing SMU callbacks, invalid bank counts, non-matching hwid/mcatype, deferred banks, and parser failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h

## Purpose
`amdgpu_aca.h` defines the internal Accelerator Check Architecture interface for amdgpu RAS. It provides register bitfield decoders, ACA register indices, hardware IP and error-type enums, bank and handle data structures, SMU callback contracts, and public functions used by RAS blocks to register ACA handles and query error data.

## Important APIs, types, and functions
- Register helpers such as `ACA_REG__STATUS__UC()`, `ADDRV()`, `CECC()`, `UECC()`, `DEFERRED()`, `POISON()`, `ERRORCODEEXT()`, `ACA_REG__IPID__HARDWAREID()`, and `ACA_REG__MISC0__ERRCNT()` decode 64-bit bank registers.
- `enum aca_reg_idx` defines the 16-slot register dump layout, including control, status, address, misc, config, IPID, syndrome, deferred status/address, and control mask.
- `enum aca_hwip_type`, `enum aca_error_type`, and `enum aca_smu_type` define dispatch and accounting domains.
- `struct aca_bank` stores a bank's SMU error type, parsed ACA error type, and raw register array.
- `struct aca_handle` represents one registered RAS block's ACA binding, including device, manager, error cache, bank operations, sysfs attribute, name, mask, and private data.
- `struct aca_bank_ops` lets a handle validate and parse banks.
- `struct aca_smu_funcs` is the platform callback table for SMU debug mode, valid-bank count, valid-bank fetch, and error-code parsing.
- `struct amdgpu_aca` is embedded in `struct amdgpu_device`.
- Public functions include lifecycle, SMU-function installation, handle registration/removal, error-data query, bank-info decode, error-code check, debug mode/debugfs helpers, and direct cache logging.

## Control flow
This header has no executable flow, but it defines the flow used by `amdgpu_aca.c`: platform code installs `aca_smu_funcs`; RAS blocks add `aca_handle` objects with `aca_info` and `aca_bank_ops`; query code fetches banks through SMU callbacks; banks are filtered/parsed by handle callbacks; parsed counts are accumulated into handle error caches and later drained into RAS data.

## State and persistence behavior
The data structures describe transient kernel state. `aca_handle_manager` tracks live handles, `aca_error_cache` stores accumulated per-handle counts, and `amdgpu_aca` stores the SMU callback table and UE update flag. The header defines no persistent storage or firmware ABI beyond numeric bit definitions matching ACA register formats.

## Dependencies and integration points
The header depends on Linux lists and forward-declared RAS query/counting types. It is included by `amdgpu.h`, `amdgpu_aca.c`, and RAS hardware blocks that need to register ACA handlers or use bank decode helpers. It also encodes SMN base constants for SMU MCA banks.

## Risks and edge cases
Bitfield macros are register-format contracts. Incorrect high/low bit positions would misclassify error validity, UE/CE/deferred/poison status, address validity, or bank identity. The enum ordering of `aca_error_type` is used with `BIT_MASK()` masks, so reordering values affects handle masks.

The misspelled `ACA_HWIP_TYPE_UNKNOW` and `ACA_BANK_ERR_IS_DEFFERED` are part of the current internal API spelling and should not be renamed casually. `ACA_MAX_REGS_COUNT` must stay consistent with `ACA_REG_IDX_COUNT` and all register dump indices.

## Test signals
Compile-time coverage should include all RAS blocks that include this header. Runtime signals are correct bank register dumps, correct `aca_bank_info_decode()` output for known IPID values, correct masks for UE/CE/deferred queries, and successful SMU callback integration on ACA-enabled ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c

## Purpose
`amdgpu_acp.c` implements the amdgpu IP block for the AMD Audio Co-Processor 2.x. It initializes ACP software state, powers and resets ACP hardware, registers MFD child devices for the ACP DMA and DesignWare I2S controllers, wires children into a generic PM domain, handles board-specific I2S resource layout quirks, and exposes the `acp_ip_block` version descriptor to the amdgpu IP manager.

## Important APIs, types, and functions
- `acp_sw_init()` creates the CGS device used for ACP register access and stores `adev->acp.parent`.
- `acp_sw_fini()` destroys the CGS device.
- `struct acp_pm_domain` wraps a generic PM domain and back pointer to `amdgpu_device`.
- `acp_poweroff()` and `acp_poweron()` call SMU power-gating helpers to gate/ungate the ACP block for PM-domain transitions.
- `acp_hw_init()` calls `amd_acp_hw_init()`, allocates `acp_genpd`, MFD cells, resources, and I2S platform data, registers child devices, adds them to the PM domain, performs ACP soft reset, enables ACP clock, and deasserts reset.
- `acp_hw_fini()` asserts soft reset, disables clock, removes children from genpd, removes MFD devices, and frees allocated resources.
- `acp_suspend()` and `acp_resume()` manage power gating for systems where no ACP child cell was registered.
- `acp_set_powergating_state()` gates or ungates ACP through SMU.
- `acp_ip_funcs` and `acp_ip_block` expose the AMD IP block callbacks and version 2.2 descriptor.

## Control flow
The amdgpu IP manager calls `sw_init` first, creating the CGS device. Hardware init then calls `amd_acp_hw_init()`. If it returns `-ENODEV`, the board uses AZ audio rather than ACP, so ACP is power-gated and init succeeds with no child devices. Otherwise, the function validates MMIO size, creates the PM domain, checks DMI quirks, and branches on `acp_machine_id`.

For `ST_JADEITE`, the file creates two MFD cells: `acp_audio_dma` and a combined playback/capture `designware-i2s` child, with three resources. For the default path, it creates four MFD cells: DMA plus separate playback, capture, and Bluetooth I2S controllers, with five resources. Stoney ASICs receive I2S quirks for 16-bit index override and capture comp-param handling.

After child registration, the code asserts ACP soft reset and polls for `SoftResetAudDone`, enables ACP clock and polls `mmACP_STATUS`, then deasserts soft reset. Failure paths free allocated arrays and return the error. Hardware fini mirrors reset/clock operations, removes PM-domain attachments, removes MFD children, and frees resources.

## State and persistence behavior
ACP state is runtime-only and stored in `adev->acp`: parent device, CGS device, private pointer, MFD cell array, resource array, and PM domain pointer. A file-static `acp_machine_id` records DMI quirk detection during init.

The MFD child devices and PM-domain membership persist until `acp_hw_fini()`. ACP power state changes are delegated to SMU and can be triggered by IP-block power-gating callbacks or child PM-domain transitions. No persistent user data is written.

## Dependencies and integration points
The file depends on Linux platform/MFD/generic PM domain/DMI/ACPI headers, DesignWare I2S platform data, ALSA PCM rate constants, CGS register helpers, ACP GFX interface helpers, SMU power-gating through `amdgpu_dpm_set_powergating_by_smu()`, and amdgpu IRQ mapping.

It integrates with downstream audio drivers via MFD cells named `acp_audio_dma` and `designware-i2s`; with runtime PM through `generic_pm_domain`; and with amdgpu IP-block lifecycle through `acp_ip_block`.

## Risks and edge cases
The allocation failure path frees `i2s_pdata`, `acp_res`, `acp_cell`, and `acp_genpd`, but `i2s_pdata` is only owned through MFD platform data after successful `mfd_add_devices()`. Lifetime must stay compatible with child device expectations. The default path allocates `i2s_pdata` locally and does not explicitly free it on normal `hw_fini`, so ownership/lifetime is subtle.

The clock-disable poll in `acp_hw_fini()` checks for `val & 0x1`, the same condition as enable, which may be hardware-specific but is suspicious and should be tested against real ACP status semantics. MMIO-size validation uses a fixed threshold. Board quirks depend on exact DMI strings and leave `acp_machine_id` static for future init calls.

## Test signals
Good signals include successful ACP audio playback/capture on default and Jadeite/ASN boards, correct MFD child creation, child removal without leaks or use-after-free, PM-domain power on/off calls reaching SMU, soft reset and clock polls completing, and `-ENODEV` boards cleanly power-gating ACP without exposing children. Suspend/resume should preserve behavior both with and without registered ACP cells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h

## Purpose
`amdgpu_acp.h` defines the internal ACP state embedded in `struct amdgpu_device` and declares the ACP IP block descriptor. It is the local interface between the amdgpu core device object and the ACP IP-block implementation in `amdgpu_acp.c`.

## Important APIs, types, and functions
- `struct amdgpu_acp` stores the parent device, CGS device, ACP private pointer, MFD cells, resources, and PM-domain pointer.
- `extern const struct amdgpu_ip_block_version acp_ip_block;` exposes ACP 2.2 IP callbacks for the IP manager.

## Control flow
The header has no runtime flow. Runtime users access `adev->acp` fields during ACP `sw_init`, `hw_init`, `hw_fini`, suspend/resume, and power-gating callbacks.

## State and persistence behavior
The struct fields describe runtime-owned kernel resources. `cgs_device`, `acp_cell`, `acp_res`, and `acp_genpd` are allocated and freed by the ACP implementation. No persistent state is defined here.

## Dependencies and integration points
The header includes `<linux/mfd/core.h>` for `struct mfd_cell`. It is included from `amdgpu.h`, so the ACP state becomes part of the central device structure when `CONFIG_DRM_AMD_ACP` is enabled.

## Risks and edge cases
Because the struct stores raw resource pointers, init/fini ordering must ensure fields are either valid or null when callbacks run. Adding fields here changes `struct amdgpu_device` layout through the embedded ACP member.

## Test signals
Compile with `CONFIG_DRM_AMD_ACP`, successful ACP IP-block registration, and clean probe/remove with no dangling ACP pointers are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c

## Purpose
`amdgpu_acpi.c` implements amdgpu's ACPI integration. It detects and verifies AMD ATIF and ATCS methods, handles ACPI video and AC power notifications, routes SBIOS requests for brightness and dGPU display events, exposes ATCS calls for PCIe performance, SmartShift, power-shift control, and UMA allocation, enumerates ACPI XCC objects for NUMA/TMR memory information, and provides suspend-mode helpers for GPU reset policy.

The file owns global ACPI capability state for the driver and per-driver XCC topology state. It is not per-device for ATIF/ATCS; the detected handles and function masks live in a singleton `amdgpu_acpi_priv`.

## Important APIs, types, and functions
- ATIF helpers: `amdgpu_atif_call()`, `amdgpu_atif_verify_interface()`, `amdgpu_atif_get_notification_params()`, `amdgpu_atif_query_backlight_caps()`, `amdgpu_atif_get_sbios_requests()`, and `amdgpu_atif_handler()`.
- ATCS helpers: `amdgpu_atcs_call()`, `amdgpu_atcs_verify_interface()`, `amdgpu_acpi_is_pcie_performance_request_supported()`, `amdgpu_acpi_pcie_notify_device_ready()`, `amdgpu_acpi_pcie_performance_request()`, `amdgpu_acpi_power_shift_control()`, `amdgpu_acpi_smart_shift_update()`, and `amdgpu_acpi_set_uma_allocation_size()`.
- XCC/NUMA helpers: `amdgpu_acpi_enumerate_xcc()`, `amdgpu_acpi_get_xcc_info()`, `amdgpu_acpi_dev_init()`, `amdgpu_acpi_get_tmr_info()`, `amdgpu_acpi_get_mem_info()`, and `amdgpu_acpi_release()`.
- Device lifecycle: `amdgpu_acpi_detect()` scans display PCI devices for ATIF/ATCS and enumerates XCC ACPI devices; `amdgpu_acpi_init()` binds a backlight device and registers the ACPI notifier; `amdgpu_acpi_fini()` unregisters it.
- Power/reset helpers: `amdgpu_acpi_should_gpu_reset()`, `amdgpu_acpi_is_s3_active()`, and `amdgpu_acpi_is_s0ix_active()`.
- Optional ISP helper: `amdgpu_acpi_get_isp4_dev()` finds supported ACPI camera sensor devices when ISP support is enabled.

## Control flow
Global ACPI detection scans PCI display-class devices and tries to find `ATIF` and `ATCS` methods under their ACPI handles. Each found handle is verified by calling the interface verification method, parsing version, notification masks, and function masks. Detection then fetches ATIF notification parameters, optionally queries backlight transfer characteristics, and enumerates `AMD3000` through `AMD3023` XCC objects until the first missing HID.

Per-device ACPI init uses detected ATIF state. If brightness-change notification is supported, it selects a DC backlight device or legacy encoder backlight. It then registers `adev->acpi_nb`, whose callback handles AC adapter events through `amdgpu_pm_acpi_event_handler()` and forwards video-class events to `amdgpu_atif_handler()`.

ATIF event handling filters to the configured video notification code, reads pending SBIOS requests, applies brightness changes through the selected backlight device, and for dGPU display events on PX systems wakes runtime PM, emits HPD notification through DRM helper code, and returns `NOTIFY_BAD` to stop ACPI video keypress propagation.

ATCS call paths build method-specific input buffers. PCIe performance request first sends device-ready notification, then retries `ATCS_FUNCTION_PCIE_PERFORMANCE_REQUEST` while firmware reports in-progress. SmartShift maps driver/device lifecycle events to power-shift control states. UMA allocation sends index/type through the ATCS set-UMA method.

XCC enumeration evaluates DSM functions for supported function count, VF-to-XCC mapping, supported/current XCP mode, memory mode, and TMR base/size. It groups XCC entries by physical function SBDF and stores NUMA data from `_PXM` in an xarray keyed by proximity domain.

## State and persistence behavior
`amdgpu_acpi_priv` stores singleton ATIF and ATCS handles, function masks, notification configuration, current backlight device pointer, and backlight capability data. `amdgpu_acpi_dev_list` stores enumerated ACPI GPU device records, each with a list of XCC records. `numa_info_xa` stores allocated NUMA info by PXM.

State persists until global release. `amdgpu_acpi_fini()` only unregisters the per-device notifier; it does not clear global ATIF/ATCS or XCC state. `amdgpu_acpi_release()` frees NUMA and XCC/device lists. Backlight caps are copied out through `amdgpu_acpi_get_backlight_caps()`.

## Dependencies and integration points
The file depends on Linux ACPI, PCI, xarray, power supply, runtime PM, suspend state, ACPI video, ACPI NUMA, DRM backlight/display helpers, AMD ACPI method structure definitions from `amd_acpi.h`, atom display types, and optional AMD PMC/ISP configuration.

It integrates with display hotplug (`drm_helper_hpd_irq_event()`), DC and legacy backlight devices, amdgpu PM AC-event handling, device reset policy, SmartShift support, KFD/partition memory information through TMR/NUMA data consumers, and ACPI-notifier registration.

## Risks and edge cases
ATIF/ATCS state is global, so multi-GPU systems rely on the first detected handles and shared function masks. Error handling around ACPI buffers assumes the first two bytes are a size field before copying into packed output structs; firmware returning malformed buffers can produce `-EINVAL` or disabled notifications.

The PCIe performance request loop returns success after retries are exhausted even if the last return was still in-progress. That may be intentional firmware tolerance, but it is a behavioral edge. `amdgpu_acpi_detect()` initializes XCC lists and xarray each time it runs; repeated detect/release ordering must avoid leaks or stale global state.

Suspend policy is configuration-sensitive. S0ix requires APU, suspend-to-idle, Raven or newer, GFXOFF feature, low-power S0 FADT flag, and `CONFIG_AMD_PMC`; otherwise it logs once and returns false. Reset policy skips GPU reset for IMU-enabled APUs, APU S3, and SR-IOV VFs.

## Test signals
Useful signals include ATIF/ATCS detection in dmesg, correct function masks, working brightness changes from firmware events, HPD events on PX dGPU display events, AC power events updating PM state, successful PCIe performance requests, SmartShift power-shift notifications on load/D0/D3/unload, UMA allocation method success, correct TMR and NUMA info for XCC devices, clean ACPI notifier unregister, and no leaks after `amdgpu_acpi_release()`. Suspend tests should cover S3 and S0ix policy decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c

## Purpose
`amdgpu_afmt.c` calculates HDMI audio clock regeneration values for amdgpu display code. It returns CTS/N timing values for 32 kHz, 44.1 kHz, and 48 kHz audio rates for a given pixel clock, using a table for common HDMI clocks and a fallback calculation for odd clocks.

## Important APIs, types, and functions
- `amdgpu_afmt_predefined_acr[]` stores known-good ACR values for common clocks such as 25.175 MHz, 27 MHz, 74.25 MHz, and 148.5 MHz, including 1000/1001 variants.
- `amdgpu_afmt_calc_cts()` computes CTS and N using GCD reduction and a multiplier chosen to avoid truncation.
- `struct amdgpu_afmt_acr amdgpu_afmt_acr(uint32_t clock)` is the exported helper declared in `amdgpu.h`.
- The return type stores the clock and CTS/N pairs for 32 kHz, 44.1 kHz, and 48 kHz.

## Control flow
`amdgpu_afmt_acr()` scans the predefined table and returns an exact match when the pixel clock is known. If no entry matches, it calls `amdgpu_afmt_calc_cts()` three times for 32000, 44100, and 48000 Hz, then fills `res.clock`.

The fallback starts with safe but large values, reduces the fraction by `gcd(n, cts)`, computes a multiplier based on the ideal `128 * freq / 1000` target, scales N and CTS, warns if N is outside the HDMI spec range, and returns the computed values.

## State and persistence behavior
The file has no mutable state. The predefined table is static const, and calculated results are returned by value. No persistent state or hardware programming happens here.

## Dependencies and integration points
The file depends on Linux HDMI definitions, `gcd()`, DRM debug logging, and the `struct amdgpu_afmt_acr` declaration in `amdgpu.h`. Display encoder code calls `amdgpu_afmt_acr()` before programming HDMI/AFMT audio timing registers.

## Risks and edge cases
The fallback calculation can produce values outside spec for unusual clocks; it warns but still returns a value. The predefined table must remain authoritative for common CEA clocks because small arithmetic differences can affect HDMI audio compatibility. The clock unit is kHz, and mixing Hz/kHz units would produce invalid CTS values.

## Test signals
Good signals include correct HDMI audio at common display modes, no warnings for predefined clocks, expected warnings for truly odd pixel clocks, and register programming that matches HDMI compliance values. Unit-style tests can compare table lookups and known fallback calculations for selected non-table clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_afmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c

## Purpose
`amdgpu_amdkfd.c` implements the amdgpu side of the private KGD-to-KFD bridge. It initializes and shuts down KFD support, probes and initializes per-GPU KFD devices, reports shared GPU resources, manages KFD suspend/resume/reset handoff, allocates kernel/GWS memory for KFD, exposes firmware/memory/clock/dmabuf/PCIe information, submits low-level IBs, toggles compute idle power policy, drains interrupts, and forwards RAS/poison and scheduler operations.

## Important APIs, types, and functions
- Global lifecycle: `amdgpu_amdkfd_init()`, `amdgpu_amdkfd_fini()`, and `amdgpu_amdkfd_device_probe()`.
- Device lifecycle: `amdgpu_amdkfd_device_init()` builds `kgd2kfd_shared_resources` and calls `kgd2kfd_device_init()`; `amdgpu_amdkfd_device_fini_sw()` calls `kgd2kfd_device_exit()`.
- DRM client support: `amdgpu_amdkfd_drm_client_create()` registers a DRM client named `kfd`.
- Reset/suspend/process flow: `amdgpu_amdkfd_suspend()`, `resume()`, `suspend_process()`, `resume_process()`, `pre_reset()`, `post_reset()`, `gpu_reset()`, and `amdgpu_amdkfd_reset_work()`.
- Memory helpers: `amdgpu_amdkfd_alloc_kernel_mem()`, `free_kernel_mem()`, `alloc_gws()`, and `free_gws()`.
- Information helpers: `amdgpu_amdkfd_get_fw_version()`, `get_local_mem_info()`, `get_gpu_clock_counter()`, `get_max_engine_clock_in_mhz()`, `get_dmabuf_info()`, `get_pcie_bandwidth_mbytes()`, and `amdgpu_amdkfd_xcp_memory_size()`.
- Execution/control helpers: `amdgpu_amdkfd_submit_ib()`, `set_compute_idle()`, `is_kfd_vmid()`, `have_atomics_support()`, `unmap_hiq()`, `stop_sched()`, `start_sched()`, `compute_active()`, and `config_sq_perfmon()`.
- RAS/interrupt helpers forward poison consumption and close-event payloads into KFD/UMC/interrupt code.

## Control flow
Module-level init calculates total system memory from `si_meminfo()`, calls `kgd2kfd_init()`, and records whether KFD initialized. Per-device probe calls `kgd2kfd_probe()` if global KFD init succeeded. Device init initializes GPUVM memory limits, builds shared resources from VMID allocation, MEC queue topology, GPUVM size, render node minor, SDMA doorbell index, MES state, compute queue bitmap, doorbell aperture, and non-CP doorbell range, then calls `kgd2kfd_device_init()`.

Reset flow is delegated both ways. KFD can trigger `amdgpu_amdkfd_gpu_reset()`, which schedules `adev->kfd.reset_work` on the reset domain if recovery is allowed. The work item builds an `amdgpu_reset_context` with source HWS or MES and calls `amdgpu_device_gpu_recover()`. During amdgpu reset, pre/post reset calls are forwarded to KFD.

Memory allocation for KFD creates amdgpu BOs with kernel/device types, pins them, allocates GART backing, maps to CPU when needed, and returns BO pointer, GPU address, and CPU pointer. Failure unwinds in reverse order. GWS allocation creates a user BO in the GWS domain with no CPU access.

Low-level IB submission chooses a compute or SDMA ring by KGD engine type, allocates an amdgpu job, fills one IB with caller-provided command pointer and VMID, schedules it, waits on the returned fence, drops the fence reference, and frees the job.

## State and persistence behavior
Global state includes `amdgpu_amdkfd_total_mem_size` and `kfd_initialized`. Per-device KFD state lives in `adev->kfd`: KFD device pointer, VRAM accounting arrays, init-complete flag, reset work, DRM client, and HMM page map. Device init increments total memory by real VRAM size; fini decrements it.

Memory helpers create BOs whose lifetime is owned by KFD through opaque `mem_obj` pointers. Scheduler and process suspend state are owned by KFD but controlled through forwarded calls. No persistent storage is written by this file.

## Dependencies and integration points
The file depends on the `kgd2kfd_*` callback interface, amdgpu VM/BO/job/IB/ring/doorbell/GFX/SDMA/DPM/XGMI/RAS/UMC/reset code, DRM client registration, dma-buf and TTM helpers, Linux KFD UAPI flags, and PSP performance-monitor configuration.

It integrates with KFD HSA runtime support, HMM/SVM memory migration through declarations in the header, reset domains, interrupt handling, RAS poison handling, and power management. It also relies on `amdgpu_amdkfd.h` stubs so builds without HSA support compile cleanly.

## Risks and edge cases
Doorbell reporting changes when MES is enabled: KFD receives only the base address while amdgpu manages the doorbell space. Non-MES paths must correctly reserve kernel doorbells at the start of the aperture. Incorrect queue bitmap complementing or last-valid-bit clearing can expose invalid compute queues to KFD.

`amdgpu_amdkfd_submit_ib()` uses caller-provided IB memory and explicit VMID, with a comment noting this works for NO_HWS and needs better handling without knowing VMID. It waits synchronously and must free jobs/fences on all paths.

`amdgpu_amdkfd_unmap_hiq()` fabricates a temporary ring/functions pair for KIQ unmap queues and locks the KIQ ring while emitting packets. Allocation failures, reset-in-progress, or unscheduled rings must be handled without leaving ring state inconsistent.

Memory accounting and partition sizing are subtle for APUs, XCP memory partitioning, NPS1 app-APU mode, even memory capping, and `apu_prefer_gtt`. Wrong size reporting can overcommit ROCm allocations or hide usable memory.

## Test signals
Good signals include KFD module init/fini success, per-GPU KFD node creation, correct queue/doorbell resources in KFD topology, ROCm process creation and teardown, suspend/resume with and without S0ix, GPU reset recovery with active KFD queues, BO allocation/free leak tests, GWS allocation, dmabuf import metadata checks, PCIe bandwidth values matching link masks, IB submission completion, HIQ unmap success, scheduler stop/start behavior, and poison consumption notifications reaching KFD/UMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h

## Purpose
`amdgpu_amdkfd.h` defines the private interface between amdgpu and AMD KFD. It declares bridge lifecycle functions, memory-management types and APIs, KFD device state embedded in `struct amdgpu_device`, GPUVM helpers, reset/suspend/scheduler hooks, KGD-to-KFD callback prototypes, and fallback stubs for builds without HSA/KFD/SVM support.

## Important APIs, types, and functions
- `enum TLB_FLUSH_TYPE`, `enum kfd_mem_attachment_type`, and `enum kgd_engine_type` define bridge-level enums for GPUVM and engine operations.
- `struct kfd_mem_attachment` describes per-device mappings of a KFD allocation with BO VA, VA address, flags, mapping state, and attachment type.
- `struct kgd_mem` is the KFD-facing memory object containing an amdgpu BO or dma-buf/range, attachment list, validation list, domain, VA, allocation flags, invalidation state, process info, sync object, GEM handle, and import/AQL flags.
- `struct amdgpu_amdkfd_fence` extends `dma_fence` for KFD eviction and SVM synchronization.
- `struct amdgpu_kfd_dev` stores per-device KFD state: KFD device pointer, per-XCP VRAM usage counters, init flag, reset work, DRM client, and HMM `dev_pagemap`.
- `struct amdkfd_process_info` tracks all amdgpu VMs and BOs associated with a KFD process, userptr valid/invalid lists, eviction fence, MMU-notifier state, restore work, pid, and notification blocking flag.
- Public bridge APIs cover init/fini, device probe/init/fini, suspend/resume, reset, process teardown, interrupts, memory allocation, GWS, firmware/version queries, local memory and clock info, dmabuf info, PCIe bandwidth, HIQ unmap, scheduler controls, SQ perfmon config, GPUVM allocation/map/sync/import/export, RAS poison, memory limits, and XCP memory sizing.
- `read_user_wptr()` safely reads a user write pointer with page faults disabled and optional temporary kthread mm adoption.
- The `kgd2kfd_*` declarations and stubs define the callback boundary into KFD.

## Control flow
This header defines the call graph used by amdgpu and KFD. amdgpu core calls the `amdgpu_amdkfd_*` lifecycle hooks around probe, init, suspend, reset, and teardown. KFD calls back through memory/GPUVM helpers to allocate BOs, map/unmap GPU memory, synchronize, manage process VMs, reserve memory limits, and drive low-level queues.

Kconfig controls large parts of the flow. With `CONFIG_HSA_AMD`, real KFD callbacks and GPUVM/fence helpers are available. Without it, many functions become no-op or harmless-return stubs so the rest of amdgpu can compile and call bridge hooks unconditionally. With `CONFIG_HSA_AMD_SVM`, zone-device initialization is real; otherwise it is a stub returning success.

## State and persistence behavior
The header describes runtime state owned by amdgpu and KFD. `kgd_mem` objects persist while KFD allocations live. Attachments persist while mapped to one or more GPUs. `amdkfd_process_info` persists for a KFD process and coordinates BO lists, eviction fences, and MMU notifier state. `amdgpu_kfd_dev` persists for the lifetime of an amdgpu device.

No persistent disk state is defined. Memory-limit counters and VRAM usage arrays are runtime accounting only.

## Dependencies and integration points
The header depends on Linux list/mm/kthread/workqueue/mmu-notifier/memremap types, DRM client support, KFD topology and interface headers, amdgpu sync/VM/XCP types, and KFD ioctl flags. It is included by `amdgpu.h`, `amdgpu_amdkfd.c`, GPUVM bridge implementation files, and KFD-facing amdgpu code.

It is a major integration point between DRM render-node/GEM/TTM memory management and ROCm/HSA process management.

## Risks and edge cases
Many structs cross subsystem ownership boundaries. Locking comments are important: `kgd_mem.validate_list` is protected by `amdkfd_process_info.lock`; BO lists, userptr lists, and MMU-notifier state have separate locks. Misusing these types can create deadlocks between DQM, mmap locks, BO reservations, and MMU notifier paths.

The `read_user_wptr()` macro deliberately disables page faults and borrows an mm for kthreads. It must only be used when the memory is pinned and mapped, as the comment states. The stubs for disabled HSA builds must preserve caller expectations; returning success for some stubs and false/error for others is part of the contract.

`struct amdgpu_kfd_dev` contains `dev_pagemap` and is embedded last in `struct amdgpu_device`; layout assumptions from `amdgpu.h` must be preserved.

## Test signals
Compile coverage should include HSA enabled/disabled, HSA SVM enabled/disabled, debugfs enabled/disabled, and P2P enabled/disabled. Runtime signals include ROCm allocation/map/unmap, userptr invalidation/restore, eviction fencing, dmabuf import/export, process teardown, scheduler stop/start, reset pre/post callbacks, and successful no-HSA amdgpu probe with all bridge stubs linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h -->
