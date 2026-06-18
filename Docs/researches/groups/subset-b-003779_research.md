# Research: subset-b-003779

Grouped research for Xe GuC submission, TLB invalidation, HuC/GSC support, hardware engines, hardware errors, and hardware fences.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.c

Purpose: implements the GuC-backed `xe_exec_queue_ops` scheduler backend. It owns GuC context ID allocation, registration/deregistration, GuC CT H2G messages for submission and scheduling policy, G2H completion/error handlers, reset/pause/replay flows, multi-LRC/parallel work queues, multi-queue CGP synchronization, and devcoredump snapshots.

Important APIs/functions: `xe_guc_submit_init`, `xe_guc_submit_enable/disable`, `xe_guc_submit_reset_prepare`, `xe_guc_submit_stop/start`, `xe_guc_submit_pause*`, `xe_guc_submit_unpause*`, `xe_guc_submit_wedge`, GuC G2H handlers such as `xe_guc_sched_done_handler`, `xe_guc_deregister_done_handler`, `xe_guc_exec_queue_reset_handler`, CAT/CGP/error-capture handlers, `xe_guc_exec_queue_snapshot_*`, `xe_guc_submit_print`, `xe_guc_register_vf_exec_queue`, `xe_guc_has_registered_mlrc_queues`, and `xe_guc_contexts_hwsp_rebase`. Local core paths include `guc_exec_queue_run_job`, `guc_exec_queue_timedout_job`, `register_exec_queue`, `submit_exec_queue`, `disable_scheduling_deregister`, and queue message processors.

Control flow: initialization installs GuC exec queue ops on the GT, initializes `submission_state.lock`, the GuC ID manager, the xarray `exec_queue_lookup`, and managed cleanup actions. Queue creation allocates `struct xe_guc_exec_queue`, initializes scheduler/entity state, reserves one or more GuC IDs under the submission lock, stores xarray lookups, and links secondary multi-queue queues into their group. First job submission lazily registers the queue with GuC, emits the job if needed, writes ring tails or parallel WQ items, then sends either `SCHED_CONTEXT_MODE_SET` enable or `SCHED_CONTEXT`.

State/persistence: per-queue GuC state is an atomic bitfield (`REGISTERED`, `ENABLED`, `PENDING_ENABLE`, `PENDING_DISABLE`, `DESTROYED`, `SUSPENDED`, `RESET`, `KILLED`, `WEDGED`, `BANNED`, `PENDING_RESUME`, `IDLE_SKIP_SUSPEND`). GuC submission global state persists in `guc->submission_state`: ID bitmap, xarray lookup, `stopped`, `enabled`, and fini waitqueue. Queue policy state comes from `q->sched_props`; parallel queues persist WQ head/tail in `q->guc` and shared scratch memory.

Dependencies/integration: depends on GuC CT transport, GuC ID manager, DRM GPU scheduler, Xe scheduler messages, LRC/ring ops, PM runtime, forcewake, devcoredump, GuC capture, VM/LR mode, SR-IOV VF recovery, hardware engine class names, and multi-queue groups. It is called from GT reset/recovery, exec queue lifecycle, GuC G2H dispatch, devcoredump, and VF migration/recovery paths.

Risks: state transition races are high risk because G2H handlers, scheduler work, reset paths, suspend/resume, and destroy can overlap. The code relies on atomic bits plus CT wait queues rather than one global state lock for all transitions. Timeout paths may trigger GT reset if GuC fails to answer enable/disable. Parallel WQ space waiting can force reset after a long stall. Multi-queue CGP sync allows one outstanding update and resets/bans on timeout. Destroy paths defer work to avoid scheduler self-finalization, so refcount and xarray cleanup bugs can leak queues or prematurely free scheduler-visible names.

Test signals: exercise GuC submission creation/destruction, lazy registration, scheduler property changes, suspend/resume, TDR timeout, GuC reset recovery, VF pause/unpause replay, MLRC/parallel queue WQ wrapping, multi-queue CGP sync done/error notifications, CAT faults, devcoredump snapshots, and driver unload with outstanding queues. Logs mentioning pending enable/disable failure, schedule disable failure, CGP sync wait failure, invalid G2H lengths, or unexpected queue state are strong regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.h

Purpose: public GuC submission interface for the Xe driver. It exposes lifecycle, reset, pause/unpause, G2H handling, snapshot, VF registration, MLRC detection, and HWSP rebase entry points implemented in `xe_guc_submit.c`.

