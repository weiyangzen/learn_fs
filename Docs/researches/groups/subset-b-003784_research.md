# subset-b-003784 Research

This grouped report covers Xe SR-IOV PF/VF provisioning and migration, tile infrastructure, SVM, sync objects, TLB invalidation, stepping, survivability mode, and tracepoint instantiation. Each source section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c

## Purpose

`xe_sriov_pf_provision.c` implements Physical Function provisioning policy for Xe SR-IOV resources. It switches between automatic and custom provisioning and applies per-VF or bulk configuration for execution quantum, preemption timeout, scheduling priority, and VRAM/LMEM quota across all GTs or tiles.

## Important APIs, Types, and Functions

The public API is the `xe_sriov_pf_provision_*` family declared in the paired header. Auto provisioning flows through `xe_sriov_pf_provision_vfs()` and `xe_sriov_pf_unprovision_vfs()`, using `xe_gt_sriov_pf_config_set_fair()` and `xe_gt_sriov_pf_config_release()`. Scheduler tunables are handled by `*_apply_vf_eq`, `*_query_vf_eq`, `*_apply_vf_pt`, `*_query_vf_pt`, `*_apply_vf_priority`, and bulk equivalents. VRAM quota is handled by `*_apply_vf_vram`, `*_bulk_apply_vram`, and `*_query_vf_vram`. `xe_sriov_pf_provision_set_mode()` is the mode transition gate.

## Control Flow

Auto mode provisions VFs by iterating every GT and assigning a fair split from `VFID(1)` through `num_vfs`. Unprovisioning releases each VF on each GT. Most EQ/PT/VRAM operations take `xe_sriov_pf_master_mutex(xe)` and then iterate GTs or tiles, preserving the first error while attempting all backends. Query operations compare every GT's value and return `-EUCLEAN` through `pf_report_unclean()` if per-GT state diverges. VRAM quota rounds the requested device-wide size up to tile count times LMTT page alignment, then divides it per tile.

## State and Persistence Behavior

The persistent device-level state is `xe->sriov.pf.provision.mode`. Resource assignments themselves persist in GT PF configuration objects and tile LMTT-backed LMEM provisioning, not in this file. Switching from auto to custom preserves existing allocations; switching back to auto is refused while VFs are enabled and otherwise releases all VF resources.

## Dependencies and Integration Points

This file depends on SR-IOV helpers for VF counts and PF assertions, GT PF config/policy code for actual GuC-facing provisioning, LMTT page size for VRAM alignment, and `xe_sriov_printk.h` for diagnostics. It is called from PF enable/disable flows, sysfs bulk/per-VF attributes, and SR-IOV debugfs quota controls.

## Risks and Test Signals

Risks include partial success across GTs because the first error is returned after later GTs may already have changed, stale custom allocations when changing modes intentionally preserves resources, and inconsistent query state on multi-GT devices. Tests should cover mode transitions with VFs enabled/disabled, multi-GT inconsistency returning `-EUCLEAN`, VRAM rounding on multi-tile devices, and sysfs/debugfs paths forcing custom mode after manual quota changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h

## Purpose

`xe_sriov_pf_provision.h` is the PF provisioning public interface. It exports the functions used by PF setup, sysfs, debugfs, and VF lifecycle code to allocate or query SR-IOV resources.

## Important APIs, Types, and Functions

The header declares bulk and per-VF operations for execution quantum (`eq`), preemption timeout (`pt`), scheduling priority, and VRAM quota. It also exposes `xe_sriov_pf_provision_vfs()`, `xe_sriov_pf_unprovision_vfs()`, and `xe_sriov_pf_provision_set_mode()`. The inline `xe_sriov_pf_provision_set_custom_mode()` is a convenience wrapper for callers that should preserve manual allocations.

## Control Flow

Callers parse user or policy input, then call these APIs rather than touching GT config directly. Bulk APIs affect all VFs and, where supported, PF policy. Per-VF APIs use 1-based VF identifiers with `PFID` equal to zero where the implementation allows PF priority handling.

## State and Persistence Behavior

The header does not own state, but it exposes operations that mutate persistent PF provisioning mode and backend GT/tile resource configuration. The included `xe_sriov_pf_provision_types.h` makes the mode enum part of the public contract.

## Dependencies and Integration Points

It depends on Linux integer types and the provisioning types header. Integration points include `xe_sriov_pf_sysfs.c`, `xe_tile_sriov_pf_debugfs.c`, PF SR-IOV enable/disable control, and tests of GT provisioning policy.

## Risks and Test Signals

The API relies on callers to pass a PF device and valid VF IDs; most validation is in implementation asserts. Compile tests should catch signature drift, and behavioral tests should verify all declared operations remain wired to sysfs/debugfs consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h

## Purpose

`xe_sriov_pf_provision_types.h` defines the small persistent type surface for PF provisioning mode.

## Important APIs, Types, and Functions

`enum xe_sriov_provisioning_mode` has `XE_SRIOV_PROVISIONING_MODE_AUTO` and `XE_SRIOV_PROVISIONING_MODE_CUSTOM`; a static assertion guarantees auto remains zero. `struct xe_sriov_pf_provision` stores the selected mode.

## Control Flow

The mode drives `xe_sriov_pf_provision_vfs()` and unprovisioning behavior. Auto mode lets VF enable/disable implicitly allocate and release resources. Custom mode makes allocations explicit through uABI/sysfs/debugfs paths and preserves them across VF disable.

## State and Persistence Behavior

`struct xe_device_pf` embeds `struct xe_sriov_pf_provision`, so the mode persists for the PF device lifetime. There is no serialization in this header; users must rely on PF provisioning functions for coordinated changes.

## Dependencies and Integration Points

The header only needs `linux/build_bug.h`. It is included by PF provisioning, PF type definitions, and the provisioning API header.

## Risks and Test Signals

Changing enum values would alter default mode and break assumptions in initialization. Tests should verify newly initialized PF state defaults to auto and that user-visible mode transitions preserve the semantics documented here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_provision_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c

## Purpose

`xe_sriov_pf_service.c` implements PF-side negotiation of the VF/PF GuC relay ABI version. It records the PF's base/latest supported versions and tracks the negotiated ABI for each VF.

## Important APIs, Types, and Functions

`xe_sriov_pf_service_init()` initializes base and latest ABI versions from `guc_relay_actions_abi.h`. `xe_sriov_pf_service_handshake_vf()` negotiates a VF-requested version, stores it with `pf_connect()`, or clears it with `pf_disconnect()`. `xe_sriov_pf_service_is_negotiated()` checks whether a VF can use a feature requiring a specific ABI. `xe_sriov_pf_service_reset_vf()` clears per-VF negotiation state. `xe_sriov_pf_service_print_versions()` emits base/latest and per-VF negotiated versions.

## Control Flow

During PF service initialization, compile-time checks ensure a nonzero base ABI and sane major ordering. On handshake, a VF may request "any" and receive latest, request a newer major and receive the PF latest, request an older-than-base version and get `-EPERM`, or request the same major and receive the lower common minor. Previous major support is currently rejected with `-ENOPKG` unless the driver grows true multi-version support.

## State and Persistence Behavior

PF-wide base/latest versions live in `xe->sriov.pf.service.version`. Per-VF negotiated versions live in `xe->sriov.pf.vfs[vfid].version` and remain until reset, failed negotiation, VF reset, or PF teardown.

## Dependencies and Integration Points

The file integrates with GuC relay ABI constants, SR-IOV PF helper validation, debug printing, and debugfs/service diagnostics. It includes the KUnit service test when built with Xe KUnit support.

## Risks and Test Signals

The major-version path is intentionally not multi-version capable and asserts if base/latest majors diverge. Tests should cover `ANY`, newer-than-latest, older-than-base, same-major minor clamping, reset behavior, and printed version output. Consumers should check `xe_sriov_pf_service_is_negotiated()` before using ABI-gated relay features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h

## Purpose

`xe_sriov_pf_service.h` exposes the PF service ABI negotiation API.

## Important APIs, Types, and Functions

The declarations cover service initialization, version printing, VF handshake, negotiated-version checks, and VF reset. The interface uses `u32` requested/selected major and minor values while persistent storage uses the service type struct's `u16` fields.

## Control Flow

PF initialization calls `xe_sriov_pf_service_init()` before any VF handshakes. Relay handling calls `xe_sriov_pf_service_handshake_vf()` when a VF connects, and feature handlers can call `xe_sriov_pf_service_is_negotiated()` to gate newer functionality. VF reset paths call `xe_sriov_pf_service_reset_vf()`.

## State and Persistence Behavior

