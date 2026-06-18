# Research Group subset-b-003776

Scope: GT SR-IOV PF/VF control, migration, monitoring, policy, debugfs, runtime service, stats, sysfs, and throttling files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/xe`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.c

Purpose: implements the PF-side GT SR-IOV VF control state machine. It drives pause, resume, stop, FLR, and migration save/restore sequencing for each VF by sending GuC control commands and reacting to GuC-to-PF event messages.

Important APIs and functions: exported entry points include `xe_gt_sriov_pf_control_init`, `xe_gt_sriov_pf_control_restart`, `xe_gt_sriov_pf_control_pause_vf`, `xe_gt_sriov_pf_control_resume_vf`, save/restore trigger/process/finish helpers, `xe_gt_sriov_pf_control_stop_vf`, FLR prepare/trigger/sync/wait helpers, and `xe_gt_sriov_pf_control_process_guc2pf`. Internal GuC command helpers wrap `GUC_ACTION_PF2GUC_VF_CONTROL` for PAUSE, RESUME, STOP, FLR_START, and FLR_FINISH.

Control flow: each VF owns a bitmap of `XE_GT_SRIOV_STATE_*` bits plus a completion. Top-level operations set a WIP bit and enqueue the VF on `gt->sriov.pf.control.list`; `control_worker_func` dispatches one queued VF at a time through `pf_process_vf_state_machine`. GuC `-EBUSY` responses requeue the same send state, `-EIO` is treated as command rejection/mismatch, and success advances the state machine. Pause and FLR wait for asynchronous GuC DONE events before completing. Stop and resume complete after accepted GuC control command responses. FLR progresses through start, GuC done, optional multi-GT sync, config/data/MMIO reset, finish command, and ready state.

State and persistence: state is volatile GT memory in `gt->sriov.pf.vfs[vfid].control.state`. `WIP` gates overlapping operations and `done` completes blocked callers. Restart after GT reset cancels the worker and returns all VFs to ready, clearing paused/stopped/saved/restored/mismatch and WIP-derived states. Save/restore state also owns and frees the migration packet ring through migration helpers.

Dependencies and integration: depends on GuC CT send/blocking APIs, GuC SR-IOV ABI definitions, PF config sanitization, PF migration packet helpers, monitor FLR reset, tile/device SR-IOV service synchronization, and PF migration waitqueues. It is called from debugfs control files, PCI SR-IOV control paths, migration uAPI orchestration, and GuC G2H dispatch.

Risks: the state machine is sensitive to out-of-order GuC events and races between command response and DONE notification, handled by entering WAIT_GUC before sending commands. Timeout constants are short for pause/FLR wait and longer for restore/config reset; slow firmware or heavy VRAM migration can surface as `-ETIMEDOUT` or `-EIO`. Mismatch bits are diagnostic but also mask failed states until a clean transition. Save/restore uses a small ring, so userspace must drain/fill promptly.

Test signals: exercise debugfs `control` commands, forced GuC busy/reject paths, FLR notification ordering, GT reset during WIP operations, migration save/restore with empty/full rings, and PVC multi-GT FLR dispatch. Logs from `xe_gt_sriov_dbg_verbose`, notices on FLR/save/restore failure, and completion timeout paths are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.h

Purpose: declares the PF GT SR-IOV control API used by PF provisioning, debugfs, migration, PCI FLR, and GuC event dispatch code.

Important APIs: exposes initialization/restart, pause/resume/stop, save and restore trigger/process/finish/status helpers, FLR prepare/trigger/sync/wait, and conditional `xe_gt_sriov_pf_control_process_guc2pf`. The GuC event function compiles to `-EPROTO` when PCI IOV is disabled.

Control flow: callers initiate operations through synchronous wrappers that generally start an asynchronous state machine then wait for completion, while migration producer/consumer paths use the process/check functions to drive work after ring state changes.

State and persistence: no state is stored in the header; it ties users to `struct xe_gt` and the state definitions in `xe_gt_sriov_pf_control_types.h`.

Dependencies and integration: includes Linux errno/types and forward-declares `struct xe_gt`. It is consumed by PF debugfs for manual stop/pause/resume, PF migration orchestration for save/restore, PCI SR-IOV FLR paths, and GuC event routing.

Risks: the API assumes PF-only callers and valid VFIDs; misuse is mostly caught by implementation asserts. The conditional stub can hide missing PCI IOV support unless callers handle `-EPROTO`.

Test signals: compile with and without `CONFIG_PCI_IOV`, verify all exported functions have matching implementations, and run PF control/migration tests through both debugfs and GuC event paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control_types.h

Purpose: defines PF-side GT SR-IOV control state bits and container structs used by `xe_gt_sriov_pf_control.c`.

Important types: `enum xe_gt_sriov_control_bits` enumerates WIP, FLR, pause, save, restore, resume, stop, terminal, failure, and mismatch bits. `struct xe_gt_sriov_control_state` stores the per-VF bitmap, completion, and queue link. `struct xe_gt_sriov_pf_control` stores the worker, pending list, and spinlock.

Control flow: the bit layout is the state-machine contract. `XE_GT_SRIOV_STATE_MISMATCH` must remain last because `XE_GT_SRIOV_NUM_STATES` is derived from it and controls bitmap sizing.

State and persistence: all state is in memory under `gt->sriov.pf.vfs[vfid].control` and `gt->sriov.pf.control`. Completion state is reinitialized per WIP operation; list membership is protected by the PF control spinlock.

Dependencies and integration: includes completion, spinlock, and workqueue type headers; embedded by `xe_gt_sriov_pf_types.h`.

Risks: adding states without updating debug string mapping or process ordering can create silent stuck states. Since state bits can coexist, callers must clear stale terminal/failure bits on successful transitions.

Test signals: build-time coverage for enum/string switch, debug logs that dump bitmaps, and stress tests for repeated queue/list movement under concurrent events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_control_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.c

Purpose: builds the PF SR-IOV debugfs hierarchy for PF and VF GT views. It exposes provisioning, policy, scheduler group, thresholds, manual control, runtime registers, adverse events, and debug-only config blob access.

Important APIs and functions: public functions are `xe_gt_sriov_pf_debugfs_populate` and `xe_gt_sriov_pf_debugfs_register`. Helpers extract `xe_gt`, `xe_device`, and VFID from dentry private data. Macro-generated file operations handle policy (`reset_engine`, `sched_if_idle`, `sample_period_ms`), quotas/config (`contexts_quota`, `doorbells_quota`, `exec_quantum_ms`, `preempt_timeout_us`, `sched_priority`), thresholds, scheduler group arrays, and `control`.

Control flow: `xe_gt_sriov_pf_debugfs_populate` creates `gt%u` directories under PF/VF SR-IOV trees and delegates to `pf_populate_gt`. PF entries get policy/config/info files; VF entries get VF quota/config, `control`, scheduler group config, and optional `config_blob`. `xe_gt_sriov_pf_debugfs_register` creates symlinks in ordinary GT debugfs back to the SR-IOV tree.

State and persistence: debugfs itself is volatile. Writes mutate PF policy/config state through runtime PM guards, usually setting custom provisioning mode after successful changes. `config_blob_open` snapshots serialized config into heap memory per open; write restores a user-provided blob up to 4 KiB.

Dependencies and integration: depends on DRM debugfs helpers, PF config/provision APIs, PF policy, monitor, service runtime, PF control, runtime PM, and scheduler group GuC ABI constants.

Risks: debugfs is privileged but exposes powerful controls that can pause/stop VFs and overwrite config blobs. Dentry-parent assumptions are strict; hierarchy changes must update extraction helpers. Scheduler group debugfs is registered before policy init can fully determine valid groups, so some files may exist but return unsupported errors. Array parsing and count limits protect but need careful ABI testing.

Test signals: enumerate PF/VF debugfs tree, read info files, write all policy/quota/threshold attributes, verify custom provisioning mode transition, use `control` stop/pause/resume, test scheduler group mode with active VFs and active MLRC queues, and test config blob round trips in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.h

Purpose: declares PF-specific GT SR-IOV debugfs registration and population entry points.

Important APIs: `xe_gt_sriov_pf_debugfs_register` adds symlinks from GT debugfs to the SR-IOV tree, and `xe_gt_sriov_pf_debugfs_populate` creates per-GT directories under PF/VF SR-IOV debugfs branches. When `CONFIG_PCI_IOV` is disabled, `register` becomes a no-op; no no-op is provided for `populate`.

Control flow: the header separates ordinary GT debugfs registration from SR-IOV hierarchy population.

State and persistence: no state is stored here; debugfs dentry private data and PF structures are managed in the implementation.

Dependencies and integration: forward-declares `struct xe_gt` and `struct dentry`; included by debugfs setup code.

Risks: callers must be gated correctly under PCI IOV for `populate`, since only `register` has a stub. Incorrect parent dentry layout will break implementation asserts.

Test signals: build with `CONFIG_PCI_IOV` enabled and disabled, and verify no unresolved references for debugfs setup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_helpers.h

Purpose: provides GT-scoped convenience wrappers around device-level SR-IOV PF helper APIs.

Important APIs: `xe_gt_sriov_pf_assert_vfid`, `xe_gt_sriov_pf_get_totalvfs`, and `xe_gt_sriov_pf_master_mutex`.

Control flow: inline wrappers derive `struct xe_device` from `struct xe_gt` and forward to device-level helpers.

State and persistence: no stored state; it centralizes access to total VF count and the master PF mutex used to serialize provisioning/policy operations.

Dependencies and integration: includes `xe_gt_types.h` and `xe_sriov_pf_helpers.h`. Used broadly across PF control, config, policy, monitor, debugfs, and migration code.

Risks: wrappers assume the GT belongs to a PF-capable device. Locking correctness depends on callers consistently using the returned master mutex for shared PF state.

Test signals: compile-time inlining, debug assertions for invalid VFIDs, and lockdep coverage around PF policy/config updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.c

Purpose: implements PF-side per-GT VF migration packet production and restoration. It saves/restores GGTT, GuC firmware state, MMIO software flags, and VRAM into `xe_sriov_packet` records exchanged with userspace through a small per-VF ring.

Important APIs and functions: exported helpers include init, component save/restore for GuC/GGTT/MMIO/VRAM, `xe_gt_sriov_pf_migration_size`, ring empty/full/free, save bitmap init/pending/complete, and save/restore produce/consume functions. Internal helpers issue `GUC_ACTION_PF2GUC_SAVE_RESTORE_VF`, snapshot VF GGTT config, read/write VF SW flag MMIO through a VF view, and copy VRAM chunks with `xe_migrate_vram_copy_chunk`.

Control flow: save initialization resets `data_remaining` and VRAM offset, then marks required packet types. PF control repeatedly calls component save functions in GuC, GGTT, MMIO, VRAM order. Each save allocates a packet, fills header/body, and produces it to the ring; VRAM returns `-EAGAIN` until all 512 MiB chunks are emitted. Restore consumes packets from the ring and dispatches by packet type.

State and persistence: per-VF `struct xe_gt_sriov_migration_data` stores a `ptr_ring`, save bitmap, and VRAM offset. Data packets own BO-backed buffers and are freed on consume, failure, cleanup action, or ring flush. Migration support is disabled globally if GuC firmware is older than 70.54.0.

Dependencies and integration: used by PF control save/restore state machines and higher-level `xe_sriov_pf_migration.c` userspace orchestration. Depends on PF config for GGTT/LMEM objects, GuC buffers and CT, packet helpers, MMIO VF view, migrate copy fences, DRM exec locking, and PF migration waitqueues.

Risks: ring size is only five packets, so backpressure is expected. VRAM copy timeout is 5 seconds per chunk and chunk size is 512 MiB. Restore validates VRAM bounds but packet ordering is effectively controlled by the producer. GuC state sizing is queried dynamically but a header TODO still defines an 8 MiB maximum constant elsewhere. Failure paths must free packets exactly once.

Test signals: save/restore with and without LMEM, multi-chunk VRAM migration, ring full/empty wakeups, invalid packet sizes/offsets, old GuC firmware support disabling, and fault injection for BO allocation, GuC buffer allocation, CT errors, fence timeout, and interrupted wait events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.h

Purpose: declares PF GT-level VF migration helpers and the ring interface between PF control and higher-level migration code.

Important APIs: component save/restore functions for GuC, GGTT, MMIO, VRAM; total size query; ring empty/full/free; save initialization and bitmap helpers; save producer/consumer; restore producer/consumer. Defines `XE_GT_SRIOV_PF_MIGRATION_GUC_DATA_MAX_SIZE` as an 8 MiB TODO-backed upper bound.

Control flow: callers start with `xe_gt_sriov_pf_migration_init`, then `save_init`, then query pending component types and produce packets; restore paths push packets into the ring and notify control processing.

State and persistence: no state in the header, but the API exposes ownership-sensitive `struct xe_sriov_packet *` flows where producers hand packets to rings and consumers must free them.

Dependencies and integration: forward-declares `struct xe_gt`, `struct xe_sriov_packet`, and packet type enum. Used by PF control and device-level migration uAPI code.

Risks: the API mixes synchronous component operations with asynchronous ring backpressure. Misinterpreting `NULL`, `ERR_PTR(-EAGAIN)`, and real packet returns from `save_consume` can break userspace migration loops.

Test signals: compile contract against PF control and migration orchestrator, plus packet ownership tests for all return-value cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration_types.h

Purpose: defines the per-GT, per-VF PF migration state embedded in VF metadata.

Important type: `struct xe_gt_sriov_migration_data` contains a `ptr_ring` for migration packets and a nested save state with `data_remaining` bitmap and `vram_offset`.

Control flow: PF control checks ring full/empty states to enter WAIT_DATA bits; migration save logic uses `data_remaining` to decide which packet type to emit next and `vram_offset` to continue chunked VRAM saves.

State and persistence: all state is volatile and per VF. Ring cleanup is registered during PF migration init and frees unprocessed packet objects.

Dependencies and integration: includes Linux `ptr_ring`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: `data_remaining` uses packet type values as bit positions, so packet enum changes must remain compatible. `vram_offset` must reset at save start to avoid skipped chunks.

Test signals: migration save restart, ring cleanup on driver teardown, and large LMEM tests that advance `vram_offset` across multiple chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_migration_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.c

Purpose: tracks PF-side adverse threshold events reported by GuC for PF/VF functions and resets per-VF counters on FLR.

Important APIs and functions: `xe_gt_sriov_pf_monitor_flr`, `xe_gt_sriov_pf_monitor_process_guc2pf`, and `xe_gt_sriov_pf_monitor_print_events`. Internal helpers map threshold KLV keys to indexes and increment `monitor.guc.events`.

Control flow: GuC adverse event messages are validated for origin/type/action, MBZ fields, length, VFID range, and threshold key. Valid events increment the corresponding counter and log threshold exceedance with the configured threshold value. FLR zeroes all counters for the VF.

State and persistence: per-VF counters live in `gt->sriov.pf.vfs[vfid].monitor.guc.events`; they are volatile and reset on FLR or driver unload.

Dependencies and integration: depends on GuC message ABI, KLV threshold helpers, PF config threshold getters, PF helpers, and SR-IOV logging. Debugfs exposes counters through `adverse_events`.

Risks: unknown threshold keys return `-ENOTCONN`, which may indicate ABI drift. Counters are plain integers and not protected by a lock; event dispatch serialization is assumed by the GuC event handling path.

Test signals: inject/observe GuC adverse events for every threshold, verify debugfs output hides empty VFs unless debug SR-IOV is enabled, test invalid MBZ/length/VFID/key handling, and confirm FLR clears counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.h

Purpose: declares PF adverse-event monitor APIs for FLR cleanup, GuC event dispatch, and debug printing.

Important APIs: `xe_gt_sriov_pf_monitor_flr`, `xe_gt_sriov_pf_monitor_print_events`, and conditional `xe_gt_sriov_pf_monitor_process_guc2pf`; the latter returns `-EPROTO` when PCI IOV is disabled.

Control flow: PF control calls FLR cleanup after VF reset data cleanup; GuC event dispatch calls `process_guc2pf`; debugfs calls print.

State and persistence: no state in the header; state is defined by `xe_gt_sriov_pf_monitor_types.h`.

Dependencies and integration: forward-declares `struct xe_gt` and `struct drm_printer`.

Risks: callers must treat the no-IOV stub as unsupported rather than a transient parse failure.

Test signals: build both PCI IOV configurations and route adverse event messages through the PF GuC event multiplexer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor_types.h

Purpose: defines per-VF PF monitoring storage for GuC adverse events.

Important type: `struct xe_gt_sriov_monitor` contains `guc.events[XE_GUC_KLV_NUM_THRESHOLDS]`, one counter per configured GuC threshold.

Control flow: event indexes come from `xe_guc_klv_threshold_key_to_index`; debug printing uses the same threshold set macro to name fields.

State and persistence: counters are volatile per-VF state, reset by FLR and initialized with VF metadata allocation.

Dependencies and integration: includes `xe_guc_klv_thresholds_set_types.h`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: threshold set macro changes must keep the array size and printer mappings consistent.

Test signals: compile with new threshold definitions and verify array bounds with all generated threshold attributes/events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.c

Purpose: manages PF GT SR-IOV GuC policies, including scheduling-if-idle, reset-after-VF-switch, adverse event sample period, and scheduler group mode provisioning.

Important APIs and functions: public setters/getters for `sched_if_idle`, `reset_engine`, `sample_period`, scheduler group support/mode/enabled checks, `xe_gt_sriov_pf_policy_init`, `sanitize`, `reprovision`, and `print`. Internal helpers build GuC KLV payloads and send `GUC_ACTION_PF2GUC_UPDATE_VGT_POLICY`.

Control flow: setters take the PF master mutex, push a KLV to GuC, and update cached policy only on success. Reprovision optionally resets cached policy to defaults, then pushes all policy KLVs with runtime PM held. Scheduler group init computes supported media-slice grouping modes from hardware engines and GuC/platform capability. Scheduler group mode changes are rejected if VFs are active or MLRC queues are registered.

State and persistence: cached policy lives in `gt->sriov.pf.policy.guc`. Scheduler group mode data stores max group count, supported mode mask, current mode, and per-mode group arrays allocated with DRM managed memory.

Dependencies and integration: depends on GuC KLV helpers/ABI, GuC CT/buffer APIs, hardware engine iteration, runtime PM, GuC submit MLRC state, PF master mutex, and debugfs/provisioning callers.

Risks: `err |= ...` in reprovision compresses multiple failures into `-ENXIO`, which loses detail. Scheduler group support is hardcoded to max two groups pending firmware query support. Media-slice grouping is intentionally disabled for post-Battlemage platforms. Policy setters update cached state only after firmware success, so reset/sanitize/reprovision ordering matters.

Test signals: KLV count mismatch handling, firmware rejection paths, debugfs writes, reprovision after GT reset, scheduler group mode switching before/after enabling VFs, active MLRC rejection, and media GT grouping on BMG-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.h

Purpose: declares the PF GT SR-IOV policy API and scheduler group mode helpers.

Important APIs: policy setters/getters for scheduler-if-idle, reset-engine, sample period; scheduler group support, mode support, mode set, and enabled checks; init/sanitize/reprovision/print.

Control flow: callers use setters for live updates, `sanitize` to reset cached policy, and `reprovision` after reset or when pushing cached/default values to GuC.

State and persistence: no state in the header; state is in `struct xe_gt_sriov_pf_policy` from the types header.

Dependencies and integration: includes `xe_gt_sriov_pf_policy_types.h`; used by PF debugfs, provisioning, and PF GT init/reset flows.

Risks: callers must hold no conflicting locks before setters because implementation takes the PF master mutex and runtime PM in reprovision.

Test signals: compile API coverage and lockdep during debugfs/provisioning updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy_types.h

Purpose: defines PF policy storage and scheduler group mode structures.

Important types: `enum xe_sriov_sched_group_modes` currently supports disabled and media-slices. `struct xe_gt_sriov_scheduler_groups` tracks max groups, supported mode mask, current mode, and per-mode `guc_sched_group` arrays. `struct xe_gt_sriov_guc_policies` stores boolean/u32 GuC policies plus scheduler groups. `struct xe_gt_sriov_pf_policy` wraps GuC policies.

Control flow: mode arrays are populated during policy init and consumed by provisioning and debugfs.

State and persistence: policy is volatile cached driver state mirrored to GuC by KLV updates; scheduler group arrays are DRM-managed allocations.

Dependencies and integration: includes GuC scheduler ABI for `GUC_MAX_ENGINE_CLASSES` and `struct guc_sched_group`.

Risks: adding enum modes requires updating mode string conversion, debugfs parser, init switch, and KLV provisioning behavior.

Test signals: compile with exhaustive enum switch warnings, debugfs mode listing, and KLV payload size validation for each mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_policy_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.c

Purpose: implements PF GT-level services consumed by VFs over GuC relay: ABI handshake and runtime register query. It also snapshots platform-specific runtime registers that VFs cannot read directly.

Important APIs and functions: public `xe_gt_sriov_pf_service_init`, `xe_gt_sriov_pf_service_update`, `xe_gt_sriov_pf_service_process_request`, and `xe_gt_sriov_pf_service_print_runtime`. Internal register tables select runtime registers by graphics version/platform. Message handlers process `GUC_RELAY_ACTION_VF2PF_HANDSHAKE` and `GUC_RELAY_ACTION_VF2PF_QUERY_RUNTIME`.

Control flow: init allocates the runtime value array and stores a static register table. Update reads all runtime registers from PF MMIO. Handshake validates message length/MBZ and delegates global VF/PF version negotiation to device-level service code. Runtime query validates negotiated ABI >= 1.0, supports chunked reads with start/limit, and writes offset/value pairs to the response.

State and persistence: runtime register state lives in `gt->sriov.pf.service.runtime` with static `regs`, DRM-managed `values`, and count. Values persist until refreshed by `service_update`.

Dependencies and integration: depends on GuC relay ABI, HxG helpers, MMIO register definitions, PF service version negotiation, SR-IOV logging, and debugfs runtime printing. VF-side code uses the matching query protocol to cache inaccessible register values.

Risks: runtime register table selection must match platforms and VF expectations. Values can become stale if not refreshed after hardware state changes. Runtime query response sizing is in dwords and packed `reg_data` units; malformed limits or ABI drift can cause protocol errors.

Test signals: VF/PF ABI handshake, chunked runtime query with small response buffers, unsupported graphics version returning `-ENOPKG`, debugfs runtime dump, and comparing VF cached reads against PF snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.h

Purpose: declares PF GT SR-IOV relay service APIs for initialization, runtime refresh/printing, and VF request processing.

Important APIs: `xe_gt_sriov_pf_service_init`, `xe_gt_sriov_pf_service_update`, `xe_gt_sriov_pf_service_print_runtime`, and conditional `xe_gt_sriov_pf_service_process_request` with a `-EPROTO` stub when PCI IOV is disabled.

Control flow: PF GT init calls init, lifecycle/update paths call update after registers are valid, GuC relay dispatch calls process_request, and debugfs calls print.

State and persistence: state is defined in `xe_gt_sriov_pf_service_types.h`.

Dependencies and integration: forward-declares `struct xe_gt` and `struct drm_printer`; includes Linux errno/types.

Risks: request processing must be gated to PF devices and PCI IOV builds; callers need to size response buffers according to GuC relay ABI.

Test signals: no-IOV build stubs, relay request dispatch with invalid action/length, and runtime debugfs output after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service_types.h

Purpose: defines PF GT SR-IOV service state for ABI version metadata and runtime register snapshots.

Important types: `struct xe_gt_sriov_pf_service_version` stores major/minor VF/PF ABI values. `struct xe_gt_sriov_pf_service_runtime_regs` stores selected register descriptors, captured values, and count. `struct xe_gt_sriov_pf_service` combines base/latest versions and runtime data.

Control flow: service init fills runtime table/value storage; service update refreshes values; relay response code reads version/runtime fields.

State and persistence: runtime values are cached in memory and are not persistent across driver reload. Version fields are part of PF service state but global negotiation is also coordinated by device-level service code.

Dependencies and integration: forward-declares `struct xe_reg`; embedded in `xe_gt_sriov_pf_types.h`.

Risks: `regs` points to static arrays owned by the implementation, while `values` is allocated; lifetime assumptions must remain valid for the GT lifetime.

Test signals: init/fini lifetime checks, runtime value allocation failure, and response queries after repeated updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_service_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_types.h

Purpose: aggregates all GT-level PF SR-IOV state into metadata structures embedded in `struct xe_gt`.

Important types: `struct xe_gt_sriov_metadata` stores per-VF config, monitor, control, negotiated VF/PF version, and migration data. `struct xe_gt_sriov_pf_workers` currently stores the restart worker. `struct xe_gt_sriov_pf` stores workers, service, control, policy, spare PF config, and an array of per-VF metadata.

Control flow: per-VF metadata is indexed by VFID, with VFID 0 representing PF in several paths. Control code relies on pointer arithmetic from `control` back to the metadata array to recover VFID.

State and persistence: all fields are in-memory driver state, initialized by PF GT setup and reset/sanitized by lifecycle paths. `vfs` is the core per-VF backing store.

Dependencies and integration: includes PF config, control, migration, monitor, policy, and service type headers.

Risks: layout coupling matters because `container_of(... control)` and array index math assume every `control` belongs to `gt->sriov.pf.vfs`. Any allocation/count bug in `vfs` affects all PF subsystems.

Test signals: PF init allocation for total VFs plus PFID, VFID indexing assertions, restart worker teardown, and migration/control operations over first/last VFIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_printk.h

Purpose: provides GT-scoped SR-IOV logging macros that include tile and GT context in messages.

Important APIs: `xe_gt_sriov_err`, `notice`, `info`, `dbg`, and `dbg_verbose`. Verbose debug compiles to real debug output only under `CONFIG_DRM_XE_DEBUG_SRIOV`; otherwise it typechecks the GT pointer without emitting code.

Control flow: macros format messages through tile and GT print helpers before forwarding to device-level `xe_sriov_*` log macros.

State and persistence: no state; it standardizes log prefixes for PF/VF SR-IOV code.

Dependencies and integration: includes `xe_gt_printk.h` and `xe_tile_sriov_printk.h`. Used throughout PF/VF control, migration, policy, monitor, and service files.

Risks: macro arguments must be side-effect safe, especially for verbose logs that compile out. Format nesting must stay compatible with tile/device logging macros.

Test signals: build with and without debug SR-IOV, verify log prefixes include PF/VF mode, tile, and GT identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.c

Purpose: implements VF-side GT SR-IOV bootstrap, GuC ABI negotiation, VF config/resource query, PF relay handshake/runtime query, inaccessible register emulation, and post-migration recovery.

Important APIs and functions: exports `xe_gt_sriov_vf_reset`, `bootstrap`, `guc_versions`, `query_config`, `connect`, `query_runtime`, migration event/init/recovery checks, `gmdid`, `guc_ids`, scheduler group status, `read32`/`write32`, debug printers, `wait_valid_ggtt`, and fixup count. Internal helpers send VF2GUC reset/version/KLV/resfix messages and VF2PF relay handshake/runtime requests.

Control flow: bootstrap resets GuC VF state and negotiates a stable GuC interface version. Config query reads GGTT start/size, LMEM size, submission CTX/doorbell quotas, scheduler group availability, and GMDID through GuC KLVs; GGTT base changes shift existing GGTT nodes. PF connection negotiates relay ABI, then runtime query fetches PF-owned register snapshots in chunks. `read32` serves inaccessible registers from cached runtime data or GMDID.

State and persistence: state lives in `gt->sriov.vf`: wanted/found GuC versions, self_config, runtime register cache, scheduler group flag, GMDID, and migration recovery state. Runtime regs are DRM-managed and resized as PF reports different counts. Migration state has a scratch buffer, worker, waitqueue, spinlock, queued/inprogress/teardown flags, `ggtt_need_fixes`, marker, debug stoppers, and atomic fixup count.

Migration recovery: on migrated event, the VF marks recovery pending, wakes CT waiters, queues ordered work, flushes/stops CT, pauses GuC submit, resets TLB invalidation, sends RESFIX_START, requeries config, rebases CCS/default LRC HWSP/GuC contexts, marks GGTT fixups done, resumes IRQ/CT/submission, sends RESFIX_DONE, then kickstarts jobs. Failures abort submission pause and wedge the device; shared-GT ordering can requeue media recovery behind primary GT recovery.

Dependencies and integration: depends on GuC MMIO communication, GuC relay, KLV ABI, GGTT/tile VF storage, LMEM, IRQ, memirq, GuC CT/submit, LRC, CCS rebase, TLB invalidation, WOPCM, runtime PF service, and debugfs.

Risks: version changes after prior handshake return `-EREMCHG`. Resource reassignment checks reject changed GGTT/LMEM/CTX/doorbell sizes except GGTT base shifting. Migration recovery assumes memirq for immediate pending detection and can wedge on failed fixups. Runtime register cache must be sorted as supplied by PF for `bsearch`. `xe_gt_sriov_vf_lmem` is declared in the header but not implemented in this file, so consumers rely on another definition or risk link failure.

Test signals: VF bootstrap across platform version baselines, GuC KLV query failures, GGTT base migration, PF ABI/runtime chunk query, inaccessible register read/write debug warnings, migration recovery success/failure/requeue with debug `resfix_stoppers`, and waiters using `xe_gt_sriov_vf_wait_valid_ggtt`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.h

Purpose: declares the VF-side GT SR-IOV API for bootstrap/config/runtime, migration recovery, register emulation, and debug printing.

Important APIs: reset/bootstrap/version query, config query, PF connect, runtime query, migrated event handler, init early/init, recovery pending, GMDID/GUC IDs/LMEM/scheduler group accessors, read32/write32, config/runtime/version printers, wait valid GGTT, and fixup completion count.

Control flow: the expected VF lifecycle is early migration init, GuC bootstrap, config query, PF connect, runtime query, regular register access, and migration recovery handling after migrated events.

State and persistence: no state in the header; state is defined in `xe_gt_sriov_vf_types.h`.

Dependencies and integration: forward-declares GT, register, printer, and firmware version types. Used by VF debugfs, MMIO helpers, CCS/migration, GuC init, and query paths.

Risks: `xe_gt_sriov_vf_lmem` is declared but not implemented in the researched `.c` file, which should be checked against the broader tree. Callers must only use VF APIs on VF devices after required negotiation.

Test signals: link check for all declarations, VF-only assertions, and lifecycle ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.c

Purpose: registers VF-specific GT debugfs entries under each GT directory.

Important APIs and functions: `xe_gt_sriov_vf_debugfs_register` creates a `vf` directory and DRM info files for `self_config`, `abi_versions`, and optionally `runtime_regs`. In debug builds it also exposes writable `resfix_stoppers` for migration recovery delay injection.

Control flow: registration asserts VF mode and GT dentry private data, creates `vf`, assigns GT private data, then creates info files backed by VF printer functions.

State and persistence: debugfs entries are volatile. `resfix_stoppers` directly mutates `gt->sriov.vf.migration.debug.resfix_stoppers`, affecting recovery worker wait injection.

Dependencies and integration: depends on DRM debugfs, GT debugfs simple show helper, VF printers, GT types, and SR-IOV mode checks.

Risks: `resfix_stoppers` can intentionally stall migration recovery in debug kernels. Runtime regs are hidden unless debug or debug SR-IOV is enabled.

Test signals: VF debugfs tree enumeration, output of self config/version/runtime files after negotiation, and controlled migration recovery stalls using `resfix_stoppers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.h