Important APIs: initialization and enablement (`xe_guc_submit_init`, `xe_guc_submit_enable`, `xe_guc_submit_disable`), reset lifecycle (`xe_guc_submit_reset_prepare`, `xe_guc_submit_reset_wait`, `xe_guc_submit_stop`, `xe_guc_submit_start`), pause/replay (`xe_guc_submit_pause`, `xe_guc_submit_pause_vf`, `xe_guc_submit_unpause_prepare_vf`, `xe_guc_submit_unpause`, `xe_guc_submit_unpause_vf`, `xe_guc_submit_pause_abort`), wedging (`xe_guc_submit_wedge`), GuC notification handlers, snapshot capture/print/free, and `xe_guc_contexts_hwsp_rebase`.

Control flow: callers include GT init, GuC startup, reset handlers, CT G2H dispatch, VF recovery, devcoredump, and exec queue utilities. The header deliberately forward-declares objects to keep compile-time dependencies lower.

State/persistence: no state is declared here, but every function manipulates `struct xe_guc` submission state or per-queue GuC state described in the C file. Snapshot allocation returns a heap object that callers must free with `xe_guc_exec_queue_snapshot_free`.

Dependencies/integration: uses `u32`/`bool`, `struct drm_printer`, `struct xe_guc`, and `struct xe_exec_queue`. It is a central contract between GuC transport, reset, exec queue management, and diagnostics.

Risks/test signals: signature mismatches would break CT dispatch and reset integration. Tests should verify that all G2H handlers reject malformed message lengths and that snapshot users pair capture/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit_types.h

Purpose: defines GuC submission data layouts shared between host and GuC-facing submission code, especially parallel submission scratch/WQ memory and devcoredump snapshots.

Important types/constants: WQ status/type masks, GuC ID and ring tail masks, `PARALLEL_SCRATCH_SIZE`, `WQ_SIZE`, `struct guc_sched_wq_desc`, cacheline-padded `struct sync_semaphore`, `struct guc_submit_parallel_scratch`, and `struct xe_guc_submit_exec_queue_snapshot`.

Control flow: `xe_guc_submit.c` initializes `guc_submit_parallel_scratch`, appends NOOP or multi-LRC WQ entries, reads WQ head/tail/status for snapshots, and prints the snapshot fields later from devcoredump/debug paths.

State/persistence: the scratch structure is memory shared with GuC through the LRC parallel scratch mapping. The snapshot persists a point-in-time copy of queue identity, scheduling properties, LRC snapshots, schedule state, parallel WQ contents, and multi-queue metadata.

Dependencies/integration: depends on `xe_hw_engine_types.h` for engine classes and `XE_HW_ENGINE_MAX_INSTANCE`; implicitly depends on LRC snapshot definitions through pointers. ABI layout and packed descriptors must remain compatible with GuC expectations.

Risks/test signals: layout, size, and mask changes can corrupt GuC WQ interpretation. Tests should cover WQ wrap/noop behavior, multi-LRC width bounds, snapshot allocation/printing, and early sequence wrap behavior in parallel queue submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_submit_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.c

Purpose: GuC-backed implementation of `xe_tlb_inval_ops`. It sends global, GGTT, ASID PPGTT, context PPGTT, range-selective, and page-reclamation invalidation requests through GuC CT, with MMIO fallback for GGTT invalidation when CT submission is unavailable.

Important functions: `send_tlb_inval`, `send_tlb_inval_all`, `send_tlb_inval_ggtt`, `send_tlb_inval_ppgtt`, `send_tlb_inval_asid_ppgtt`, `send_tlb_inval_ctx_ppgtt`, `normalize_invalidation_range`, `send_page_reclaim`, `xe_guc_tlb_inval_init_early`, and `xe_guc_tlb_inval_done_handler`.

Control flow: early init stores the GuC as `tlb_inval->private` and selects ASID or context ops based on `xe->info.has_ctx_tlb_inval`. Each send path allocates a seqno in the generic TLB invalidation layer, builds a GuC action, sends it with a one-message G2H reservation, then the done handler forwards the returned seqno to `xe_tlb_inval_done_handler`.