No state is stored here; it is a stable contract over `xe->sriov.pf.service` and `xe->sriov.pf.vfs[].version`.

## Dependencies and Integration Points

It depends only on Linux types and forward declarations. Integration points include PF relay message handling, debugfs printing, and KUnit coverage in the implementation.

## Risks and Test Signals

Callers must pass PF devices and valid VF IDs. Build coverage should catch ABI signature drift, while handshake tests should verify the header remains synchronized with implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h

## Purpose

`xe_sriov_pf_service_types.h` defines persistent PF service ABI version state.

## Important APIs, Types, and Functions

`struct xe_sriov_pf_service_version` contains `major` and `minor`. `struct xe_sriov_pf_service` contains `version.base` and `version.latest`, representing the lowest and newest VF/PF ABI the PF can negotiate.

## Control Flow

These types are written during PF service init and read during handshakes and diagnostics. Per-VF metadata reuses `xe_sriov_pf_service_version` to record each VF's selected ABI.

## State and Persistence Behavior

The data persists in `struct xe_device_pf` for the PF lifetime. A zero per-VF version means disconnected or not negotiated.

## Dependencies and Integration Points

The type header depends on Linux integer types. It is embedded by `xe_sriov_pf_types.h` and consumed by PF service code and per-VF metadata.

## Risks and Test Signals

Width changes could affect ABI display and storage. Tests should verify initialization stores expected GuC relay constants and reset clears per-VF version fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_service_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c

## Purpose

`xe_sriov_pf_sysfs.c` builds the PF-admin sysfs tree under a PCI device for SR-IOV administration. It exposes bulk provisioning attributes, per-PF/per-VF profile attributes, VF control operations, and symlinks to PF/VF PCI devices.

## Important APIs, Types, and Functions

Internal wrappers `xe_sriov_kobj`, `xe_sriov_dev_attr`, and `xe_sriov_vf_attr` connect kobjects to `xe_device` and VF IDs. Bulk write-only attributes are `.bulk_profile/exec_quantum_ms`, `preempt_timeout_us`, `sched_priority`, and `vram_quota`. Per-function `profile/` attributes expose exec quantum, preempt timeout, scheduling priority, and VF VRAM quota. The VF control attribute `stop` maps to `xe_sriov_pf_control_stop_vf()`. Public functions are `xe_sriov_pf_sysfs_init()`, `xe_sriov_pf_sysfs_link_vfs()`, and `xe_sriov_pf_sysfs_unlink_vfs()`.

## Control Flow

Initialization creates `sriov_admin`, then child `pf` and `vfN` kobjects for every total VF, registers devm cleanup actions, and links `pf/device` to the PF device. Store paths acquire runtime PM, wait for PF readiness, parse the input, and call provisioning/control APIs. Visibility callbacks hide VRAM quota when LMTT is unavailable, hide or downgrade scheduling-priority write access for VFs, and hide control files for PF. VF link/unlink functions add or remove `device` symlinks only for enabled VFs.

## State and Persistence Behavior

The root kobject is stored in `xe->sriov.pf.sysfs.root`; per-function kobjects are stored in `xe->sriov.pf.vfs[n].kobj`. The sysfs files mutate persistent PF provisioning state and GT/tile resource assignments via the provisioning APIs. Kobjects are devm-managed with `kobject_put` cleanup.

## Dependencies and Integration Points

The file integrates Linux kobject/sysfs, DRM managed actions, Xe runtime PM, PCI SR-IOV VF lookup, PF readiness, PF control, PF provisioning, and SR-IOV logging. It is the user-visible administrative surface for PF resource shaping.

## Risks and Test Signals

Risks include partial VF symlink setup if PCI VF lookup fails mid-loop, user-visible permission mismatches for priority/VRAM on unsupported platforms, and race sensitivity around VF enable/disable versus sysfs writes. Tests should cover kobject tree creation, attribute visibility by platform/LMTT/VFID, parse failures, runtime-PM guarded writes, successful bulk/per-VF provisioning, and link/unlink idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h

## Purpose

`xe_sriov_pf_sysfs.h` declares the PF SR-IOV sysfs lifecycle and VF device-link helpers.

## Important APIs, Types, and Functions

`xe_sriov_pf_sysfs_init()` creates the `sriov_admin` tree. `xe_sriov_pf_sysfs_link_vfs()` creates `device` symlinks for enabled VFs. `xe_sriov_pf_sysfs_unlink_vfs()` removes those links.

## Control Flow

PF setup calls init once after PF metadata is available. VF enable paths call link for the enabled count; VF disable paths call unlink before or during teardown.

## State and Persistence Behavior

The functions update kobjects stored in PF metadata and create/remove sysfs links. The header owns no state.

## Dependencies and Integration Points

It forward-declares `struct xe_device` and is consumed by PF init and SR-IOV PCI enable/disable flows.

## Risks and Test Signals

The API assumes a PF device and valid VF counts. Tests should verify link removal matches link creation and that missing VF PCI devices are logged but do not corrupt the existing tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h

## Purpose

`xe_sriov_pf_types.h` defines the persistent per-PF and per-VF metadata embedded in `struct xe_device` when running as an SR-IOV Physical Function.

## Important APIs, Types, and Functions

`struct xe_sriov_metadata` stores a VF kobject, negotiated service version, and migration state. `struct xe_device_pf` stores PF mode flags, total/max VF counts, a guard for VF enabling, the PF master mutex, provisioning state, migration state, service version state, sysfs root, and the `vfs` metadata array.

## Control Flow

PF initialization allocates/fills this structure and its `vfs` array, initializes the master lock and service/provisioning state, then PF sysfs/debugfs/control/migration paths operate through these fields.

## State and Persistence Behavior

All fields persist for the PF device lifetime. `master_lock` serializes cross-GT VF configuration. `guard_vfs_enabling` protects enable flows. Per-VF kobjects and migration/service metadata remain indexed by VFID, with index zero representing PF metadata where used.

## Dependencies and Integration Points

The header includes guard, provisioning, service, and migration type headers and is included by Xe device SR-IOV mode-specific state. It is a central contract for PF provisioning, sysfs, VFIO migration, service negotiation, and control.

## Risks and Test Signals

Because many subsystems share this structure, layout or ownership changes can break teardown and reset paths. Tests should cover allocation/cleanup of `vfs`, master-lock use around provisioning, service reset on VF reset, and sysfs kobject lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h

## Purpose

`xe_sriov_printk.h` provides SR-IOV-aware logging macros that prepend PF/VF context to normal Xe driver messages.

## Important APIs, Types, and Functions

`xe_sriov_printk_prefix()` returns `PF: `, `VF: `, or an empty prefix from `xe->sriov.__mode`. Macros `xe_sriov_err`, `warn`, `notice`, `info`, and `dbg` wrap the corresponding Xe logging macros. `xe_sriov_dbg_verbose` compiles to debug logging only under `CONFIG_DRM_XE_DEBUG_SRIOV`; otherwise it type-checks the device pointer.

## Control Flow

Call sites use these macros exactly like normal Xe logging. The prefix is evaluated at log time from the device mode and merged into the format string.

## State and Persistence Behavior

There is no owned state. Output depends on persistent `xe->sriov.__mode`.

## Dependencies and Integration Points

It depends on `xe_printk.h` and is used throughout PF/VF SR-IOV provisioning, service, migration, and diagnostics.

## Risks and Test Signals

The macros assume a valid `struct xe_device *`. Format-string tests and compile coverage under both verbose-debug enabled and disabled configurations should catch type or variadic macro regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h

## Purpose

`xe_sriov_types.h` defines the common SR-IOV mode and function-ID constants shared by PF and VF code.

## Important APIs, Types, and Functions

`VFID(n)` represents the 1-based PCI VF identifier convention, and `PFID` aliases `VFID(0)`. `enum xe_sriov_mode` distinguishes bare-metal, PF, and VF modes, intentionally starting `XE_SRIOV_MODE_NONE` at one to catch premature zero-initialized checks.

## Control Flow

Mode probes set `xe->sriov.__mode` to one of these enum values. Helpers and logging macros then branch on PF versus VF mode. VFID/PFID values index PF metadata and drive sysfs/debugfs naming.

## State and Persistence Behavior

The header owns no state, but its constants define how persistent SR-IOV mode and per-VF arrays are interpreted.

## Dependencies and Integration Points

It only depends on build assertions. It is included broadly by PF, VF, logging, and tile SR-IOV code.

## Risks and Test Signals

Changing enum or ID values would break array indexing and mode checks. Tests should include early mode-probe behavior and boundary checks around VFID zero versus real VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c