Purpose: declares VF GT debugfs registration.

Important API: `xe_gt_sriov_vf_debugfs_register(struct xe_gt *gt, struct dentry *root)`.

Control flow: GT debugfs setup calls this for VF devices to add the `vf` subtree.

State and persistence: no state in the header.

Dependencies and integration: forward-declares GT and dentry types; implemented unconditionally with VF assertions.

Risks: no compile-time stub is provided, so build integration must avoid calling it in non-debugfs contexts only if the rest of debugfs code is absent.

Test signals: compile and VF debugfs registration smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_types.h

Purpose: defines GT-level VF SR-IOV state structures.

Important types: `xe_gt_sriov_vf_selfconfig` stores assigned GuC contexts and doorbells. `xe_gt_sriov_vf_runtime` stores GMDID, scheduler group flag, and PF-provided runtime register offset/value array. `xe_gt_sriov_vf_migration` stores recovery worker, lock, waitqueue, scratch buffer, fixup counter, debug stoppers, resfix marker, and recovery/ggtt flags. `xe_gt_sriov_vf` aggregates negotiated GuC versions, self config, runtime, and migration.

Control flow: config/runtime queries fill self_config/runtime; migration event handling drives migration fields and waitqueue; debugfs can set `debug.resfix_stoppers`.