State/persistence: the algorithm assumes GuC processes invalidations in order. `seqno_lock` protects PPGTT issue ordering. Context invalidation temporarily moves active VM exec queues onto a local list while holding `vm->exec_queues.lock` and returns them before dropping refs. PRL requests use a suballocated buffer address and invalidate seqno only on the page reclamation message.

Dependencies/integration: integrates GuC CT, GT stats, forcewake/MMIO fallback registers, VM ASID lookup, exec queue activity callbacks, SA BO addresses for page reclamation, and generic `xe_tlb_inval` sequencing/waiting.

Risks/test signals: ordered seqno dependence is explicit and fragile if GuC ordering changes. Range normalization must avoid overflow and respect platform range invalidation constraints. Context invalidation must preserve VM exec queue list integrity on all errors. Test with CT enabled/disabled, wedged devices, SR-IOV VF fallback cancellation, high active queue counts forcing full invalidation, no-active-queue dummy GGTT invalidations, PRL requests, and malformed done messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.h

Purpose: public header for binding a generic Xe TLB invalidation client to GuC-backed operations and for receiving GuC invalidation completion messages.

Important APIs: `xe_guc_tlb_inval_init_early` and `xe_guc_tlb_inval_done_handler`.

Control flow/state: init is called during GT/GuC setup before runtime invalidations, while the done handler is called from GuC CT G2H dispatch. The header carries no storage and uses forward declarations for `struct xe_guc` and `struct xe_tlb_inval`.

Dependencies/integration: bridges GuC submission/CT with the generic TLB invalidation subsystem.

Risks/test signals: malformed G2H length should return `-EPROTO`; initialization must select the correct backend ops for context versus ASID invalidation platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_types.h

Purpose: central state definition for the Xe GuC object and small GuC managers. It aggregates firmware, logging, ADS, CT, buffer cache, capture, power conservation, doorbells, submission state, hwconfig, SR-IOV relay, engine activity, notify register, and control parameters.

Important types: `struct xe_guc_db_mgr`, `struct xe_guc_id_mgr`, and `struct xe_guc`. Key nested state is `submission_state` with ID manager, `exec_queue_lookup` xarray, `stopped`, `reset_blocked`, lock, `enabled`, `initialized`, and fini waitqueue.

Control flow: fields are initialized across GuC firmware bring-up, submission init, CT setup, ADS setup, hwconfig retrieval, relay setup, and power management. Submission code relies on the xarray and ID manager under `submission_state.lock`.

State/persistence: this structure is long-lived per GT. Several nested objects own BOs or firmware state managed by DRM/devm lifetimes. Atomic fields allow reset and submission stop state to be observed in CT handlers and scheduler paths.

Dependencies/integration: includes many GuC component type headers plus xarray/idr and register definitions. It is referenced by nearly every GuC subsystem.

Risks/test signals: because this type is a shared hub, field lifetime and locking documentation matter. Submission ID manager and doorbell manager both rely on `submission_state.lock`; tests should cover init/fini ordering and reset while queues are live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.c

Purpose: creates the auxiliary MEI/HECI device used to communicate with the Graphics Security Controller firmware and forwards GSC/CSC HECI interrupts from Xe IRQ handling to that auxiliary device.

Important functions/types: `struct heci_gsc_def`, platform definitions for DG1/DG2/PVC/Battlemage, `heci_gsc_irq_init`, `heci_gsc_irq_setup`, `heci_gsc_add_device`, `xe_heci_gsc_init`, `xe_heci_gsc_irq_handler`, `xe_heci_csc_irq_handler`, and cleanup `xe_heci_gsc_fini`.

Control flow: init checks `has_heci_gscfi`/`has_heci_cscfi`, selects a platform BAR definition, registers managed cleanup, optionally allocates a Linux IRQ descriptor unless polling/survivability boot mode is active, constructs a `mei_aux_device` with BAR resource under PCI BAR0, initializes it as an auxiliary device, and adds it. IRQ handlers filter IIR bits, check feature support and valid IRQ, then call `generic_handle_irq_safe`.

State/persistence: `xe->heci_gsc` stores the auxiliary device pointer and IRQ number. Cleanup deletes/uninitializes the auxiliary device and frees the IRQ descriptor.

Dependencies/integration: integrates Linux auxiliary bus, MEI aux driver, PCI resources, GSC register base definitions, DRM logging, and survivability mode.