## Purpose

`xe_sriov_vf.c` implements VF-side SR-IOV initialization, migration capability gating, migration-disable logging, and VF debugfs registration. It also contains the design documentation for VF restore and post-migration resource fixups.

## Important APIs, Types, and Functions

`xe_sriov_vf_migration_supported()` reports the inverse of the VF migration disabled flag. `xe_sriov_vf_migration_disable()` logs a formatted reason and permanently disables migration support for the VF. `xe_sriov_vf_init_early()` rejects migration when memory-based IRQs are missing. `xe_sriov_vf_init_late()` requires GuC ABI 1.27.0 or newer and initializes CCS support through `xe_sriov_vf_ccs_init()`. `xe_sriov_vf_debugfs_register()` registers `sa_info_vf_ccs`.

## Control Flow

Early init checks hardware prerequisites. Late init skips work if migration has already been disabled, reads GuC versions from the root MMIO GT, disables migration on too-old firmware, and otherwise initializes VF CCS save/restore helpers. Debugfs printing delegates to CCS printing.

## State and Persistence Behavior

The migration disabled flag lives in `xe->sriov.vf.migration.disabled`. Once set, later checks return unsupported and late CCS initialization is skipped. CCS initialization persists in `xe->sriov.vf.ccs`.

## Dependencies and Integration Points

The file integrates VF GT GuC version queries, memory IRQ capability, CCS migration code, SR-IOV logging, DRM debugfs, and DRM managed cleanup from CCS setup. The documented restore flow ties PF VFIO migration, GuC VF states, and VF post-migration recovery together.

## Risks and Test Signals

Risks include silent migration disable on missing prerequisites, dependency on exact GuC ABI thresholds, and debugfs output being empty when CCS is not initialized. Tests should cover memirq absence, GuC ABI below/above threshold, repeated disable calls, late init success/failure, and debugfs registration on VF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h

## Purpose

`xe_sriov_vf.h` declares the VF SR-IOV lifecycle, migration capability, and debugfs API.

## Important APIs, Types, and Functions

The header exposes `xe_sriov_vf_init_early()`, `xe_sriov_vf_init_late()`, `xe_sriov_vf_migration_supported()`, `xe_sriov_vf_migration_disable()`, and `xe_sriov_vf_debugfs_register()`.

## Control Flow

VF device initialization calls early then late init. Migration-capable code checks the supported helper before registering CCS or migration paths. Debugfs setup calls the registration function with the VF root dentry.

## State and Persistence Behavior

The APIs mutate or read `xe->sriov.vf` state, especially the migration disabled flag and CCS state initialized later.

## Dependencies and Integration Points

It depends on Linux types and forward declarations for `dentry` and `xe_device`. Consumers include VF probe/init, debugfs setup, and VF migration support code.

## Risks and Test Signals

Callers must only use these functions in VF mode. Build tests should catch signature drift and VF init tests should confirm early disable prevents late CCS setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c

## Purpose

`xe_sriov_vf_ccs.c` manages VF-side compression metadata (CCS) save/restore support for migration. It creates special migration execution queues/LRCAs, allocates batch-buffer pools, registers save/restore contexts with GuC, and attaches per-BO CCS copy commands.

## Important APIs, Types, and Functions

`xe_sriov_vf_ccs_init()` is the main setup path. `xe_sriov_vf_ccs_register_context()` re-registers save and restore contexts after runtime suspend. `xe_sriov_vf_ccs_rebase()` rewrites LRC rings after GGTT rebasing. `xe_sriov_vf_ccs_attach_bo()` and `xe_sriov_vf_ccs_detach_bo()` insert or clear CCS copy commands for BOs. `xe_sriov_vf_ccs_rw_update_bb_addr()` patches the batch-buffer address in the LRC. `xe_sriov_vf_ccs_print()` dumps pool state. Internal helpers compute pool size, allocate `xe_mem_pool`, reset LRC head/tail, and map context IDs to GuC compression save/restore types.

## Control Flow

Initialization runs only for VFs with migration enabled, integrated devices using flat CCS, and GuC ABI at least 1.23. For each read/write CCS context it creates a permanent kernel migrate queue, allocates and zeroes a BB pool sized from system memory and CCS ratio, writes an LRC ring pointing at the pool, registers the queue with GuC, and registers devm cleanup. BO attach loops over read/write contexts and calls `xe_migrate_ccs_rw_copy()`. Detach clears copy commands for valid CCS BBs.

## State and Persistence Behavior

Persistent VF CCS state is `xe->sriov.vf.ccs.contexts[]`, each holding context ID, migration queue, and CCS BB pool. `initialized` marks readiness. Cleanup sets ring tail to head before dropping the queue so GuC does not submit stale work after unbind.

## Dependencies and Integration Points

This file depends on MI/GPU command definitions, LRC ring helpers, exec queue creation and GuC registration, migration copy helpers, memory pools, runtime PM, VF migration gating, and BO `bb_ccs` bookkeeping. It is used by VF init, runtime resume, BO binding/unbinding, GGTT rebasing, and debugfs.

## Risks and Test Signals

The code has a documented workaround requiring LRC head zero for repeated migrations. Risks include oversized BB-pool memory use, partial initialization when one context succeeds and the other fails, stale BB addresses after GGTT movement, and attach continuing after an earlier context error. Tests should cover GuC version gating, non-flat-CCS no-op, successful read/write context registration, rebase ring contents, BO attach/detach idempotence, cleanup with GuC pause, and repeated migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h

## Purpose

`xe_sriov_vf_ccs.h` declares the VF CCS migration API and readiness helper.

## Important APIs, Types, and Functions

The header exposes CCS init, BO attach/detach, GuC context registration, GGTT rebase, debug printing, and LRC batch-buffer address update. `xe_sriov_vf_ccs_ready()` asserts VF mode and returns `xe->sriov.vf.ccs.initialized`. `IS_VF_CCS_READY()` combines SR-IOV VF mode and readiness.

## Control Flow

Callers use `IS_VF_CCS_READY()` to skip CCS operations on unsupported configurations. Runtime resume re-registers contexts, GGTT rebase updates rings, and BO paths attach/detach CCS copy command buffers.

## State and Persistence Behavior

The header accesses persistent VF CCS state embedded in `struct xe_device_vf`.

## Dependencies and Integration Points

It includes Xe device and SR-IOV headers plus CCS types. Integration points include BO code, migration code, VF init, runtime PM resume, and debugfs.

## Risks and Test Signals

Readiness checks must not be bypassed. Compile tests should cover all call sites under SR-IOV/VF and non-ready configurations; runtime tests should verify no CCS operation runs when `initialized` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h

## Purpose

`xe_sriov_vf_ccs_types.h` defines the persistent data structures for VF CCS migration contexts.

## Important APIs, Types, and Functions

`enum xe_sriov_vf_ccs_rw_ctxs` defines read/save and write/restore contexts plus count. `for_each_ccs_rw_ctx()` iterates both. `struct xe_sriov_vf_ccs_ctx` stores context ID, migration exec queue, and CCS BB pool. `struct xe_sriov_vf_ccs` stores the context array and initialization flag.

## Control Flow

Initialization fills each context and then sets `initialized`. Attach, detach, rebase, register, and print paths iterate contexts using the macro.

## State and Persistence Behavior

The structures persist in `xe->sriov.vf.ccs` for the VF lifetime and are cleaned via devm actions from initialization.

## Dependencies and Integration Points

The header uses Linux types and forward-declared struct names through included users. It is embedded by VF types and consumed by CCS implementation/header.

## Risks and Test Signals

The enum ordering is semantically tied to GuC save versus restore types and to BO `bb_ccs[]` indexing. Tests should verify both contexts are initialized and mapped to the correct GuC context type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h

## Purpose

`xe_sriov_vf_types.h` defines VF-mode persistent SR-IOV state embedded in `struct xe_device`.

## Important APIs, Types, and Functions

`struct xe_sriov_vf_relay_version` stores negotiated PF ABI major/minor. `struct xe_device_vf` stores `pf_version`, migration disabled state, and `struct xe_sriov_vf_ccs` CCS state.

## Control Flow

VF initialization fills or updates this state as the VF negotiates with the PF, checks migration prerequisites, and initializes CCS save/restore support.

## State and Persistence Behavior

All fields persist for the VF device lifetime. `migration.disabled` is sticky once prerequisites fail. `ccs.initialized` marks available CCS resources.

## Dependencies and Integration Points

The header includes workqueue types and CCS type definitions. It is the VF half of the SR-IOV union in device state and is consumed by VF init, relay, migration, and CCS code.