State and persistence: all fields are volatile driver state, allocated/initialized during VF GT setup and torn down with device-managed actions.

Dependencies and integration: includes Linux types/wait/workqueue and Xe firmware version types; embedded in main GT SR-IOV union/state.

Risks: booleans used with `READ_ONCE`/`WRITE_ONCE` and barriers in implementation must remain aligned with waitqueue semantics. Runtime register array size/count separation must be respected when resizing.

Test signals: migration recovery state transitions, runtime register resize, fixup count waits, and debug stopper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_vf_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.c

Purpose: implements per-GT debug statistics counters using per-CPU storage to avoid hot-path atomics.

Important APIs and functions: `xe_gt_stats_init` allocates per-CPU `struct xe_gt_stats` and registers cleanup; `xe_gt_stats_incr` increments a counter on the current CPU; `xe_gt_stats_print_info` sums all CPUs and prints descriptions; `xe_gt_stats_clear` zeroes all per-CPU counters.

Control flow: init attaches cleanup to the DRM device lifetime. Producers call `xe_gt_stats_incr` with an enum id. Debugfs print iterates every stat and every possible CPU to produce totals.

State and persistence: `gt->stats` points to per-CPU counters. State is volatile, cleared by explicit debugfs clear or freed on GT teardown. Clear is documented as unsafe under concurrent updates.