Risks/test signals: wrong BAR offsets or IRQ bit mapping break GSC firmware communication. Cleanup must not leak `mei_aux_device` or IRQ descriptors on partial failure. Test unsupported platforms, polling/survivability boot, aux init/add failures, GSC versus CSC IRQ feature mismatches, and repeated init cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.h

Purpose: declares the Xe HECI/GSC auxiliary-device state, interrupt bit helpers, and public init/IRQ entry points.

Important APIs/types: `GSC_IRQ_INTF`, `CSC_IRQ_INTF`, `struct xe_heci_gsc`, `xe_heci_gsc_init`, `xe_heci_gsc_irq_handler`, and `xe_heci_csc_irq_handler`.

Control flow/state: `struct xe_heci_gsc` is embedded in `struct xe_device` and persists the MEI auxiliary device pointer and allocated IRQ number. The bit helpers encode GSC HECI1/2 and CSC HECI1/2 interrupt positions.

Dependencies/integration: forward-declares `struct xe_device` and `struct mei_aux_device`, bridging Xe device code to the MEI auxiliary bus.

Risks/test signals: bit helper changes affect IRQ routing. Tests should confirm GSC/CSC interrupt filters call the generic IRQ only for the intended interface bit and only when the feature is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_heci_gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.c

Purpose: manages HuC firmware initialization, upload, authentication via GuC or GSC, status sanitization, and debug printing.

Important functions: `xe_huc_init`, `xe_huc_init_post_hwconfig`, `xe_huc_upload`, `xe_huc_auth`, `xe_huc_is_authenticated`, `xe_huc_sanitize`, `xe_huc_print_info`, plus local GSC auth helpers `huc_alloc_gsc_pkt`, `huc_emit_pxp_auth_msg`, and `huc_auth_via_gsccs`.

Control flow: init marks firmware type as HuC, skips unsupported non-media GTs on newer platforms, initializes firmware metadata, skips extra work if disabled or SR-IOV VF, allocates a GGTT system BO for GSC auth packets when GSC headers are present, and marks firmware loadable. Upload sends the firmware through `xe_uc_fw_upload`. Authentication first checks existing auth status, verifies firmware is loaded, triggers GuC RSA auth or submits a PXP 4.3 GSC packet through GSCCS, waits for the appropriate MMIO auth bit, and updates firmware status to running or load fail.

State/persistence: `struct xe_huc` stores generic firmware state and an optional `gsc_pkt` BO used as input/output packet storage. Firmware BO may be reinitialized into VRAM after hwconfig on DGFX.

Dependencies/integration: uses uC firmware helpers, GuC auth, GSC packet submit helpers, GGTT BO mapping, forcewake/MMIO, PXP command ABI, SR-IOV checks, and GT/device logging.

Risks/test signals: platform/GT support checks are sensitive because HuC availability differs between media and primary GTs. GSC auth retries handle pending replies; reply parsing and status handling must distinguish already-authenticated from real failure. Test GuC and GSC auth modes, missing packet BO, pending GSC replies, auth timeout, firmware disabled/unavailable, DGFX VRAM reinit, and HuC status debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.h

Purpose: public HuC firmware management API and authentication mode enum.

Important APIs/types: `enum xe_huc_auth_types` with GuC and GSC auth, plus init, post-hwconfig init, upload, auth, auth-status query, sanitize, and print functions.

Control flow/state: higher-level GT/uC init code calls these functions in firmware lifecycle order. Auth status is queried through MMIO-backed implementation in the C file.

Dependencies/integration: forward declares `struct xe_huc` and `struct drm_printer`; integrates with uC firmware, GuC, GSC, and debugfs callers.

Risks/test signals: adding auth types requires updating the implementation table. Tests should cover each auth enum and ensure disabled firmware paths return success without touching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.c

Purpose: registers HuC debugfs reporting under a GT/uC debugfs parent.

Important functions: `xe_huc_debugfs_register`, local `huc_info`, `node_to_huc`, and helpers to reach GT/device from `struct xe_huc`.

Control flow: registration DRM-managed allocates a copy of the static `drm_info_list`, stores the HuC pointer in each entry, and creates `huc_info`. Reads acquire PM runtime with `guard(xe_pm_runtime)` and call `xe_huc_print_info`.

State/persistence: no persistent state beyond the DRM-managed copied info list and per-entry `data` pointer.

Dependencies/integration: uses DRM debugfs helpers, `xe_huc_print_info`, PM runtime, and GT/HuC embedding.