## Risks and Test Signals

Callers must only interpret this structure in VF mode. Tests should cover default zero initialization, PF version negotiation storage, migration disable persistence, and CCS state cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c

## Purpose

`xe_sriov_vfio.c` exports the narrow PF-facing API used by the external `xe-vfio-pci` module for VF migration and lifecycle control.

## Important APIs, Types, and Functions

`xe_sriov_vfio_get_pf()` maps a VF PCI device to the PF `xe_device`. `xe_sriov_vfio_migration_supported()` gates migration on PF mode and PF migration support. Macro-generated wrappers export wait-FLR, prepare-FLR, suspend/resume, stop-copy enter/exit, resume-data enter/exit, error/stop, and stop-copy-size functions. `xe_sriov_vfio_data_read()` and `xe_sriov_vfio_data_write()` transfer migration data through PF migration helpers.

## Control Flow

Every wrapper rejects non-PF devices with `-EPERM`, rejects `PFID` or VF IDs beyond currently enabled VFs with `-EINVAL`, takes a no-resume runtime PM guard, then calls the corresponding PF control or migration function.

## State and Persistence Behavior

The file owns no state. It orchestrates persistent PF migration/control state and migration data streams managed by the PF migration subsystem.

## Dependencies and Integration Points

It depends on the public DRM Intel Xe SR-IOV VFIO header, PCI PF lookup, runtime PM guards, PF control helpers, PF migration helpers, and module-scoped symbol exports for `xe-vfio-pci`.

## Risks and Test Signals

Risks include VF ID validation tied to currently enabled VF count, no-resume PM usage requiring callers to ensure power state expectations, and cross-module ABI drift. Tests should cover non-PF rejection, PFID rejection, out-of-range VF rejection, each wrapper mapping to the intended PF helper, and data read/write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c

## Purpose

`xe_step.c` maps PCI revision IDs and GMD_ID register revision fields to Xe symbolic graphics/media/platform/base-die steppings.

## Important APIs, Types, and Functions

Static revision tables cover Tiger Lake, DG1, Alder Lake variants, DG2 subplatforms, and PVC. `xe_step_platform_get()` sets platform stepping for platforms that need it. `xe_step_pre_gmdid_get()` maps legacy PCI revids and PVC base-die IDs. `xe_step_gmdid_get()` maps graphics/media GMD_ID revid fields directly. `xe_step_name()` converts enum values to strings and is exported for KUnit.

## Control Flow

For pre-GMD_ID platforms, the function selects a table based on platform/subplatform, splits PVC revid into base ID and die revid, looks up steppings, warns on gaps, advances to the next known revid when possible, and falls back to `STEP_FUTURE` if the value is beyond the table. GMD_ID platforms use `STEP_A0 + revid`, capped at `STEP_FUTURE`.

## State and Persistence Behavior

The functions write `xe->info.step.platform`, `graphics`, `media`, and `basedie`. These persist in device info and drive platform workaround checks.

## Dependencies and Integration Points

The file depends on platform/subplatform definitions, DRM logging, bitfield helpers, and KUnit visibility. It is called during PCI/device discovery before workaround and feature gating.

## Risks and Test Signals

Risks include missing new revid mappings, table holes producing conservative but possibly wrong steppings, and PVC base-die misclassification. Tests should exercise known table entries, gaps, future values, GMD_ID capping, PVC split fields, and `xe_step_name()` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h

## Purpose

`xe_step.h` declares the stepping lookup API and a GMD_ID conversion helper.

## Important APIs, Types, and Functions

It exposes `xe_step_platform_get()`, `xe_step_pre_gmdid_get()`, `xe_step_gmdid_get()`, `xe_step_to_gmdid()`, and `xe_step_name()`.

## Control Flow

Device discovery chooses either pre-GMD_ID or GMD_ID path and may call platform-level stepping first. Consumers use `xe_step_name()` for diagnostics and tests.

## State and Persistence Behavior

The APIs write fields in `xe->info.step`; the header owns no state. `xe_step_to_gmdid()` assumes enum values are spaced like GMD_ID stepping values.

## Dependencies and Integration Points

It includes `xe_step_types.h` and Linux types, and is used by device probe, workaround code, and tests.

## Risks and Test Signals

Enum spacing changes would break `xe_step_to_gmdid()`. Compile and KUnit tests should cover the conversion and exported name mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h

## Purpose

`xe_step_types.h` defines the symbolic stepping enum and storage struct used by platform stepping detection.

## Important APIs, Types, and Functions

`struct xe_step_info` stores platform, graphics, media, and base-die stepping bytes. `STEP_NAME_LIST()` enumerates minor steppings A0 through J3 in groups of four to match GMD_ID spacing. `enum xe_step` adds `STEP_NONE`, all symbolic steps, `STEP_FUTURE`, and `STEP_FOREVER`.

## Control Flow

Revision tables initialize `struct xe_step_info` entries using these enum values. `xe_step_gmdid_get()` depends on four-value spacing per major stepping.

## State and Persistence Behavior

The types are embedded in device info and persist for the device lifetime after probe.

## Dependencies and Integration Points

The header depends on Linux types and is consumed by step lookup, platform workaround checks, and diagnostics.

## Risks and Test Signals

Changing list order or spacing would affect GMD_ID conversion and comparison logic. Tests should assert enum ordering, string conversion, and `STEP_FUTURE` capping semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_step_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c

## Purpose

`xe_survivability_mode.c` implements boot and runtime survivability mode, a reduced driver mode for firmware recovery and telemetry when boot firmware or runtime firmware reaches a failed state.

## Important APIs, Types, and Functions

`xe_survivability_mode_is_requested()` checks platform support, configfs request state, and PCODE scratch boot status. `xe_survivability_mode_boot_enable()` enables boot survivability when requested. `xe_survivability_mode_runtime_enable()` creates survivability sysfs, marks the device wedged with vendor recovery, and tells userspace firmware flash is required. `xe_survivability_mode_is_boot_enabled()` reports active boot mode. Internal helpers populate scratch-register telemetry, expose sysfs attributes, initialize HECI GSC/VSEC/NVM/I2C services, and log critical boot data.

## Control Flow

Requested mode is limited to discrete, non-VF, Battlemage-or-newer devices. Boot enable reads PCODE breadcrumbs, rejects critical failures on breadcrumb versions before v2, sets type to boot, creates sysfs, marks `survivability->mode`, initializes recovery-capable auxiliary services, and optionally NVM when FDO mode is set. Runtime enable populates info, creates sysfs, sets type runtime, declares the device wedged, and returns success after notification.

## State and Persistence Behavior

`xe->survivability` stores scratch info, boot status, enabled mode, type, FDO mode, and breadcrumb version. Sysfs files persist until devm cleanup removes `survivability_mode`; the info group is devm-managed. Boot mode intentionally avoids full DRM card bring-up.

## Dependencies and Integration Points

The file integrates configfs, PCI/sysfs, MMIO PCODE scratch registers, HECI GSC, VSEC, NVM, I2C, pcode API bitfields, and Xe wedging notification.

## Risks and Test Signals

Risks include incorrect scratch linked-list traversal, sysfs creation failure leaving partial state, unsupported platform gating, and FDO/NVM init failure disabling mode. Tests should cover configfs request, PCODE critical/non-critical status, breadcrumb v1/v2 behavior, sysfs attribute visibility, runtime wedge signaling, and FDO mode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h

## Purpose

`xe_survivability_mode.h` declares the public survivability-mode control and query functions.

## Important APIs, Types, and Functions

The header exposes boot enable, runtime enable, boot-enabled query, and requested query functions.

## Control Flow

Probe code calls the requested/boot-enable path when normal initialization detects incomplete pcode or a manual configfs request. Runtime error handling calls runtime enable when firmware recovery requires a flash.

## State and Persistence Behavior

These functions read and mutate `xe->survivability` state and sysfs presence; the header owns no state.

## Dependencies and Integration Points

It depends on Linux types and forward-declares `struct xe_device`. It integrates with probe, wedging, and firmware recovery code.

## Risks and Test Signals

Callers must respect platform support and the reduced boot-mode lifecycle. Tests should verify unsupported platforms return false or `-EINVAL` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h

## Purpose

`xe_survivability_mode_types.h` defines the scratch-register identifiers and persistent survivability state.

## Important APIs, Types, and Functions

`enum scratch_reg` names capability, postcode trace, overflow, and auxiliary info registers. `enum xe_survivability_type` distinguishes boot and runtime. `struct xe_survivability` stores telemetry, scratch count, boot status, enabled flag, type, FDO mode, and breadcrumb version.