Dependencies and integration: depends on DRM managed cleanup and printer, `xe_device`, and the enum/type header. Counters are used by SVM page fault/migration, TLB invalidation, page-table reclaim, and hardware engine group paths; debugfs exposes print/clear.

Risks: `xe_gt_stats_incr` silently ignores invalid ids, but assumes `gt->stats` is initialized when CONFIG_DEBUG_FS is enabled. Concurrent clear can produce unpredictable totals. Description array must stay aligned with enum order.

Test signals: debugfs stats read/clear, hot-path increments from SVM/TLB/page reclaim, CPU hotplug/per-CPU summing, and enum/description build consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.h

Purpose: declares GT stats APIs and provides no-op/time helper behavior when debugfs stats are disabled.

Important APIs: under `CONFIG_DEBUG_FS`, declares init/print/clear/incr. Without debugfs, init returns 0 and increment is a no-op. Inline time helpers return `ktime_get`/delta only when debugfs is enabled, otherwise zero.

Control flow: instrumentation can call stats and timing helpers unconditionally; compile-time config removes overhead for non-debugfs builds.

State and persistence: state is `gt->stats` from the implementation and `struct xe_gt_stats`.

Dependencies and integration: includes `linux/ktime.h` and `xe_gt_stats_types.h`; used by SVM, TLB invalidation, page reclaim, and engine group code.