Risks/test signals: missing allocation silently skips debugfs. Test debugfs read with runtime suspended/resumed and with HuC disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.h

Purpose: declares HuC debugfs registration.

Important API: `xe_huc_debugfs_register(struct xe_huc *huc, struct dentry *parent)`.

Control flow/state: called by debugfs setup code to publish HuC information below a parent dentry. It owns no types beyond forward declarations.

Dependencies/integration: bridges debugfs setup with HuC firmware status printing.

Risks/test signals: incorrect parent or HuC pointer would affect only diagnostics. Verify `huc_info` appears when debugfs is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_types.h

Purpose: defines the persistent HuC object embedded in Xe uC/GT state.

Important type: `struct xe_huc` containing `struct xe_uc_fw fw` and optional `struct xe_bo *gsc_pkt`.

Control flow/state: firmware lifecycle helpers update `fw` status, BO placement, load/auth state, and use `gsc_pkt` when authentication is routed through GSC/GSCCS.

Dependencies/integration: depends on generic uC firmware types and forward-declares `struct xe_bo`.

Risks/test signals: `gsc_pkt` lifetime must match managed BO lifetime and only be used when allocated. Tests should verify GSC-auth platforms allocate it and GuC-auth or VF paths do not require it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.c

Purpose: discovers, filters, initializes, controls, and snapshots physical hardware engines for a GT. It maps engine IDs to classes/MMIO bases/IRQ offsets/forcewake domains, applies workarounds and tuning, enables rings, handles engine IRQs, and exposes lookup/utility helpers.

Important functions/types: static `engine_infos`, `xe_hw_engines_init_early`, `xe_hw_engines_init`, `hw_engine_init_early`, `hw_engine_init`, `xe_hw_engine_enable_ring`, `xe_hw_engine_setup_default_lrc_state`, `xe_hw_engine_mmio_read32/write32`, fuse readers for media/copy/compute engines, GSC availability and configfs filtering, `xe_hw_engine_handle_irq`, snapshot capture/free/print, reservation checks, class string conversion, timestamp read, forcewake domain lookup, and UAPI class-instance lookup.

Control flow: early init reads fuses and software disable masks, disables unavailable GSC engine, fills each valid `struct xe_hw_engine`, initializes scheduling defaults per class, processes tuning/workaround/register whitelist state, and prepares default register save/restore tables. Full init applies register state, creates an HWSP BO, creates execlist ports when GuC is disabled or enables rings when GuC is enabled, adjusts IDLEDLY, registers cleanup, computes logical instances, and sets up hardware engine groups.

State/persistence: each engine persists GT pointer, class/instance/logical instance, MMIO base, IRQ offset, forcewake domain, HWSP BO, execlist port or GuC ring state, per-class scheduling interface, register state tables, optional IRQ handler, and group pointer. `gt->info.engine_mask` is destructively filtered by fuses/config before engine objects are initialized.

Dependencies/integration: integrates registers, forcewake, MMIO, BO/HWSP allocation, execlist backend, GuC/GSC support, GT topology, CCS mode, configfs engine disabling, tuning/workaround/RTP frameworks, hw fences, IRQ dispatch, devcoredump/GuC capture, and UAPI engine class mapping.

Risks/test signals: engine mask filtering affects user-visible engine availability. Forcewake must be held for engine-relative MMIO helpers. GSC engine timeout and availability logic are platform-sensitive. Snapshot code has different behavior for VF and GuC capture availability. Test fuse combinations, configfs engine masks, GuC versus execlist init, MSI-X IRQ offsets, compute/copy/media engine masks, reserved engines (OTHER, CCS mode, USM BCS), ring enable register writes, and lookup bounds/nospec behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.h

Purpose: public hardware-engine API and default scheduler property bounds.

Important APIs/constants: Kconfig-backed defaults for job timeout, timeslice, and preempt timeout min/max/defaults; engine init, IRQ, ring enable, per-class mask, snapshot, print, LRC state setup, reservation check, lookup, class-to-string, timestamp, forcewake-domain, and engine-relative MMIO helpers. `xe_hw_engine_is_valid` checks `hwe->name`.

Control flow/state: GT init calls early/full init; IRQ code calls `xe_hw_engine_handle_irq`; exec queue and diagnostics code call lookup and snapshots; register programming code uses MMIO helpers.