## Control Flow

The implementation reads PCODE scratch registers into `info[]`, sets `boot_status`, derives version/FDO bits, and uses `type` for sysfs display.

## State and Persistence Behavior

The struct persists in `struct xe_device` and represents current survivability state for sysfs and recovery flows.

## Dependencies and Integration Points

The header uses Linux integer limits/types and is included by survivability implementation and device state.

## Risks and Test Signals

The sysfs visibility code assumes `survivability_info_attrs[]` order matches `enum scratch_reg`. Tests should catch enum/order changes and version-gated FDO visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c

## Purpose

`xe_svm.c` implements Xe shared virtual memory over DRM GPU SVM and DRM pagemap. It handles CPU mmu-notifier invalidation, GPU page faults, VRAM migration, device-private page maps, TLB invalidation, and SVM range garbage collection.

## Important APIs, Types, and Functions

Lifecycle APIs are `xe_svm_init()`, `xe_svm_close()`, `xe_svm_fini()`, and `xe_svm_flush()`. Fault APIs include `xe_svm_handle_pagefault()`, `xe_svm_range_find_or_insert()`, `xe_svm_range_get_pages()`, `xe_svm_range_validate()`, `xe_svm_range_needs_migrate_to_vram()`, `xe_svm_alloc_vram()`, and `xe_svm_range_migrate_to_smem()`. Mapping helpers include `xe_svm_has_mapping()`, `xe_svm_unmap_address_range()`, `xe_svm_ranges_zap_ptes_in_range()`, `xe_vma_resolve_pagemap()`, and `xe_drm_pagemap_from_fd()`. Pagemap support creates `xe_pagemap`, implements device map/unmap, devmem population, migration copy callbacks, and pagemap cache/shrinker creation.

## Control Flow

In fault mode, init creates the garbage collector, acquires a pagemap owner peer, grabs local pagemaps for each VRAM tile, and initializes `drm_gpusvm` with range allocation/free/invalidate callbacks and 2M/64K/4K fault chunk sizes. MMU invalidation finds affected ranges, zaps PTEs per tile, records invalidated tile masks, submits TLB invalidation to all affected GTs, unmaps pages, and queues garbage collection for CPU unmaps. Page fault handling first drains garbage collection, resolves the target pagemap from VMA attributes and tile, finds or inserts a range, optionally migrates to VRAM, gets pages/DMA mappings, rebinds the range into the VM under validation exec, waits for the bind fence, and updates statistics. VRAM migration allocates DRM pagemap devmem pages, migrates CPU memory to device memory, and uses Xe migration queues to copy between SRAM and VRAM.

## State and Persistence Behavior

SVM state is embedded in `struct xe_vm`: a `drm_gpusvm`, notifier lock, garbage-collector list/work, peer owner, and per-tile pagemap references. Each `xe_svm_range` persists until removed and tracks tile-present and tile-invalidated masks. Device-private memory persists through `xe_pagemap` objects cached per VRAM region and reference-counted with DRM pagemap owners. Statistics accumulate in GT stats counters.

## Dependencies and Integration Points

This file integrates Linux MMU notifiers through DRM GPU SVM, DRM pagemap/devmem, PCI P2PDMA distance checks, Xe VM/VMA binding and validation, Xe PT zap/rebind, TLB invalidation batches, runtime PM, BO/TTM VRAM allocation, migration copy engines, page reclaim, and module SVM parameters.

## Risks and Test Signals

Risks include notifier-lock and VM-lock ordering, stale range masks if PTE zap succeeds but TLB invalidation fails, retry loops around VRAM migration and CPU VMA changes, deadlocks in reclaim paths, devmem lifetime/power references, P2P DMA mapping correctness, and unsupported 4K migration on 64K-only VRAM platforms. Tests should cover SVM init/close/fini, CPU unmap invalidation and garbage collection, valid fault fast path, CPU-to-VRAM and VRAM-to-CPU migration, devmem-only atomic faults, VMA autorestore/splitting, pagemap fd lookup, P2P mapping, and build behavior with `CONFIG_DRM_XE_PAGEMAP` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h

## Purpose

`xe_svm.h` declares the SVM, devmem pagemap, and SVM range API, with full implementations when `CONFIG_DRM_XE_GPUSVM` is enabled and stub fallbacks otherwise.

## Important APIs, Types, and Functions

With GPU SVM enabled, the header defines `struct xe_svm_range`, `struct xe_pagemap`, range helpers, lifecycle functions, pagefault handling, range migration/validation, PTE zap, pagemap resolution, pagemap shrinker/cache creation, and `xe_drm_pagemap_from_fd()`. It also defines interconnect protocol IDs for local VRAM and P2P. Without GPU SVM, it provides stub structures and no-op or error-returning inline functions.

## Control Flow

Callers can compile against a single interface regardless of config. Runtime paths use notifier lock helpers (`xe_svm_notifier_lock`, unlock, asserts) when DRM GPUSVM exists, and no-op lock helpers otherwise.

## State and Persistence Behavior

The full structs persist in VM and pagemap state. The fallback range struct preserves enough fields for code to compile but reports no valid pages/mappings.

## Dependencies and Integration Points

The full path depends on DRM GPU SVM, DRM pagemap, Xe VM, BO, GT, tile, VMA, and VRAM types. Integration points span VM fault handling, VMA memory attributes, device memory fd handling, and tile pagemap cache setup.

## Risks and Test Signals

The fallback signature for `xe_svm_range_validate()` differs semantically from the full declaration and should be watched during config-matrix builds. Tests should compile both GPUSVM/pagemap enabled and disabled configurations and exercise inline helpers for range boundaries and DMA mapping visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c

## Purpose

`xe_sync.c` parses user synchronization objects for Xe ioctls, creates dependencies, signals syncobjs/timeline syncobjs/user fences, and constructs input fences from queue/VM state.

## Important APIs, Types, and Functions

`xe_sync_entry_parse()` decodes `drm_xe_sync` entries. `xe_sync_entry_add_deps()` adds in-fence dependencies to scheduler jobs. `xe_sync_entry_wait()` and `xe_sync_needs_wait()` handle blocking waits. `xe_sync_entry_signal()` signals normal syncobj, timeline syncobj, or user fence outputs. `xe_sync_entry_cleanup()` releases references. `xe_sync_in_fence_get()` returns a queue/VM fence or fence array covering VM queues and TLB invalidation fences. User fence helpers manage `struct xe_user_fence` references and signaled status.

## Control Flow

Parse copies the uABI struct, rejects reserved flags, handles syncobj/timeline/user-fence types, validates LR mode restrictions and address alignment, looks up syncobjs, obtains input fences for wait entries, and preallocates chain fences for signal entries. User-fence signal paths add a timeline point to an internal syncobj, then register a dma-fence callback; on callback or already-signaled fence they queue ordered work to copy the value into the saved user address.

## State and Persistence Behavior

Each `xe_sync_entry` owns references to syncobjs, fences, chain fences, and optional user fence. `xe_user_fence` persists until callback work completes and all external references are dropped; it keeps an `mm_struct` reference and signaled flag.

## Dependencies and Integration Points

The file integrates DRM syncobj/timeline syncobj, dma-fence arrays/chains, scheduler jobs, Xe exec queues, Xe VMs, ordered workqueues, user access helpers, and queue last-fence/TLB-invalidation fence tracking.

## Risks and Test Signals

Risks include user fence writes after mm exit, missing cleanup on parse failures, LR mode signal restrictions, timeline seqno lookup failures, and fence-array reference leaks. Tests should cover all sync types, input versus signal paths, invalid flags/reserved fields, aligned/unaligned user fences, callback already-signaled path, cleanup idempotence, and VM queue fence aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h

## Purpose

`xe_sync.h` declares the Xe sync-entry API used by execution, VM bind, and wait paths.

## Important APIs, Types, and Functions

It defines parse flags for exec mode, long-running mode, and user-fence disallowance. It declares parse, dependency add, signal, wait, cleanup, input-fence aggregation, user-fence reference helpers, and `xe_sync_is_ufence()`.

## Control Flow

Ioctl handlers parse user sync entries, add dependencies to jobs, signal output syncs with the resulting fence, and clean entries after use. User-fence consumers can take references and poll signaled status.

## State and Persistence Behavior

The header exposes operations over `struct xe_sync_entry`, whose reference-owned members are released by cleanup.

## Dependencies and Integration Points

It includes sync types and forward declares DRM/Xe types. Integration points include exec ioctl, VM bind ioctl, scheduler jobs, and user fence wait/status paths.

## Risks and Test Signals