Risks: timing helpers returning zero when disabled means callers must only use them for stats, not functional timing. Print/clear declarations are absent in non-debugfs builds.

Test signals: compile with and without CONFIG_DEBUG_FS and verify instrumentation has no missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats_types.h

Purpose: defines GT statistics IDs and the per-CPU counter storage structure.

Important types: `enum xe_gt_stats_id` covers SVM page faults, TLB invalidations, page-fault sizes/timings, migration/copy metrics, hardware engine group queue metrics, and page reclaim list metrics. `struct xe_gt_stats` stores a cacheline-aligned `u64 counters[__XE_GT_STATS_NUM_IDS]`.

Control flow: enum values index both counter arrays and the description array in `xe_gt_stats.c`.

State and persistence: per-CPU instances are allocated at GT stats init and freed at teardown.

Dependencies and integration: includes Linux types; included by `xe_gt_types.h` and stats API.

Risks: enum insertions require updating `stat_description` to avoid NULL names or mismatched output. Cacheline alignment helps but per-CPU allocation still consumes memory proportional to stat count and CPU count.

Test signals: build-time and debugfs output validation for every enum id, plus instrumentation tests for newly added counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.c

Purpose: creates the per-GT sysfs kobject under a tile sysfs node.

Important APIs and functions: `xe_gt_sysfs_init` allocates `struct kobj_gt`, initializes its kobject type, adds it as `gt%d` under `tile->sysfs`, stores `gt->sysfs`, and registers a managed cleanup action. `xe_gt_sysfs_kobj_release` frees the wrapper object; `gt_sysfs_fini` drops the kobject reference.