Dependencies/integration: includes engine types and uses `struct xe_gt`, `struct xe_device`, `struct xe_exec_queue`, DRM printer, and UAPI class-instance structs.

Risks/test signals: default range macros must align with sysfs validation. Tests should verify invalid engines have no name, lookups reject out-of-range UAPI classes, and forcewake assertions catch bad MMIO access in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.c

Purpose: exposes per-hardware-engine-class scheduler properties through sysfs, with writable live values and read-only `.defaults`.

Important functions: `xe_hw_engine_class_sysfs_init`, `xe_hw_engine_timeout_in_range`, kobject creation/cleanup helpers, show/store wrappers that hold PM runtime, and store/show methods for job timeout, timeslice duration, and preempt timeout current/min/max/defaults.

Control flow: init creates an `engines` kobject under GT sysfs, walks hardware engines, skips OTHER/MAX, creates one child per engine class (`rcs`, `bcs`, `vcs`, `vecs`, `ccs`), attaches the class scheduling interface, creates `.defaults`, then creates live writable files. Managed cleanup removes files and puts kobjects.

State/persistence: sysfs writes update `hwe->eclass->sched_props` using `WRITE_ONCE`; default values remain in `eclass->defaults`. No locking beyond atomic-style writes is used for these 32-bit properties.

Dependencies/integration: integrates Linux kobject/sysfs APIs, DRM managed cleanup, Xe PM runtime, hardware engine class names, and scheduler property storage in `struct xe_hw_engine_class_intf`.

Risks/test signals: min/max stores must preserve valid ordering; live values are only range-checked against current min/max. Kobject release frees allocated objects, so cleanup ordering must match created files. Test valid/invalid writes, min > max rejection, max < min rejection, PM runtime around reads/writes, one sysfs directory per class despite multiple instances, and error-injected default directory creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.h

Purpose: declares engine-class sysfs initialization, timeout range validation, and the kobject wrapper used to map sysfs callbacks back to Xe device and engine class state.

Important APIs/types: `xe_hw_engine_class_sysfs_init`, `xe_hw_engine_timeout_in_range`, `struct kobj_eclass`, `kobj_to_eclass`, and `kobj_to_xe`.

Control flow/state: sysfs callbacks receive a `struct kobject` and recover the embedded `kobj_eclass` to access `xe` and `eclass` pointers.

Dependencies/integration: includes Linux kobject and references `struct xe_hw_engine_class_intf`; implicitly requires `struct xe_device` visibility in users.

Risks/test signals: the inline container conversions assume every callback kobject is a `struct kobj_eclass` except the defaults child uses parent conversion. Tests should cover default file callbacks and live file callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_class_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.c

Purpose: groups hardware engines that share resources so the driver can enforce mutual exclusion between long-running faulting execution and DMA-fence mode execution.

Important functions: `xe_hw_engine_setup_groups`, `xe_hw_engine_group_add_exec_queue`, `xe_hw_engine_group_del_exec_queue`, `xe_hw_engine_group_resume_faulting_lr_jobs`, `xe_hw_engine_group_get_mode`, `xe_hw_engine_group_put`, and `xe_hw_engine_group_find_exec_mode`. Local helpers allocate groups, suspend faulting LR jobs, wait for DMA-fence jobs, switch modes, and wait sync dependencies.

Control flow: setup allocates three groups per GT: render/compute, copy, and video decode/enhance. Adding an exec queue links it under `mode_sem`; when adding a fault-mode queue while the group is in DMA-fence mode, it suspends and waits for that queue first. `get_mode` acquires read mode if already correct, otherwise upgrades to write, switches by suspending LR queues or waiting DMA-fence jobs, downgrades to read, and expects caller to release with `put`.

State/persistence: each group owns `exec_queue_list`, `resume_work`, a workqueue, `mode_sem`, and current execution mode. Exec queues are linked through `hw_engine_group_link`.

Dependencies/integration: uses exec queue suspend/resume ops, VM mode helpers, sync waiters, DMA fence waits, GT stats, DRM managed allocation, and workqueue cleanup.

Risks/test signals: lock acquisition is interruptible/killable in public paths. Switching from LR to DMA-fence can return `-EAGAIN` when a faulting LR queue cannot be suspended while dependencies exist; the code waits syncs then retries. Test mode switches with dependency syncs, queue add/delete under mode changes, fault-mode resume work, DMA fence wait errors, and stats counters for suspend/wait latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.h