All parsed entries must eventually be cleaned. Tests should verify every parse success path has matching cleanup and that LR mode flags reject unsupported signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h

## Purpose

`xe_sync_types.h` defines the per-sync-entry state used while translating userspace sync objects into dma-fence operations.

## Important APIs, Types, and Functions

`struct xe_sync_entry` stores an optional DRM syncobj, input fence, timeline chain fence, user-fence chain fence, internal user-fence syncobj, `xe_user_fence`, user address, timeline values, type, and flags.

## Control Flow

Parsing fills the fields according to sync type and signal direction. Later dependency, wait, signal, and cleanup helpers consume the populated fields.

## State and Persistence Behavior

Entries are transient per ioctl/job submission. Reference fields must be released by `xe_sync_entry_cleanup()`.

## Dependencies and Integration Points

The header forward declares DRM syncobj, dma-fence, chain, uABI sync, and user fence types. It is consumed by the sync implementation and ioctl paths.

## Risks and Test Signals

Partially initialized entries on parse failure are a cleanup risk. Tests should exercise parse failure after each allocation point and confirm cleanup handles NULL fields safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sync_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c

## Purpose

`xe_tile.c` allocates and initializes per-tile Xe driver resources: GGTT, migration helpers, VRAM region structures, pagemap caches, sysfs, memory IRQs, and suballocation pools.

## Important APIs, Types, and Functions

`xe_tile_init_early()` stores the backpointer/ID, allocates GGTT and migration objects, and initializes PCODE state. `xe_tile_alloc_vram()` creates a tile VRAM region on discrete devices. `xe_tile_init_noalloc()` applies tile workarounds, creates pagemap cache, initializes TTM VRAM manager when needed, updates memory-region mask, and creates tile sysfs. `xe_tile_init()` initializes memory IRQs and kernel/reclaim suballocator pools. `xe_tile_migrate_wait()` waits on migration work. `xe_tile_local_pagemap()` returns an active local pagemap when pagemap support is enabled.

## Control Flow

Probe runs early init before hardware-dependent setup, allocates VRAM structs for DGFX, runs noalloc initialization before allocations that could disturb inherited display framebuffers, then runs full init for runtime resources.

## State and Persistence Behavior

Tile fields persist in `struct xe_tile`: `xe`, `id`, GGTT, migrate helper, VRAM/kernel VRAM, kernel BB pool, reclaim pool, memirq, pcode lock, sysfs kobject, debugfs dentry, SR-IOV tile state, and MERT state.

## Dependencies and Integration Points

The file integrates DRM managed allocation, GGTT, migration, PCODE, workarounds, tile sysfs, TTM VRAM manager, SVM pagemap caches, memory IRQs, suballocators, and VRAM region management.

## Risks and Test Signals

Risks include initialization ordering around display readout, memory-region mask updates, DGFX-only VRAM paths, and pagemap cache availability before SVM faults. Tests should cover single/multi-tile init order, allocation failure injection, DGFX versus integrated paths, noalloc behavior, and pagemap-enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h

## Purpose

`xe_tile.h` declares tile initialization and utility helpers.

## Important APIs, Types, and Functions

It exposes early/noalloc/full tile init, VRAM allocation, migration wait, root-tile check, `xe_tile_to_vr()`, and config-dependent `xe_tile_local_pagemap()`.

## Control Flow

Device probe and teardown use these APIs in staged order. SVM and migration code use local pagemap and migration wait helpers.

## State and Persistence Behavior

The APIs operate on persistent `struct xe_tile` state defined in `xe_tile_types.h`.

## Dependencies and Integration Points

It includes tile types and forward-declares device/pagemap types. It is consumed by probe, SVM, migration, debugfs, and platform setup code.

## Risks and Test Signals

Callers must not use full init before required allocation/noalloc stages. Build tests should cover pagemap enabled and disabled branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c

## Purpose

`xe_tile_debugfs.c` creates per-tile debugfs directories and reusable show callbacks for tile-specific debugfs files.

## Important APIs, Types, and Functions

`xe_tile_debugfs_simple_show()` resolves the tile from the parent dentry private pointer and invokes a printer function stored in `drm_info_list.data`. `xe_tile_debugfs_show_with_rpm()` wraps the simple show with runtime PM. `xe_tile_debugfs_register()` creates `tileN`, stores the tile pointer, adds VF-safe `ggtt` and `sa_info` files, and creates `vram_mm` resource-manager debugfs when VRAM exists.

## Control Flow

Debugfs registration runs per tile. File reads resolve `drm_info_node`, parent dentry, tile, and printer callback, then emit through a DRM seq-file printer.

## State and Persistence Behavior

`tile->debugfs` stores the directory dentry, and its inode private pointer stores the tile. Debugfs entries reflect live GGTT, suballocator, and TTM manager state.

## Dependencies and Integration Points

The file depends on Linux debugfs, DRM debugfs helpers, runtime PM, GGTT dump, suballocator dump, and TTM VRAM manager debugfs.

## Risks and Test Signals

Risks include dentry private pointer assumptions, missing runtime PM for future files that need hardware access, and debugfs creation errors being silently ignored. Tests should cover directory layout, file read callbacks, VF-safe file presence, and RPM acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h

## Purpose

`xe_tile_debugfs.h` declares the per-tile debugfs registration and reusable show callbacks.

## Important APIs, Types, and Functions

It exposes `xe_tile_debugfs_register()`, `xe_tile_debugfs_simple_show()`, and `xe_tile_debugfs_show_with_rpm()`.

## Control Flow

Tile debugfs setup calls register. Other tile-specific debugfs providers reuse the show callbacks with `drm_info_list.data` set to tile printer functions.

## State and Persistence Behavior

The functions operate on tile debugfs dentries and live tile state, but the header owns none.

## Dependencies and Integration Points

It forward-declares `seq_file` and `xe_tile`. It is reused by core tile debugfs and SR-IOV PF tile debugfs.

## Risks and Test Signals

Consumers must set dentry private data as expected by the implementation. Tests should read representative debugfs files and verify correct tile selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_printk.h

## Purpose

`xe_tile_printk.h` provides tile-prefixed logging, warning, and DRM printer helpers.

## Important APIs, Types, and Functions

Macros `xe_tile_err`, `warn`, `notice`, `info`, and `dbg` wrap Xe device logging with `Tile%u:` prefix. Warning macros add tile context to `xe_WARN` variants. Inline printer constructors return DRM printers that route to tile err/info/dbg logging functions.

## Control Flow

Tile-aware code logs through these macros or creates a printer for dump functions that should land in tile-specific logging.

## State and Persistence Behavior

No state is owned. Output depends on `tile->id` and `tile->xe`.

## Dependencies and Integration Points

It depends on `xe_printk.h` and DRM printer conventions. SR-IOV tile logging composes with these macros.

## Risks and Test Signals

The macros require valid tile pointers and can evaluate arguments in logging paths. Compile coverage should include warning/printer users and debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.c

## Purpose

`xe_tile_sriov_pf_debugfs.c` populates PF SR-IOV debugfs with per-tile quota and provisioning files for PF and VFs.

## Important APIs, Types, and Functions

`xe_tile_sriov_pf_debugfs_populate()` creates `tileN` under PF or VF debugfs directories. Read-only info files print available/provisioned GGTT and provisioned VRAM for PF. Debugfs attributes `ggtt_spare`/`ggtt_quota` and `vram_spare`/`vram_quota` are generated by `DEFINE_SRIOV_TILE_CONFIG_DEBUGFS_ATTRIBUTE()` and map to GT PF config getters/setters.

## Control Flow

Population validates parent private data, creates a tile directory with tile private data, adds quota attributes, adds PF-only summary files, and delegates GT-specific population for each GT on the tile. Setters take runtime PM, wait for PF readiness, apply the GT config, and switch provisioning to custom mode on success.

## State and Persistence Behavior

The debugfs files expose and mutate live GT PF configuration. Successful manual changes persist in backend config and mark PF provisioning mode custom.

## Dependencies and Integration Points

The file depends on debugfs, DRM debugfs, runtime PM, PF readiness, GT SR-IOV PF config/debugfs, tile debugfs callbacks, PF provisioning mode, and SR-IOV mode helpers.

## Risks and Test Signals

Risks include unsafe debugfs files operating on live PF state, overflow checks limited to target type width, and custom-mode transitions only after successful writes. Tests should cover PF versus VF directory layouts, DGFX/LMEM visibility, quota set/get, PF readiness failures, and GT delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h

## Purpose

`xe_tile_sriov_pf_debugfs.h` declares the PF SR-IOV per-tile debugfs population hook.