Control flow: initialization is called during GT setup after tile sysfs exists. On kobject add failure, the initialized kobject is put, invoking release.

State and persistence: `gt->sysfs` points to the kobject for the GT lifetime. Sysfs entries are kernel object lifetime state, not persistent storage.

Dependencies and integration: depends on Linux kobject/sysfs, DRM managed device actions, and GT/tile/device types. Other GT sysfs feature groups attach under this kobject.

Risks: kobject lifetime correctness depends on exactly one `kobject_put` through managed cleanup after successful add. `kzalloc_obj` allocation failure or `kobject_add` failure must not leak.

Test signals: GT sysfs directory creation/removal for multi-tile/multi-GT devices, failure injection on allocation/add, and use-after-free checks during device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.h

Purpose: declares GT sysfs initialization and provides a helper to recover `struct xe_gt` from a GT kobject.

Important APIs: `xe_gt_sysfs_init` and inline `kobj_to_gt`, which uses `container_of(kobj, struct kobj_gt, base)->gt`.

Control flow: sysfs attribute handlers use `kobj_to_gt` to map from their kobject context back to the GT.

State and persistence: no state beyond the `kobj_gt` wrapper defined in the types header.

Dependencies and integration: includes `xe_gt_sysfs_types.h`; used by throttling and frequency sysfs code.