Purpose: public API for hardware engine group setup, exec queue membership, execution mode acquisition/release, mode selection, and async LR queue resume.

Important APIs: `xe_hw_engine_setup_groups`, add/delete exec queue, `xe_hw_engine_group_get_mode`, `xe_hw_engine_group_put`, `xe_hw_engine_group_find_exec_mode`, and `xe_hw_engine_group_resume_faulting_lr_jobs`.

Control flow/state: callers acquire a group mode with `get_mode` before submitting work that requires LR or DMA-fence execution, then release with `put`. Exec queue lifecycle calls add/delete.

Dependencies/integration: uses `struct xe_hw_engine_group`, exec queues, GT, and sync entries.

Risks/test signals: get/put pairing is required because `get_mode` returns with `mode_sem` held for read. Tests should catch missing puts and queue deletion while mode is held.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group_types.h

Purpose: defines hardware engine group modes and persistent group state.

Important types: `enum xe_hw_engine_group_execution_mode` (`EXEC_MODE_LR`, `EXEC_MODE_DMA_FENCE`) and `struct xe_hw_engine_group` with queue list, resume work/workqueue, read-write semaphore, and current mode.

Control flow/state: the group state is initialized during hardware engine setup and mutated by mode switching and queue add/delete paths.

Dependencies/integration: includes forcewake/LRC/reg state headers indirectly from engine type context, though this file only needs list/workqueue/rwsem declarations via broader includes.

Risks/test signals: `cur_mode` default is zero (`EXEC_MODE_LR`) because groups are zero-allocated; tests should verify initial mode assumptions and resume work lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_group_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_types.h

Purpose: declares engine class IDs, hardware engine IDs/masks, per-class scheduler property storage, hardware engine state, and hardware engine snapshot state.

Important types/constants: `enum xe_engine_class`, `enum xe_hw_engine_id`, class masks such as `XE_HW_ENGINE_BCS_MASK`, `XE_HW_ENGINE_MAX_INSTANCE`, `struct xe_hw_engine_class_intf`, `struct xe_hw_engine`, `enum xe_hw_engine_snapshot_source_id`, and `struct xe_hw_engine_snapshot`.

Control flow/state: hardware engine init populates `struct xe_hw_engine`; sysfs reads/writes `eclass`; exec queue creation and UAPI lookup use class/instance/logical instance; devcoredump/debug capture produces snapshots.

Dependencies/integration: includes forcewake, LRC, and register save/restore types and forward-declares BO, execlist port, GT, OA unit, and engine group.

Risks/test signals: enum ordering is ABI-sensitive inside the driver and maps to static tables. `XE_HW_ENGINE_MAX_INSTANCE` bounds parallel WQ arrays. Tests should verify masks cover intended IDs and engine info table stays aligned with enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_engine_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.c

Purpose: handles discrete GPU hardware error interrupts, logs and counts RAS errors, processes PVC GT/SOC error registers, handles Battlemage CSC firmware errors, and processes boot-time hardware errors.

Important functions/data: error severity mapping, PVC error name tables with `static_assert` sizes, `fault_inject_csc_hw_error`, `csc_hw_error_work`, `csc_hw_error_handler`, logging helpers, `gt_hw_error_handler`, `soc_slave_ieh_handler`, `soc_hw_error_handler`, `hw_error_source_handler`, `xe_hw_error_irq_handler`, `hw_error_info_init`, `process_hw_errors`, and `xe_hw_error_init`.

Control flow: init skips non-DGFX and SR-IOV VF, initializes CSC error work on the root tile, initializes RAS info for PVC, then reads and processes boot-time master IRQ state. IRQ handler iterates hardware error classes signaled in master control, reads `DEV_ERR_STAT`, handles CSC errors specially, maps source bits to RAS components, dispatches GT/SOC platform handlers, logs/counts, clears status registers, and un/masks SOC event controls when needed.

State/persistence: RAS counters live in `xe->ras`; CSC error work schedules runtime survivability mode enablement. Error status is persisted in hardware registers until read/cleared.

Dependencies/integration: uses hardware error/GSC/IRQ registers, Xe DRM RAS, MMIO, survivability mode, Linux fault injection, IRQ lock, and platform checks for PVC/Battlemage.