## Important APIs, Types, and Functions

The single public function is `xe_tile_sriov_pf_debugfs_populate(struct xe_tile *tile, struct dentry *parent, unsigned int vfid)`.

## Control Flow

PF SR-IOV debugfs setup calls this for every tile under the PF directory and under each VF directory.

## State and Persistence Behavior

The function creates debugfs dentries tied to live tile and VF configuration state. The header owns no state.

## Dependencies and Integration Points

It forward-declares `dentry` and `xe_tile` and is consumed by PF SR-IOV debugfs setup.

## Risks and Test Signals

Callers must pass a parent dentry with the private-data layout expected by the implementation. Debugfs layout tests should catch misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_pf_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h

## Purpose

`xe_tile_sriov_printk.h` composes tile-aware and SR-IOV-aware logging for messages that need both PF/VF and tile context.

## Important APIs, Types, and Functions

It defines tile SR-IOV print, err, notice, info, dbg, and verbose dbg macros. Messages are routed through `xe_sriov_*` logging while using the tile prefix format.

## Control Flow

Tile SR-IOV code calls these macros instead of raw tile or SR-IOV logging to include both contexts.

## State and Persistence Behavior

No state is owned. Logs depend on tile ID, device pointer, and SR-IOV mode.

## Dependencies and Integration Points

It includes `xe_tile_printk.h` and `xe_sriov_printk.h`. It is intended for tile-level PF/VF SR-IOV config and diagnostics.

## Risks and Test Signals

Macro composition can obscure format-string errors. Compile coverage under verbose debug enabled/disabled should validate calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c

## Purpose

`xe_tile_sriov_vf.c` stores and retrieves VF self-configuration for tile-local LMEM and GGTT assignment, including GGTT base needed after migration.

## Important APIs, Types, and Functions

The public getters/setters are `xe_tile_sriov_vf_lmem()`, `xe_tile_sriov_vf_lmem_store()`, `xe_tile_sriov_vf_ggtt()`, `xe_tile_sriov_vf_ggtt_store()`, `xe_tile_sriov_vf_ggtt_base()`, and `xe_tile_sriov_vf_ggtt_base_store()`.

## Control Flow

VF provisioning queries from GuC or PF/VF relay update the self config through store functions. Consumers read these values for GGTT sizing, LMEM sizing, and post-migration GGTT node rebasing.

## State and Persistence Behavior

Values persist in `tile->sriov.vf.self_config`. `ggtt_base` uses `READ_ONCE`/`WRITE_ONCE`, reflecting that it can be observed across recovery paths without heavier locking.

## Dependencies and Integration Points

The file integrates tile assertions, SR-IOV mode checks, GGTT/WOPCM layout concepts, and VF post-migration recovery. It includes GTT definitions and WOPCM headers for the documented GGTT layout context.

## Risks and Test Signals

Risks include stale GGTT base after migration, assuming identical total GGTT layout across source/destination, and using these helpers outside VF mode. Tests should cover store/get round trips, concurrent GGTT base reads, migration rebase flows, and VF-mode assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h

## Purpose

`xe_tile_sriov_vf.h` declares VF tile self-configuration accessors.

## Important APIs, Types, and Functions

It exposes getters and setters for VF GGTT size, GGTT base, and LMEM size.

## Control Flow

VF provisioning and migration recovery update values; GGTT/LMEM consumers read them through this interface.

## State and Persistence Behavior

The APIs operate on `tile->sriov.vf.self_config` persistent state.

## Dependencies and Integration Points

It depends on Linux types and forward-declares `xe_tile`. It is consumed by VF provisioning, GGTT setup, and migration fixup paths.

## Risks and Test Signals

Callers must pass VF-mode tiles. Tests should verify values survive across the relevant provisioning and recovery phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h

## Purpose

`xe_tile_sriov_vf_types.h` defines the VF per-tile self-configuration data.

## Important APIs, Types, and Functions

`struct xe_tile_sriov_vf_selfconfig` stores assigned GGTT base, GGTT size, and LMEM size.

## Control Flow

VF provisioning stores values after querying PF/GuC-assigned resources. Other VF code reads them for memory management and post-migration address fixups.

## State and Persistence Behavior

The struct is embedded in the VF arm of `struct xe_tile.sriov` and persists for the tile lifetime.

## Dependencies and Integration Points

It depends on Linux types and is included by tile types and VF tile helpers.

## Risks and Test Signals

Incorrect base/size values can corrupt GGTT rebasing or resource bounds. Tests should check initialization to zero and updates after provisioning query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c

## Purpose

`xe_tile_sysfs.c` creates a per-tile kobject under the PCI device and initializes tile-specific sysfs children such as VRAM frequency attributes.

## Important APIs, Types, and Functions

`xe_tile_sysfs_init()` allocates `struct kobj_tile`, initializes a kobject with `kobj_sysfs_ops`, adds it as `tile%d`, stores it in `tile->sysfs`, initializes VRAM frequency sysfs, and registers devm cleanup. Internal release and cleanup helpers free the wrapper and put the kobject.

## Control Flow

Tile noalloc initialization calls this after VRAM manager/pagemap cache setup. Error paths put the kobject, triggering release.

## State and Persistence Behavior

`tile->sysfs` persists until device-managed teardown. The wrapper stores a backpointer to the tile for child sysfs callbacks.

## Dependencies and Integration Points

The file depends on Linux kobject/sysfs, DRM managed cleanup, Xe runtime-related headers, tile types, and VRAM frequency sysfs.

## Risks and Test Signals