Risks: `kobj_to_gt` assumes the kobject is a `struct kobj_gt`, so it must not be used on child group kobjects unless their parent is first resolved appropriately.

Test signals: sysfs attribute handlers on GT kobjects and type-safety review of call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs_types.h

Purpose: defines the wrapper type connecting a sysfs kobject to an Xe GT.

Important type: `struct kobj_gt` contains the base `struct kobject` and a `struct xe_gt *gt`.

Control flow: `xe_gt_sysfs_init` allocates and registers this wrapper; `kobj_to_gt` retrieves the GT for sysfs handlers.

State and persistence: wrapper lifetime is owned by kobject reference counting and device-managed cleanup.

Dependencies and integration: includes Linux kobject and forward-declares `struct xe_gt`.

Risks: release must free the wrapper allocation, and users must not keep `gt` references past GT teardown.

Test signals: kobject lifetime tests during driver bind/unbind and sysfs access races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sysfs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.c

Purpose: exposes GT hardware/firmware frequency throttling reasons under `freq0/throttle/` sysfs.

Important APIs and functions: `xe_gt_throttle_get_limit_reasons` reads platform-specific perf limit reason registers with runtime PM held. `xe_gt_throttle_init` creates the throttle sysfs group and registers cleanup. Internal sysfs show helpers expose boolean `status`, individual `reason_*` files, and aggregate `reasons`.