Risks/test signals: register clear order matters to avoid losing or re-reporting errors. CSC firmware errors make the device unrecoverable and trigger survivability mode. Platform guards mean most logic is PVC or Battlemage specific. Test fault injection, blank status registers, correctable/nonfatal/fatal paths, PVC GT vector counters, SOC master/slave handling, CSC survivability work scheduling, and boot-time preexisting errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.h

Purpose: public hardware error init and IRQ handling contract.

Important APIs: `xe_hw_error_irq_handler(struct xe_tile *tile, const u32 master_ctl)` and `xe_hw_error_init(struct xe_device *xe)`.

Control flow/state: device init calls `xe_hw_error_init`; IRQ code calls the handler with a tile and master interrupt control bits.

Dependencies/integration: forward-declares tile and device and includes Linux types.

Risks/test signals: callers must pass the correct tile matching the MMIO master status. Tests should verify init is a no-op for non-DGFX and SR-IOV VF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.c

Purpose: implements Xe hardware completion fences as `dma_fence` objects backed by a seqno memory location and signaled from engine IRQ work.

Important functions: module slab init/exit, `xe_hw_fence_irq_init`, `xe_hw_fence_irq_finish`, `xe_hw_fence_irq_run`, `xe_hw_fence_ctx_init`, `xe_hw_fence_alloc`, `xe_hw_fence_free`, `xe_hw_fence_init`, and dma-fence ops for driver/timeline names, signaling, signaled check, and release.

Control flow: module init creates a cache. A fence context allocates a dma-fence context and initial seqno. Fence init stores device, name, seqno map, initializes list link, and calls `dma_fence_init` with the IRQ spinlock. Enabling signaling takes a fence ref and appends it to `irq->pending`; IRQ work scans pending fences under lock and drops refs for signaled fences. Engine IRQs call `xe_hw_fence_irq_run`.

State/persistence: `xe_hw_fence_irq` owns the pending list and lock per engine class. Each fence stores its seqno map and list node. Release uses RCU and the slab cache. `XE_FENCE_INITIAL_SEQNO` intentionally starts near wrap to expose wrapping issues early.

Dependencies/integration: integrates Linux dma-fence, irq_work, RCU, Xe map reads, engine IRQ dispatch, tracepoints, GT/device state, and hardware seqno writes from jobs.

Risks/test signals: pending list refs must balance when signaling or finishing. Signaled logic treats fence error as completion and compares hardware seqno with dma-fence seqno. Test IRQ signaling, software-completed fences that need immediate work kick, finish with pending fences, RCU slab destruction, early seqno wrap, and fence error signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.h

Purpose: public API for Xe hardware fence module, IRQ list handling, fence contexts, allocation/free, and initialization.

Important APIs/constants: `XE_FENCE_INITIAL_SEQNO`, module init/exit, IRQ init/finish/run, context init/finish, `xe_hw_fence_alloc`, `xe_hw_fence_free`, and `xe_hw_fence_init`.

Control flow/state: module init must precede fence allocation; engine/GT setup initializes IRQ and contexts; jobs allocate/init fences; engine IRQs run pending fence signaling.

Dependencies/integration: includes `xe_hw_fence_types.h` and exposes `struct dma_fence`/`iosys_map` users through that header.

Risks/test signals: callers must not free initialized fences with `xe_hw_fence_free`; initialized fences are dma-fence refcounted. Test module unload after pending fences and context seqno progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence_types.h

Purpose: defines state for hardware fence IRQ handling, fence contexts, and individual hardware fences.

Important types: `struct xe_hw_fence_irq` with spinlock, irq_work, pending list, and enabled flag; `struct xe_hw_fence_ctx` with GT, IRQ pointer, dma-fence context, next seqno, and name; `struct xe_hw_fence` with embedded dma fence, device pointer, name, seqno map, and pending-list link.

Control flow/state: contexts issue monotonically increasing seqnos; fences compare their seqno against a memory-mapped hardware-written value; IRQ handler scans `pending`.

Dependencies/integration: depends on Linux dma-fence, iosys-map, irq_work, list, and spinlock; forward-declares Xe device and GT.

Risks/test signals: lock lifetime is important because it is passed to `dma_fence_init`; `xe_hw_fence_irq_finish` synchronizes RCU for safe lock release. Tests should inspect pending-list cleanup and seqno wrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hw_fence_types.h -->