Risks include partial sysfs setup if VRAM frequency initialization fails and ensuring kobject lifetime matches tile lifetime. Tests should cover allocation failure, kobject add failure, VRAM freq failure, and `kobj_to_tile()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h

## Purpose

`xe_tile_sysfs.h` declares tile sysfs initialization and the kobject-to-tile helper.

## Important APIs, Types, and Functions

`xe_tile_sysfs_init()` creates per-tile sysfs state. `kobj_to_tile()` converts a tile kobject to its `struct xe_tile *` through `struct kobj_tile`.

## Control Flow

Tile init creates the kobject, and child sysfs callbacks use `kobj_to_tile()` to recover tile context.

## State and Persistence Behavior

The helper relies on a persistent `struct kobj_tile` wrapper allocated during init.

## Dependencies and Integration Points

It includes tile sysfs types and is consumed by tile setup and tile sysfs child modules.

## Risks and Test Signals

Using `kobj_to_tile()` on non-tile kobjects is invalid. Tests should read child attributes and verify the correct tile is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h

## Purpose

`xe_tile_sysfs_types.h` defines the kobject wrapper used by tile sysfs.

## Important APIs, Types, and Functions

`struct kobj_tile` contains the base kobject and a backpointer to the associated `struct xe_tile`.

## Control Flow

`xe_tile_sysfs_init()` allocates and initializes this wrapper. Sysfs callbacks recover the tile through `kobj_to_tile()`.

## State and Persistence Behavior

The wrapper persists for the lifetime of the tile sysfs kobject and is freed by its release callback.

## Dependencies and Integration Points

The header depends on Linux kobject and forward-declares `xe_tile`. It supports tile sysfs and child attribute modules.

## Risks and Test Signals

Kobject lifetime bugs can cause use-after-free in child sysfs callbacks. Tests should cover teardown while attributes exist and verify release frees the wrapper once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h

## Purpose

`xe_tile_types.h` defines `struct xe_tile`, the central per-tile hardware/software state container.

## Important APIs, Types, and Functions

The `tile_to_xe()` generic helper returns the parent device. `struct xe_tile` stores tile ID, parent Xe device, primary/media GTs, MMIO, memory substructure (kernel/user VRAM, GGTT, kernel BB pool, reclaim pool), SR-IOV PF LMTT or VF self-config union, memory IRQ state, CSC error work, PCODE lock, migration helper, sysfs kobject, debugfs dentry, and MERT data.

## Control Flow

Probe fills the structure in stages: early backpointer/ID/allocation, VRAM/noalloc setup, full runtime resource setup, then debugfs/sysfs and GT initialization.

## State and Persistence Behavior

The structure persists for the device lifetime and owns or references most per-tile resources. SR-IOV substate is mode-dependent: PF uses LMTT, VF uses self-config.

## Dependencies and Integration Points

The header includes MMIO, LMEM translation, memory IRQ, MERT, and VF tile SR-IOV types. It is included throughout GT, tile, VRAM, SVM, debugfs, sysfs, and SR-IOV code.

## Risks and Test Signals

Because this is shared state, ownership changes can affect many subsystems. Tests should cover multi-tile initialization, PF/VF union use, root versus remote tile behavior, and teardown ordering for sysfs/debugfs/migrate/VRAM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c

## Purpose

`xe_tlb_inval.c` implements the frontend for Xe TLB invalidation. It assigns sequence numbers, tracks pending invalidation fences, handles completion/timeout/reset, and submits all/GGTT/range invalidations to a backend such as GuC.

## Important APIs, Types, and Functions

`xe_gt_tlb_inval_init_early()` initializes per-GT invalidation state and wires the GuC backend. `xe_tlb_inval_all()`, `xe_tlb_inval_ggtt()`, `xe_tlb_inval_range()`, and `xe_tlb_inval_vm()` issue invalidations. `xe_tlb_inval_done_handler()` processes backend completion seqnos. `xe_tlb_inval_fence_init()` initializes stack or heap fences. `xe_tlb_inval_idle()`, `xe_tlb_inval_batch_wait()`, and `xe_tlb_inval_range_tilemask_submit()` support batching across tiles/GTs.

## Control Flow

Issuing takes `seqno_lock`, prepares a fence with the current seqno, queues it on `pending_fences`, schedules timeout work if needed, calls the backend op, signals the fence immediately on backend error, and advances seqno modulo `TLB_INVALIDATION_SEQNO_MAX`. Completion updates `seqno_recv`, signals pending fences in order, and updates/cancels timeout work. Timeout flushes the backend, marks expired fences `-ETIME`, and reschedules if pending fences remain. Reset signals all pending fences and advances received seqno to cover outstanding requests.

## State and Persistence Behavior

`struct xe_tlb_inval` persists per GT and stores backend private data, ops, seqno, received seqno, locks, pending fence list, delayed timeout work, job workqueue, and timeout workqueue. Each fence holds a runtime PM reference until signaled.

## Dependencies and Integration Points

The file depends on DRM managed cleanup, dma-fence, runtime PM, GuC TLB invalidation backend, GT stats/users, Xe tracepoints, forcewake/MMIO includes, and VM/SVM invalidation callers.

## Risks and Test Signals

Risks include seqno wrap ordering, timeout races with completion, stack versus heap fence lifetime, backend `-ECANCELED` handling, and reset during early backend init. Tests should cover seqno wrap, invalid completion seqno, timeout signaling, backend error signaling, GGTT synchronous wait, multi-tile range submit, reset with pending fences, and lockdep under reclaim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h

## Purpose

`xe_tlb_inval.h` declares the TLB invalidation frontend API and the inline fence wait helper.

## Important APIs, Types, and Functions

It exposes init, reset, all/GGTT/VM/range invalidation, fence initialization, completion handler, idle query, tile-mask range submit, batch wait, and `xe_tlb_inval_fence_wait()`.

## Control Flow

Backends call the done handler when firmware/hardware completes a seqno. VM/SVM and migration paths initialize fences, issue invalidations, and wait or batch-wait as needed.

## State and Persistence Behavior

The API operates on persistent `struct xe_tlb_inval` and transient `struct xe_tlb_inval_fence` or batch objects.

## Dependencies and Integration Points

It includes TLB invalidation types and forward-declares GT/GuC/VM. It is used by GT init, VM binds/unbinds, SVM notifier handling, and TLB invalidation jobs.

## Risks and Test Signals

Callers must initialize fences before issuing and must wait/drop according to stack/heap ownership. Tests should validate each public issue path and batch error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c

## Purpose

`xe_tlb_inval_job.c` wraps TLB invalidation in a dependency-scheduled job so invalidations can be ordered behind migration or bind work and represented by scheduler fences.

## Important APIs, Types, and Functions

`struct xe_tlb_inval_job` embeds `xe_dep_job`, TLB client, exec queue, VM, page reclaim list, refcount, invalidation fence, range, GT type, and armed flag. Public APIs create jobs, add page reclaim lists, preallocate dependency storage, push jobs, and manage references.

## Control Flow

Create allocates the job and heap invalidation fence, initializes scheduler job state, and takes queue/VM/runtime PM references. Push optionally swaps a preallocated stub dependency for a real unsignaled fence, arms the invalidation fence, locks migration job submission, pushes the scheduler job, records the scheduler finished fence as the queue's last TLB invalidation fence, and returns that finished fence. The run callback optionally builds a page reclaim list BO and issues range invalidation. Destruction frees PRL references, fence, scheduler job, queue/VM refs, and PM ref.

## State and Persistence Behavior

Jobs are reference-counted and live until scheduler completion and caller references are dropped. Page reclaim entries are copied into the job and retained until destroy. The invalidation fence is owned by the job until armed, then by dma-fence references.

## Dependencies and Integration Points

The file integrates dependency scheduler, DRM scheduler jobs, Xe exec queues, migration locking, page reclaim, TLB invalidation frontend, VM lifetime, runtime PM, and queue last-fence tracking.

## Risks and Test Signals

Risks include requiring `xe_tlb_inval_job_alloc_dep()` before pushing with an unsignaled fence in reclaim paths, PRL fallback to PPC flush when PRL BO creation fails, and lifetime split between scheduler finished fence and internal invalidation fence. Tests should cover dependency preallocation, signaled/unsignaled dependencies, PRL attach, destroy before arm, destroy after arm, and queue last-fence update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h

## Purpose

`xe_tlb_inval_job.h` declares the dependency-scheduled TLB invalidation job API.

## Important APIs, Types, and Functions

It exposes job creation, page reclaim list attachment, dependency preallocation, job push, and reference get/put operations.

## Control Flow

VM/migration code creates a job for a range, optionally embeds PRL data, preallocates dependency storage when needed, pushes the job behind a dependency fence, and drops references after use.

## State and Persistence Behavior

The opaque `xe_tlb_inval_job` object owns references described in the implementation until `xe_tlb_inval_job_put()` destroys it.

## Dependencies and Integration Points

It forward-declares dma-fence, dependency scheduler, exec queue, migrate, PRL, TLB invalidation, and VM types. It is consumed by VM bind/unbind and migration/reclaim paths.

## Risks and Test Signals

The create/push/get/put ownership contract is subtle. Tests should verify callers release creation references and that push returns a fence with a valid caller reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h

## Purpose

`xe_tlb_inval_types.h` defines backend operations, frontend state, invalidation fences, and invalidation batches.

## Important APIs, Types, and Functions

`struct xe_tlb_inval_ops` defines backend callbacks for all, GGTT, PPGTT/range, initialized, flush, and timeout delay. `struct xe_tlb_inval` stores backend private pointer, Xe device, ops, seqno state, locks, pending fence list, delayed timeout work, workqueues, and fence lock. `struct xe_tlb_inval_fence` wraps dma-fence with TLB client, list link, seqno, and invalidation time. `struct xe_tlb_inval_batch` stores one fence per possible GT across all tiles.

## Control Flow

The frontend uses ops to submit hardware/firmware invalidations and uses these state fields to track completion by seqno. Batch objects collect per-GT fences for tile-mask invalidations.

## State and Persistence Behavior

`xe_tlb_inval` persists per GT. Fences are transient per invalidation. Batches are caller-owned stack or embedded objects reset after wait.

## Dependencies and Integration Points

The header depends on workqueue and dma-fence types plus Xe device constants for maximum tile/GT count. Backends such as GuC must implement the ops contract.

## Risks and Test Signals

Backend ops must return `-ECANCELED` for mid-reset and provide correct timeout delays. Tests should validate backend/frontend contracts, pending list protection, and batch size coverage for maximum topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tlb_inval_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c

## Purpose

`xe_trace.c` instantiates Xe tracepoints by defining `CREATE_TRACE_POINTS` before including `xe_trace.h`.

## Important APIs, Types, and Functions

The file has no runtime functions of its own. Its key behavior is conditional inclusion outside sparse checker builds so tracepoint definitions are emitted in exactly one translation unit.

## Control Flow

During compilation, this translation unit expands tracepoint declarations from `xe_trace.h` into definitions. Other files include `xe_trace.h` only as declarations and call trace helpers such as TLB invalidation fence send/receive/signal tracepoints.

## State and Persistence Behavior

Tracepoint registration state is owned by the kernel tracing infrastructure. This file does not maintain driver state.

## Dependencies and Integration Points

It depends on `xe_trace.h` and integrates with all Xe code that emits tracepoints, including TLB invalidation and related GPU/VM paths.

## Risks and Test Signals

If this file is omitted from the build or another file also defines `CREATE_TRACE_POINTS`, tracepoints will fail to link or duplicate. Build tests and tracing smoke tests should verify Xe tracepoints are present and callable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace.c -->