Control flow: register selection uses media vs non-media GT and Crescent Island vs default masks. `reason_show` checks a single mask; `reasons_show` reads the full reason mask once, iterates the active platform group, and emits names for all active reason attributes or `none`.

State and persistence: no cached state; every read samples MMIO. Sysfs group lifetime follows `gt->freq` and DRM device-managed cleanup.

Dependencies and integration: depends on GT regs, MMIO, platform types, runtime PM, GT sysfs/frequency kobjects, and callers such as GuC power/frequency reporting.

Risks: aggregate `reasons` depends on attribute names starting with `reason_`; `status` uses `U32_MAX` as a special mask but is excluded from aggregate names. Unknown bits trigger a one-time DRM warning and return `none`, which can hide new hardware reason bits until masks are updated.

Test signals: sysfs reads on Crescent Island and default platforms, media/non-media register selection, runtime PM behavior, unknown bit warning, and cleanup on GT removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.h

Purpose: declares the GT throttling sysfs setup and reason-mask read API.

Important APIs: `xe_gt_throttle_init` creates throttling sysfs attributes, and `xe_gt_throttle_get_limit_reasons` returns the current masked throttle reason bits from hardware.

Control flow: GT frequency sysfs setup calls init; power/frequency reporting code can call the reason getter directly.

State and persistence: no state in the header; implementation reads MMIO on demand.

Dependencies and integration: forward-declares `struct xe_gt` and includes Linux types.

Risks: callers of `get_limit_reasons` may trigger runtime PM and MMIO reads, so it should not be used from atomic contexts.

Test signals: compile integration with GT frequency and GuC power code, plus sysfs group creation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_throttle.h -->
