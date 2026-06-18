# Research Report: subset-b-003775

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.c

## Purpose
Implements Intel Xe GSC firmware lifecycle for the media GT: firmware staging into a private stolen-memory BO, GSCCS command submission for firmware load, compatibility-version query, async work handling, GSC reset workarounds, HuC-after-GSC authentication, proxy startup, and diagnostic printing.

## Important APIs, Types, and Functions
- Public entry points: `xe_gsc_init`, `xe_gsc_init_post_hwconfig`, `xe_gsc_load_start`, `xe_gsc_wait_for_worker_completion`, `xe_gsc_stop_prepare`, `xe_gsc_hwe_irq_handler`, `xe_gsc_wa_14015076503`, and `xe_gsc_print_info`.
- Firmware load helpers: `memcpy_fw`, `emit_gsc_upload`, `gsc_fw_is_loaded`, `gsc_fw_wait`, `gsc_upload`, and `gsc_upload_and_init`.
- Version query path uses `xe_gsc_emit_header`, `xe_gsc_pkt_submit_kernel`, and `xe_gsc_read_out_header` with MKHI compatibility-version ABI structures.
- Async work is encoded in `gsc->work_actions` using `GSC_ACTION_FW_LOAD`, `GSC_ACTION_SW_PROXY`, and `GSC_ACTION_ER_COMPLETE`, then consumed by `gsc_work`.

## Control Flow
- `xe_gsc_init` marks the GSC firmware type, initializes work/lock state, rejects non-media GTs when a media GT exists, initializes the uC firmware object, and initializes the GSC proxy unless the platform/configuration makes it unavailable.
- `xe_gsc_init_post_hwconfig` allocates a 4 MiB stolen/GGTT private BO, creates a permanent kernel GSCCS exec queue, creates an ordered workqueue, and marks the firmware loadable.
- `xe_gsc_load_start` handles already-loaded firmware surviving GT reset/D3Hot, otherwise sets `GSC_ACTION_FW_LOAD` and queues work.
- `gsc_upload_and_init` applies workaround `14018094691` with forcewake/MCR writes around `gsc_upload`, marks firmware transferred/running, restores sanitized frequencies, attempts HuC auth through GSC, and starts the GSC proxy.
- `xe_gsc_hwe_irq_handler` queues `GSC_ACTION_ER_COMPLETE`; `gsc_er_complete` reads `GSCI_TIMER_STATUS` and wedges the device if the Xe2 GSC engine reset timer expired.

## State and Persistence
- Persistent driver state lives in `struct xe_gsc`: firmware status, private BO, exec queue, ordered workqueue, pending action bits, and proxy state.
- GSC firmware survives GT reset and D3Hot; the code detects loaded firmware and only redoes missing proxy initialization state.
- `xe->needs_flr_on_fini` is set after firmware upload because the GSC can keep using the assigned memory until an FLR/D3cold-style reset.
- Firmware status transitions include loadable, transferred, running, and load-fail through `xe_uc_fw_change_status`.

## Dependencies and Integration Points
- Depends on Xe BO/GGTT mapping, GSCCS batch-buffer submission, uC firmware management, forcewake, MCR, GuC PC frequency control, HuC auth, proxy code, and GSC/HW registers.
- Integrated into GT init via `xe_uc_init_post_hwconfig`/GSC uC flows and GT reset via `xe_gsc_wa_14015076503`.
- `xe_gsc_print_info` is exposed by GSC debugfs and reads HECI status registers under `XE_FW_GSC` forcewake.

## Risks and Edge Cases
- Firmware copy uses CPU memcpy as a workaround for stolen-memory migration limitations, so mapping lifetime and BO size assumptions are important.
- Firmware load and packet submit both wait only one second for fences; slow GSCCS execution can produce `-ETIME`.
- Missing proxy completion before stop is treated seriously because interrupted init requires FLR to recover.
- Reset-timer failure currently wedges the full device because runtime FLR recovery is not implemented.

## Test Signals
- Boot/probe with GSC-capable media GTs should log GSC compatibility version and transition firmware to running.
- debugfs `gsc_info` should show firmware and HECI FWSTS values.
- Reset tests should cover GSC-loaded and GSC-not-loaded paths, including workaround register toggling.
- HuC authentication via GSC and MEI proxy startup are high-value integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.h

## Purpose
Declares the public GSC lifecycle, interrupt, reset-workaround, and diagnostic APIs used by Xe GT/uC code.

## Important APIs
- `xe_gsc_init` and `xe_gsc_init_post_hwconfig` split software firmware discovery/proxy setup from hardware-dependent queue/BO setup.
- `xe_gsc_load_start`, `xe_gsc_wait_for_worker_completion`, and `xe_gsc_stop_prepare` control asynchronous load/proxy work around runtime and stop paths.
- `xe_gsc_hwe_irq_handler` is the GSCCS interrupt hook for GSC engine-reset completion.
- `xe_gsc_wa_14015076503` is a GT reset preparation/cleanup workaround.
- `xe_gsc_print_info` emits firmware and HECI status diagnostics.

## Control Flow and Integration
This header is consumed by GT reset/init code, uC debugfs, and GSC implementation. It intentionally hides `struct xe_gsc` internals behind forward declarations, with state defined in `xe_gsc_types.h`.

## Risks and Test Signals
- Callers must honor the split init ordering: firmware/proxy state before post-hwconfig resources and load start only after a GSCCS queue exists.
- Reset paths should call the workaround only while holding the right forcewake domains, as enforced in implementation-side assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.c

## Purpose
Registers a per-GSC debugfs file that prints GSC firmware and HECI status information.

## Important APIs and Functions
- `xe_gsc_debugfs_register` creates the `gsc_info` drm debugfs info file under the supplied parent.
- `gsc_info` gets a runtime PM reference, creates a `drm_printer`, and delegates to `xe_gsc_print_info`.
- Local helpers translate a `drm_info_node` back to the `struct xe_gsc`, `struct xe_gt`, and `struct xe_device`.

## Control Flow and State
The registration allocates a device-managed copy of the static info list, stores `gsc` in each entry's data pointer, then calls `drm_debugfs_create_files`. No persistent state is owned here beyond the debugfs metadata managed by DRM/devres.

## Dependencies and Integration Points
Depends on DRM debugfs helpers, runtime PM guard macros, and `xe_gsc_print_info`. It is normally called from uC debugfs registration under the GT debugfs tree.

## Risks and Test Signals
- Allocation failure silently skips the debugfs file, which is acceptable for diagnostics but can hide probe issues.
- Reading `gsc_info` should not fail on a suspended device because it takes runtime PM before printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.h

## Purpose
Provides the declaration for GSC debugfs registration.

## Important API
- `xe_gsc_debugfs_register(struct xe_gsc *gsc, struct dentry *parent)` installs GSC diagnostic files beneath an existing debugfs directory.

## Integration and Risks
The header keeps dependencies minimal with forward declarations. Callers must pass a valid parent dentry and a fully initialized `struct xe_gsc`; the implementation tolerates allocation failure by omitting debugfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.c

## Purpose
Implements the software proxy that relays GSC firmware messages to CSME through the MEI GSC proxy component. Platforms with integrated GSC cannot let GSC directly reach CSME, so Xe submits proxy packets to GSC, forwards payloads to MEI, and returns MEI replies to GSC until an end message is received.

## Important APIs, Types, and Functions
- Public APIs: `xe_gsc_proxy_init`, `xe_gsc_proxy_start`, `xe_gsc_proxy_request_handler`, `xe_gsc_proxy_irq_handler`, `xe_gsc_proxy_init_done`, and `xe_gsc_wait_for_proxy_init_done`.
- Component callbacks: `xe_gsc_proxy_component_bind` and `xe_gsc_proxy_component_unbind` connect Xe to the MEI component via `I915_COMPONENT_GSC_PROXY`.
- Message helpers: `proxy_send_to_gsc`, `proxy_send_to_csme`, `validate_proxy_header`, `emit_proxy_header`, and `proxy_query`.
- IRQ helpers manipulate HECI2 CSR bits using `gsc_proxy_irq_clear` and `gsc_proxy_irq_toggle`.

## Control Flow
- `xe_gsc_proxy_init` initializes the mutex, validates `CONFIG_INTEL_MEI_GSC_PROXY` and root-tile assumptions, allocates a 64 KiB channel split into 32 KiB GSC-to-host and host-to-GSC buffers, registers the component, and installs a devm cleanup action.
- `xe_gsc_proxy_start` enables HECI2 proxy interrupts, manually triggers the first request handler, verifies proxy-normal FWSTS state, and marks `proxy.started`.
- `xe_gsc_proxy_request_handler` waits up to 20 seconds for the MEI component to bind, clears a pending interrupt, and runs `proxy_query` under `proxy.mutex`.
- `proxy_query` loops: send query/reply to GSC, validate GSC proxy header, forward GSC payload to CSME, validate CSME response, rewrap it with a GSC HECI header, and stop when GSC returns a `PROXY_END` header.
- HECI2 interrupts queue `GSC_ACTION_SW_PROXY` on the GSC ordered workqueue for serialized handling.

## State and Persistence
- `gsc->proxy.component`, `component_added`, `started`, BO/map pointers, and CPU CSME buffers are owned by `struct xe_gsc`.
- `proxy.mutex` protects component binding and message exchanges; GSC action bits are protected by `gsc->lock`.
- Cleanup disables IRQs, flushes GSC worker completion, clears `started`, removes the component, and avoids registering late devm actions during module unload.

## Dependencies and Integration Points
- Depends on MEI proxy component ops `send` and `recv`, Xe BO/GGTT buffer management, GSC packet submission helpers, runtime PM, forcewake, and HECI2 MMIO registers.
- Started from GSC firmware load completion and invoked later by IRQ path in `xe_irq.c`.
- Shares the same ordered workqueue as firmware load to avoid concurrent proxy/GSC operations.

## Risks and Edge Cases
- Component bind races are handled by polling, but a missing component after timeout fails proxy init.
- Header validation is critical: wrong source/destination, oversized payload, status errors, invalid zero-length payloads, or tiny CSME replies are rejected.
- `proxy_send_to_gsc` checks only input buffer size against 32 KiB; output bounds depend on GSC header validation and caller-provided channel layout.
- Interrupts are disabled if startup fails; missed cleanup would leave HECI2 interrupt generation active.

## Test Signals
- Probe with MEI proxy enabled should reach `HECI1_FWSTS1_PROXY_STATE_NORMAL`.
- Fault injection or mock MEI failures should exercise send/recv errors and IRQ disable rollback.
- Debug logs under `CONFIG_DRM_XE_DEBUG_SRIOV`/driver debug can show proxy KLV/message failures; HECI2 IRQ handling should queue work only when component exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.h

## Purpose
Declares the GSC-to-CSME proxy interface used by GSC firmware load/startup code and the IRQ layer.

## Important APIs
- `xe_gsc_proxy_init` allocates buffers and registers the MEI component.
- `xe_gsc_proxy_start` enables interrupts and triggers the first proxy exchange.
- `xe_gsc_proxy_init_done` and `xe_gsc_wait_for_proxy_init_done` inspect/wait for firmware proxy-normal state.
- `xe_gsc_proxy_request_handler` processes a pending software proxy transaction.
- `xe_gsc_proxy_irq_handler` bridges HECI2 interrupts into GSC workqueue actions.

## Integration and Risks
The header exposes no state, so users rely on `struct xe_gsc` internals from `xe_gsc_types.h`. Correct caller ordering is essential: init before start, start only after GSC firmware load, and IRQ handling only after component registration and workqueue setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.c

## Purpose
Provides generic GSC HECI packet helpers: creating host session IDs, emitting and validating MTL GSC headers, tracking pending replies, and submitting kernel packets to GSC through the GSCCS command streamer.

## Important APIs and Functions
- `xe_gsc_create_host_session_id` returns a random 64-bit host session handle with the top client-ID bits clear.
- `xe_gsc_emit_header` writes `struct intel_gsc_mtl_header`, encoding validity marker, HECI client, optional client-tagged host session handle, version, and total message size.
- `xe_gsc_poison_header` fills a header with `POISON_FREE` to catch stale replies.
- `xe_gsc_check_and_update_pending` copies `gsc_message_handle` from an output header into the input header when GSC marks a reply pending.
- `xe_gsc_read_out_header` validates marker, status, total size, and minimum payload length.
- `xe_gsc_pkt_submit_kernel` emits `GSC_HECI_CMD_PKT` into a batch buffer and waits for the submitted job fence.

## Control Flow
Callers allocate GGTT-visible input/output memory, emit a GSC header plus payload, call `xe_gsc_pkt_submit_kernel`, then validate the output header and parse payload. Pending-message users can reuse the same input header after `xe_gsc_check_and_update_pending` updates the retry handle.

## State and Persistence
The file does not own persistent state. It uses `gsc->q` for submission and relies on caller-owned buffers/maps. Host session IDs are randomized per caller and encoded with the HECI client ID in the top byte only when nonzero.

## Dependencies and Integration Points
Used by GSC firmware version query, GSC proxy, HuC auth via GSC, and any other kernel GSC clients. Depends on Xe batch-buffer/job submission, DRM fences, GSC command ABI, and map helpers.

## Risks and Edge Cases
- `xe_gsc_read_out_header` computes `payload_size = size - GSC_HDR_SIZE` before testing `size < GSC_HDR_SIZE`; unsigned underflow is later rejected by the size check but should remain considered when modifying validation.
- Packet submission requires input and output sizes at least the GSC header size and waits for only `HZ`.
- Header helpers assert host session client bits are initially clear, so callers must not pre-encode client IDs.

## Test Signals
- Unit-style tests can validate header fields, pending handle propagation, and invalid output header rejection.
- Integration tests include HuC auth and proxy transactions that exercise real GSCCS packet submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.h

## Purpose
Declares reusable GSC packet/header helpers for kernel clients.

## Important APIs
- Header construction and poisoning: `xe_gsc_emit_header`, `xe_gsc_poison_header`.
- Reply processing: `xe_gsc_check_and_update_pending`, `xe_gsc_read_out_header`.
- Packet submission: `xe_gsc_pkt_submit_kernel`.
- Session identity: `xe_gsc_create_host_session_id`.

## Integration and Risks
The API assumes caller-provided GGTT-visible buffers and an initialized `struct xe_gsc` with a valid GSCCS queue. Callers must size payloads consistently with HECI/GSC ABI expectations and validate output before parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_types.h

## Purpose
Defines `struct xe_gsc`, the per-GT GSC uC state object embedded in `struct xe_uc`.

## Important Types and Fields
- `fw`: generic Xe uC firmware object for discovery, status, version, and blob BO.
- `security_version`: SVN from the fetched firmware blob.
- `private`: private BO assigned to GSC firmware after load.
- `q`: default GSCCS exec queue used for firmware load and packet submission.
- `wq`, `work`, `lock`, `work_actions`: ordered async execution state for firmware load, proxy handling, and reset-complete actions.
- `proxy`: MEI component pointer, mutex, state flags, GSC BO/map halves, and CSME CPU buffers.

## State and Persistence
This state persists across the GT lifetime and is partially preserved across GT reset because firmware can remain loaded. `work_actions` is a bitmask updated under a spinlock; proxy component usage is serialized by a mutex.

## Dependencies and Integration
Includes uC firmware types, device types, iosys maps, workqueue, spinlock, and mutex primitives. The structure is consumed by GSC firmware load, proxy, submit, debugfs, and uC container code.

## Risks and Test Signals
- Workqueue and queue pointers are optional until post-hwconfig init; callers must check firmware loadability and queue presence.
- Proxy buffers split a single BO and a single CPU allocation into two directional halves; any size changes must preserve this invariant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gsc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.c

## Purpose
Implements core Xe GT allocation, initialization, hardware setup, reset/restart, suspend/resume, runtime PM, default LRC capture, user engine accounting, and wedged handling.

## Important APIs and Functions
- Lifecycle: `xe_gt_alloc`, `xe_gt_init_early`, `xe_gt_init`, `xe_gt_mmio_init`, `xe_gt_sanitize`, `xe_gt_suspend_prepare`, `xe_gt_suspend`, `xe_gt_resume`, `xe_gt_runtime_suspend`, `xe_gt_runtime_resume`, and `xe_gt_shutdown`.
- Reset: `xe_gt_reset_async`, inline `xe_gt_reset`/`xe_gt_wait_for_reset` from the header, `gt_reset_worker`, `do_gt_reset`, and `do_gt_restart`.
- Engine lookup/accounting: `xe_gt_record_user_engines`, `xe_gt_hw_engine`, `xe_gt_any_hw_engine_by_reset_domain`, and `xe_gt_any_hw_engine`.
- Context state: `xe_gt_record_default_lrcs`, `emit_wa_job`, `emit_nop_job`, and `emit_job_sync`.
- Workarounds/features: host L2 VRAM enable/disable, compression 1W coherence enable, `wa_14026539277`, and `xe_gt_sanitize_freq`.

## Control Flow
- Allocation sets `gt->tile` and chooses an ordered workqueue, sharing the primary GT workqueue for certain SR-IOV VF media GTs.
- Early init initializes PF/VF SR-IOV data, register save/restore state, workarounds/tunings, forcewake, TLB invalidation, MOCS, MMIO, uC noalloc state, stats, MCR early state, and PAT.
- Main init registers devm cleanup, sysfs, forcewake-protected uC/topology/MCR/engine/sysfs/CCS setup, idle/frequency sysfs, all-forcewake hardware setup, uC load, default CCS mode, SR-IOV PF hardware setup, user engine accounting, EU stall, and VF late init.
- Reset worker sanitizes submission, takes all forcewake, stops PF/VF/uC/pagefault/TLB state, applies GSC reset workaround around GDRST, restarts hardware/uC/SR-IOV state, restores frequency, and releases the runtime PM reference.
- Suspend/runtime suspend disable submission/uC and powergating-related hardware state; resume/runtime resume reinitializes hardware state and uC.

## State and Persistence
- Persistent GT state includes workqueues, reset work, forcewake, MMIO accessor, MCR steering, register save/restore, default LRC images, engine masks, user engine counts, frequency/idle sysfs kobjects, and SR-IOV data.
- Reset loses hardware programming and GuC/PF pushed configuration, so `do_gt_restart` reapplies PAT, MCR defaults, register SR, WOPCM, engine rings, uC, LMEM translation, SR-IOV PF HW, MOCS, engine SR, CCS mode, and GuC start.
- `xe_gt_sanitize_freq` restores GuC PC-stashed frequencies once GSC is loaded, absent, or in error for a specific workaround.

## Dependencies and Integration Points
Central integration point for most Xe subsystems: forcewake, MMIO, GuC/HuC/GSC uC, GGTT, LMEM LMTT, migration, MCR, MOCS, PAT, TLB invalidation, pagefaults, sysfs/debugfs, SR-IOV PF/VF, GT topology, ring ops, workarounds, and scheduling jobs.

## Risks and Edge Cases
- Init ordering is fragile: many operations require specific forcewake domains, MMIO adjustment for media GTs, or uC availability.
- Reset failure wedges the device; partial restart must not leave forcewake or runtime PM refs leaked.
- Default LRC capture submits real jobs on every engine and can fail if workarounds or engine state are invalid.
- SR-IOV PF/VF paths diverge significantly, with VF reset delegated and PF restart queued asynchronously after GT restart.

## Test Signals
- Probe/init tests should cover main and media GTs, SR-IOV PF/VF modes, DGFX/integrated memory, and CCS-capable compute configurations.
- Reset fault injection via `gt_reset_failure` should exercise wedge paths and PM ref cleanup.
- Suspend/resume and runtime PM tests should verify uC reload, powergating, host L2 VRAM workaround, and frequency restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.h

## Purpose
Declares the core GT API, engine iteration helpers, reset wrappers, GT type helpers, and selected topology/engine macros.

## Important APIs and Macros
- `for_each_hw_engine` iterates valid hardware engines in `gt->hw_engines`.
- `RCS_INSTANCES`, `VCS_INSTANCES`, `VECS_INSTANCES`, `CCS_INSTANCES`, and `GSCCS_INSTANCES` derive instance masks from `gt->info.engine_mask`.
- Lifecycle/reset declarations mirror `xe_gt.c`.
- Inline helpers identify main/media GTs, USM-reserved hardware engines, indirect ring-state support, and VF recovery pending state.
- `xe_fault_inject_gt_reset` exposes debugfs fault injection when configured.

## Integration and Risks
This header is broadly included by Xe subsystems. Macros assume valid GT info masks and stable enum bit layout. `xe_gt_reset` is synchronous only because it queues and then flushes reset work; callers must be prepared for PM and reset side effects.

## Test Signals
Compilation across PF/VF and debugfs-disabled configs is important because inline helpers depend on configuration and included SR-IOV VF declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.c

## Purpose
Implements compute-slice-to-CCS-engine mode programming and sysfs controls for selecting how many compute engines are exposed for available compute slices.

## Important APIs and Functions
- `xe_gt_apply_ccs_mode` applies `gt->ccs_mode` to the `CCS_MODE` register when enabled and not in SR-IOV VF.
- `xe_gt_ccs_mode_sysfs_init` creates `ccs_mode` and `num_cslices` sysfs attributes.
- `ccs_mode_store` validates a requested engine count, ensures no active DRM clients, handles PF lockdown when leaving/returning to default, records user engines, and triggers GT reset.

## Control Flow
`__xe_gt_apply_ccs_mode` starts with all compute slices disabled, iterates available CCS hardware engines, assigns fused-on slices evenly across the requested engine count, builds a user-visible engine mask, writes masked `CCS_MODE`, and logs the configuration.

## State and Persistence
`gt->ccs_mode` is the persistent software selection. Hardware state is reapplied during init and GT restart. User engine accounting is refreshed when the mode changes because exposed compute engines change.

## Dependencies and Integration Points
Depends on GT sysfs, runtime PM, MMIO, SR-IOV PF lockdown helpers, engine masks, and GT reset. Integrated during GT init after early hardware engine init and during `do_gt_restart`.

## Risks and Test Signals
- Invalid mode requests are rejected unless the number of slices is exactly divisible by requested engines.
- Sysfs changes require no open DRM clients; tests should verify `-EBUSY` with active clients and `-EINVAL` for non-divisible modes.
- PF lockdown around default-mode transitions protects active VFs; SR-IOV tests should cover enabled VF rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.h

## Purpose
Declares CCS mode programming/sysfs helpers and a small predicate for whether CCS mode is meaningful on a GT.

## Important APIs
- `xe_gt_apply_ccs_mode(struct xe_gt *gt)` writes the currently selected CCS mode to hardware.
- `xe_gt_ccs_mode_sysfs_init(struct xe_gt *gt)` installs sysfs controls.
- `xe_gt_ccs_mode_enabled` returns true when more than one CCS instance is present.

## Integration and Risks
The inline predicate depends on `CCS_INSTANCES(gt)` from `xe_gt.h`; callers should only expose or apply mode when multiple compute engines exist and must still respect SR-IOV VF restrictions in implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_ccs_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.c

## Purpose
Reads GT reference clock information from `RPM_CONFIG0` and provides conversion from GT clock ticks to milliseconds.

## Important APIs and Functions
- `xe_gt_clock_init` reads crystal clock frequency and CTC shift, stores `gt->info.reference_clock` and `gt->info.timestamp_base`.
- `xe_gt_clock_interval_to_ms` converts a tick count using `mul_u64_u32_div`.
- `read_crystal_clock` decodes supported 19.2, 24, 25, and 38.4 MHz crystal clock encodings and logs invalid values.

## Control Flow and State
Initialization reads one MMIO register, decodes the base frequency/timestamp base, applies the command timestamp shift, and stores results in GT info. No dynamic state is allocated.

## Dependencies and Integration Points
Called from all-forcewake GT init before engine/uC post-hwconfig work. Consumers use the stored reference clock for timing conversions.

## Risks and Test Signals
- Invalid crystal encoding stores zero frequency and timestamp base; downstream conversions would divide by zero if called without guarding, so platform tables/MMIO access must be correct.
- Platform tests should verify expected reference clock on each hardware generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.h

## Purpose
Declares GT clock initialization and interval conversion helpers.

## Important APIs
- `xe_gt_clock_init(struct xe_gt *gt)` initializes clock fields in `gt->info`.
- `xe_gt_clock_interval_to_ms(struct xe_gt *gt, u64 count)` converts GT ticks to milliseconds.

## Integration and Risks
Callers must ensure `xe_gt_clock_init` has run and produced a nonzero reference clock before using conversion. The header keeps dependencies minimal with only `linux/types.h` and a GT forward declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.c

## Purpose
Creates per-GT debugfs directories and diagnostic/control files for topology, workarounds, register save/restore, engines, MOCS, PAT, powergating, stats, default LRCs, force reset, uC, and SR-IOV-specific views.

## Important APIs and Functions
- `xe_gt_debugfs_register` creates `tile#/gt#` debugfs directories and a legacy symlink, then registers safe and PF-only files.
- Shared show callbacks: `xe_gt_debugfs_simple_show` and `xe_gt_debugfs_show_with_rpm`.
- Diagnostic printers include `hw_engines`, `steering`, `register_save_restore`, `register_save_restore_check`, default LRC dumpers, and `hwconfig`.
- Writable controls: `stats` clears GT stats; `force_reset` queues async reset; `force_reset_sync` performs synchronous reset.

## Control Flow
The GT dentry stores `struct xe_gt *` in `i_private`; `node_to_gt` recovers it from the parent dentry for DRM info callbacks. Registration always creates VF-safe files and only adds privileged PF-only MMIO views when not an SR-IOV VF. uC and SR-IOV PF/VF debugfs registration is delegated after base GT files are installed.

## State and Persistence
No core GT state is owned here, but debugfs write paths mutate GT stats or trigger reset. Runtime PM guards are used for files that read live hardware state.

## Dependencies and Integration Points
Integrates DRM debugfs, runtime PM, forcewake, GT MCR, idle, SR-IOV PF/VF debugfs, stats, topology, GuC hwconfig, LRC, MOCS, PAT, register SR, tuning, uC debugfs, and workaround dumping.

## Risks and Test Signals
- Debugfs read paths that access privileged registers must remain VF-gated to avoid invalid VF MMIO access.
- Force-reset debugfs reads trigger reset for backward compatibility; tests should prefer write path but retain legacy behavior awareness.
- `register-save-restore-check` should be useful after init/resume/reset to catch missing register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.h

## Purpose
Declares GT debugfs registration and common DRM info-list show callbacks.

## Important APIs
- `xe_gt_debugfs_register(struct xe_gt *gt)` installs the per-GT debugfs tree.
- `xe_gt_debugfs_simple_show` delegates to a GT printer stored in `drm_info_list.data`.
- `xe_gt_debugfs_show_with_rpm` wraps the simple callback with runtime PM.

## Integration and Risks
The shared callbacks are used by GT and SR-IOV debugfs files. Callers must set up dentry private data and `drm_info_list.data` consistently or the helper will warn and return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.c

## Purpose
Exposes GT frequency management through per-GT sysfs attributes backed by GuC SLPC/PC frequency controls.

## Important APIs and Functions
- `xe_gt_freq_init` creates `freq0` under the GT sysfs directory, installs attributes, registers cleanup, and initializes throttle reporting.
- Read-only attributes: `act_freq`, `cur_freq`, `rpn_freq`, `rpa_freq`, `rpe_freq`, and `rp0_freq`.
- Read-write attributes: `min_freq`, `max_freq`, and `power_profile`.
- Helper accessors translate sysfs kobjects back to `struct xe_guc_pc` and `struct xe_device`.

## Control Flow and State
Initialization is skipped when `xe->info.skip_guc_pc` is true. Attribute reads/writes take runtime PM where live GuC PC access is needed, call the corresponding `xe_guc_pc_*` function, and return sysfs-formatted values. Cleanup removes files and drops the kobject.

## Dependencies and Integration Points
Depends on GT sysfs, GuC PC, throttle sysfs/support, runtime PM, and DRM managed cleanup. Called from `xe_gt_init` after idle/sysfs and before all-forcewake hardware init.

## Risks and Test Signals
- Min/max writes propagate GuC PC validation errors directly; sysfs tests should cover invalid frequency ranges and suspended-device reads.
- `power_profile_show` relies on GuC PC writing a NUL-terminated string into the buffer.
- Presence/absence of `freq0` should match `skip_guc_pc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.h

## Purpose
Declares GT frequency sysfs initialization.

## Important API
- `xe_gt_freq_init(struct xe_gt *gt)` creates and wires the `freq0` sysfs interface when GuC PC is available.

## Integration and Risks
The API must be called after GT sysfs and GuC PC state are ready. It returns errors for kobject/file creation and can be skipped by implementation for platforms that disable GuC PC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.c

## Purpose
Implements GT idle/powergating sysfs and helpers for enabling/disabling render/media/GSC power gating and RC6/C6 idle state management.

## Important APIs and Functions
- Public APIs: `xe_gt_idle_init`, `xe_gt_idle_enable_pg`, `xe_gt_idle_disable_pg`, `xe_gt_idle_enable_c6`, `xe_gt_idle_disable_c6`, `xe_gt_idle_pg_print`, and `xe_gt_idle_residency_msec`.
- Sysfs attributes under `gtidle`: `name`, `idle_status`, and `idle_residency_ms`.
- Residency helpers track 32-bit counter wrap and convert raw residency with a 1280 ns multiplier.

## Control Flow
- `xe_gt_idle_init` skips SR-IOV VFs, creates `gtidle`, initializes lock and function pointers, names the GT idle state as render or media, creates sysfs files, and enables powergating.
- `xe_gt_idle_enable_pg` builds `powergate_enable` from available render/media engines, media version, platform exceptions, and workarounds, then writes `POWERGATE_ENABLE` under GT forcewake.
- `xe_gt_idle_pg_print` avoids waking the GT when already C6, otherwise reads live powergate enable/status registers and prints render/media/GSC status plus forcewake domain counters.
- C6 helpers program `RC_IDLE_HYSTERSIS`, `RC_CONTROL`, and `RC_STATE`.

## State and Persistence
`struct xe_gt_idle` stores name, last programmed powergate mask, residency multiplier, extended residency counters, and function pointers into GuC PC. Runtime reads update `prev_residency` and `cur_residency` under a raw spinlock.

## Dependencies and Integration Points
Depends on GT sysfs, GuC PC idle/residency hooks, forcewake, MMIO, runtime PM, engine masks, SR-IOV gating, platform/workaround flags, and GT debugfs powergate printing.

## Risks and Test Signals
- Residency wrap handling assumes queries are frequent enough that a 32-bit counter does not wrap multiple times between reads.
- Powergating is not supported or skipped on PVC and VFs; tests should verify sysfs absence/behavior by platform.
- Workaround `14020316580` masks selected media powergates and should be validated on affected platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.h

## Purpose
Declares GT idle, powergating, C6, debug printing, and residency APIs.

## Important APIs
- `xe_gt_idle_init` initializes `struct xe_gt_idle` and sysfs.
- `xe_gt_idle_enable_pg` / `xe_gt_idle_disable_pg` control powergating bits.
- `xe_gt_idle_enable_c6` / `xe_gt_idle_disable_c6` control RC6/C6.
- `xe_gt_idle_pg_print` emits debugfs powergate state.
- `xe_gt_idle_residency_msec` returns extended residency in milliseconds.

## Integration and Risks
The header includes `xe_gt_idle_types.h` so callers can embed/use the state object. Most operations require valid GT memory/MMIO access; implementation skips SR-IOV VFs for hardware programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle_types.h

## Purpose
Defines the idle state enum and `struct xe_gt_idle` used by GT idle sysfs and power management.

## Important Types
- `enum xe_gt_idle_state` distinguishes active C0, idle C6, and unknown state.
- `struct xe_gt_idle` stores name, powergate mask, residency multiplier, extended residency counters, lock, and GuC PC function pointers for state/residency reads.

## State and Integration
The struct is embedded in `struct xe_gt`. Its counters are updated under `raw_spinlock_t` to make residency reads safe against concurrent sysfs/PMU access.

## Risks and Test Signals
Function pointers must be initialized before any sysfs/PMU read. Residency counters depend on monotonic hardware counter reads and wrap handling in `xe_gt_idle.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_idle_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.c

## Purpose
Implements GT multicast/replicated register steering. It identifies non-terminated hardware instances for MCR register ranges and serializes unicast/multicast MMIO access through software and hardware steering locks.

## Important APIs and Functions
- Initialization: `xe_gt_mcr_init_early`, `xe_gt_mcr_init`, and `xe_gt_mcr_set_implicit_defaults`.
- Steering helpers: `xe_gt_mcr_get_nonterminated_steering`, `xe_gt_mcr_get_dss_steering`, and `xe_gt_mcr_steering_info_to_dss_id`.
- Accessors: `xe_gt_mcr_unicast_read_any`, `xe_gt_mcr_unicast_read`, `xe_gt_mcr_unicast_write`, and `xe_gt_mcr_multicast_write`.
- Diagnostics: `xe_gt_mcr_steering_dump`.
- Platform data: many `xe_mmio_range` tables map register ranges to L3BANK, NODE, MSLICE, LNCF, DSS/XeCore, OADDRM/GPMXMT, SQIDI/PSMI, GAM1, INSTANCE0, or implicit steering.

## Control Flow
- Early init selects platform/media/main GT steering tables, initializes `mcr_lock`, and marks INSTANCE0 initialized for early VRAM/CCS probing.
- Normal init computes group/instance targets for each steering type using fuse registers, topology masks, GuC hwconfig, and platform generation rules.
- `xe_gt_mcr_get_nonterminated_steering` finds the table containing a register and returns target group/instance; implicit ranges require no per-access steering.
- Accessors take `mcr_lock`; on MTL+ they also acquire `STEER_SEMAPHORE`, program `MTL_MCR_SELECTOR` or `MCR_SELECTOR`, perform read/write, restore multicast mode for unicast writes, release the hardware semaphore, and unlock.

## State and Persistence
`gt->steering[]` stores range tables, initialized flags, and target group/instance values. `gt->steering_dss_per_grp` records DSS layout. `gt->mcr_lock` serializes all steering changes. Hardware selector/semaphore state is transient but must be restored to multicast-friendly defaults.

## Dependencies and Integration Points
Used by GT init, register save/restore, PAT, MOCS, workarounds, VRAM/flat CCS probing, GuC ADS, OA/EU stall code, and debugfs steering dumps. Depends on platform version, fuse topology, GuC hwconfig, MMIO, and SR-IOV gating.

## Risks and Edge Cases
- MCR registers are unavailable on SR-IOV VFs; accessors assert not VF.
- Missing table entries fall back to steering 0/0 with a warning, which may read terminated instances on new platforms until tables are updated.
- Hardware semaphore acquisition timeout only warns; subsequent access may still race external firmware steering.
- DSS-per-group fallback values are used when GuC hwconfig lacks layout attributes, which is risky on newer platforms.

## Test Signals
- Debugfs `steering` should show expected ranges and targets per platform.
- Register save/restore readback checks exercise MCR reads/writes.
- Platform bring-up should validate MCR table coverage warnings and nonzero reads for known fused configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.h

## Purpose
Declares MCR initialization, steering lookup, MCR register accessors, diagnostics, and DSS steering iteration helpers.

## Important APIs
- Init/defaults: `xe_gt_mcr_init_early`, `xe_gt_mcr_init`, `xe_gt_mcr_set_implicit_defaults`.
- Accessors: unicast read-any, explicit unicast read/write, and multicast write.
- Steering conversion: `xe_gt_mcr_get_nonterminated_steering`, `xe_gt_mcr_get_dss_steering`, `xe_gt_mcr_steering_info_to_dss_id`.
- `for_each_dss_steering` wraps topology DSS iteration with steering conversion.

## Integration and Risks
Callers must hold appropriate forcewake domains before MCR MMIO access. The API is PF/native only; implementation asserts against SR-IOV VF use. `for_each_dss_steering` depends on initialized GT topology and steering layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_mcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_printk.h

## Purpose
Defines GT-scoped logging macros and DRM printer constructors that prefix messages with GT identity through tile-aware logging.

## Important APIs and Macros
- Logging macros: `xe_gt_err`, `xe_gt_err_once`, `xe_gt_err_ratelimited`, `xe_gt_warn`, `xe_gt_notice`, `xe_gt_info`, and `xe_gt_dbg`.
- Warning macros: `xe_gt_WARN`, `xe_gt_WARN_ONCE`, `xe_gt_WARN_ON`, and `xe_gt_WARN_ON_ONCE`.
- Printer constructors: `xe_gt_err_printer`, `xe_gt_info_printer`, and `xe_gt_dbg_printer`.

## Control Flow and State
Macros format messages as `GT%u: ...` and delegate to tile logging. Printer callbacks recover `struct xe_gt *` from `drm_printer.arg`; the debug printer preserves origin by redirecting through `xe_tile_dbg_printer`.

## Dependencies and Integration Points
Used throughout GT, GSC, SR-IOV, MCR, and debug code for consistent log attribution. Depends on `xe_gt_types.h` and `xe_tile_printk.h`.

## Risks and Test Signals
- Callers must pass a valid `struct xe_gt *`; macros dereference `gt->info.id` and `gt->tile`.
- Printer callbacks are useful when dumping KLVs or debug state through existing logging levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.c

## Purpose
Coordinates per-GT SR-IOV Physical Function setup, hardware enablement, restart work, VF scratch sanitization, and readiness waits.

## Important APIs and Functions
- Public PF lifecycle: `xe_gt_sriov_pf_init_early`, `xe_gt_sriov_pf_init`, `xe_gt_sriov_pf_init_hw`, `xe_gt_sriov_pf_stop_prepare`, `xe_gt_sriov_pf_restart`, and `xe_gt_sriov_pf_wait_ready`.
- VF resource/hardware helpers: `xe_gt_sriov_pf_sanitize_hw` and `xe_gt_sriov_pf_sched_groups_enabled`.
- Internal worker flow: `pf_init_workers`, `pf_queue_restart`, `pf_worker_restart_func`, `pf_restart`, `pf_flush_restart`, and cancellation/fini helpers.

## Control Flow
- Early init allocates PF/VF metadata, initializes service and control layers, and prepares restart work.
- Late init initializes config, policy, migration, and devm cleanup.
- Hardware init enables guest GGTT updates on selected platforms and refreshes PF service state.
- GT restart queues a worker on `xe->sriov.wq`; the worker repushes PF config/control state and releases a runtime PM reference taken at queue time.
- Stop prepare cancels pending restart work to avoid racing GT teardown.

## State and Persistence
`gt->sriov.pf.vfs` is a flexible array indexed with PF at 0 and VFs at 1..n. Restart work is persistent per GT and protected by runtime PM references while queued.

## Dependencies and Integration Points
Integrates PF config/control/service/policy/migration modules, GuC submission stopped state, GGTT guest update register programming, runtime PM, and GT reset/restart.

## Risks and Test Signals
- Restart work must not leak runtime PM references when already queued or canceled.
- `xe_gt_sriov_pf_wait_ready` returns `-EBUSY` if GuC is stopped, so callers should distinguish reset-in-progress from permanent failure.
- PF init ordering is important: config push requires GuC CT and resource managers to be available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.h

## Purpose
Declares the per-GT SR-IOV PF interface and provides no-op stubs when PCI IOV support is disabled.

## Important APIs
- Init/restart/readiness: `xe_gt_sriov_pf_init_early`, `xe_gt_sriov_pf_init`, `xe_gt_sriov_pf_init_hw`, `xe_gt_sriov_pf_restart`, and `xe_gt_sriov_pf_wait_ready`.
- Stop/sanitize: `xe_gt_sriov_pf_stop_prepare`, `xe_gt_sriov_pf_sanitize_hw`.
- Policy query: `xe_gt_sriov_pf_sched_groups_enabled`.

## Integration and Risks
When `CONFIG_PCI_IOV` is disabled most APIs become harmless stubs, but `xe_gt_sriov_pf_wait_ready` and `xe_gt_sriov_pf_sanitize_hw` are only declared in the enabled block. Callers must be guarded consistently by SR-IOV/PF configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.c

## Purpose
Owns per-GT SR-IOV PF provisioning state and pushes VF/PF configuration to GuC as KLVs. It provisions GGTT, LMEM/VRAM, GuC context IDs, doorbells, execution quantum, preemption timeout, scheduler priority, adverse-event thresholds, save/restore blobs, sanitization, and debug printouts.

## Important APIs and Functions
- Resource getters/setters: `xe_gt_sriov_pf_config_get/set/bulk/fair_ggtt`, `_ctxs`, `_dbs`, and `_lmem`.
- Scheduling controls: `xe_gt_sriov_pf_config_get/set_exec_quantum`, locked/bulk variants, group execution quantum APIs, preempt timeout APIs, group preempt timeout APIs, and scheduler priority APIs.
- Threshold controls: `xe_gt_sriov_pf_config_get_threshold` and `xe_gt_sriov_pf_config_set_threshold`.
- Lifecycle and operations: `xe_gt_sriov_pf_config_init`, `xe_gt_sriov_pf_config_restart`, `xe_gt_sriov_pf_config_release`, `xe_gt_sriov_pf_config_sanitize`, `xe_gt_sriov_pf_config_push`, `xe_gt_sriov_pf_config_is_empty`, `xe_gt_sriov_pf_config_save`, and `xe_gt_sriov_pf_config_restore`.
- Migration/data helpers: `xe_gt_sriov_pf_config_ggtt_save`, `xe_gt_sriov_pf_config_ggtt_restore`, and `xe_gt_sriov_pf_config_get_lmem_obj`.
- Debug printers: config print functions for GGTT, contexts, doorbells, LMEM, and available GGTT.

## Control Flow
- GuC updates flow through `guc_action_update_vf_cfg`, `pf_send_vf_cfg_reset`, and KLV push helpers. Push replies must equal the number of KLVs sent or the code reports `-ENOKEY`/`-EPROTO`.
- Configuration is selected with `pf_pick_vf_config` under `xe_gt_sriov_pf_master_mutex(gt)`.
- Full config encoding writes KLVs for GGTT, contexts, doorbells, LMEM, scheduling, and thresholds; media GT config borrows GGTT from the primary GT, while PF self config fakes full GGTT coverage.
- Provisioning a resource generally clears old GuC config to zero, releases local resource, refreshes full config, allocates/reserves new resource, pushes new KLVs, and rolls back on failure.
- Fair provisioning estimates available resources after PF spare reservations, clamps to platform/profile limits, and bulk provisions a VF range.
- Restart pushes PF self config, skips empty VFs, and repushes all non-empty VF configs after GT reset because GuC lost previous KLV state.
- Restore parses a saved KLV stream, resets GuC/local config first, then provisions each recognized key and validates mandatory configuration.

## State and Persistence
- Persistent per-function data is in `gt->sriov.pf.vfs[vfid].config`; PF spare reservations are in `gt->sriov.pf.spare`.
- GGTT state is represented by assigned `xe_ggtt_node`s; LMEM state by pinned VRAM BOs and optional LMTT page tables across tiles; contexts and doorbells are ranges reserved in GuC managers.
- Execution quantum/preempt timeout arrays hold per scheduler group values; scalar APIs replicate one value across all groups. Thresholds are stored by `xe_guc_klv_threshold_index`.
- Devm cleanup releases all VF configs at driver teardown.

## Dependencies and Integration Points
Depends on GuC CT, GuC KLV ABI/helpers, GuC ID and doorbell managers, GGTT, LMEM/TTM VRAM manager, LMTT, migration clear, WOPCM/GGTT ranges, SR-IOV PF policy/provision/debugfs/migration/control code, and GT logging.
- Provisioning APIs are called by `xe_sriov_pf_provision.c`.
- Print and config blob APIs are consumed by SR-IOV PF debugfs.
- GGTT/LMEM object save/restore is used by SR-IOV migration.
- Sanitization is called by PF control when resetting or preparing VFs.

## Risks and Edge Cases
- All mutation assumes the PF master mutex is held; locked APIs assert this and unlocked APIs take the mutex internally.
- Some release paths call `pf_release_vf_config_ggtt` without null checks; current callers are expected to only release configured nodes or rely on lower helpers tolerating null if they do.
- Fair resource profiles contain preliminary hard-coded values and debug-build caps, so production provisioning should be validated against platform resource maps.
- LMEM provisioning requires LMTT support and DGFX; failures after BO allocation must reset LMTT and release pinned BOs.
- Restore rejects unsupported KLVs on media GT and thresholds unsupported by current GuC firmware.
- Partial bulk provisioning logs prior successes and the failed VF, but leaves already-provisioned VFs changed.

## Test Signals
- The file includes `tests/xe_gt_sriov_pf_config_kunit.c` when built for Xe KUnit, indicating direct unit coverage exists for provisioning logic.
- Integration tests should cover GuC KLV push counts, GGTT allocation/spare enforcement, LMEM/LMTT update across tiles, context/doorbell manager reservations, fair provisioning, config save/restore, reset restart repush, and forced release after GuC failure.
- Debugfs printouts for GGTT/ctxs/dbs/LMEM and provisioning sysfs/debugfs controls provide observable state for manual validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.h

## Purpose
Declares the SR-IOV PF provisioning API for per-VF resources, scheduling controls, thresholds, save/restore, lifecycle, and diagnostics.

## Important APIs
- Resource provisioning: GGTT, contexts, doorbells, and LMEM each expose get/set, fair, and bulk functions, with LMEM additionally exposing locked variants and BO reference acquisition.
- Scheduling: execution quantum and preemption timeout expose scalar, locked, bulk-locked, and scheduler-group APIs; scheduler priority has get/set.
- Thresholds: generic get/set by `enum xe_guc_klv_threshold_index`.
- Operations: `set_fair`, `sanitize`, `release`, `push`, `save`, `restore`, GGTT save/restore, `is_empty`, `init`, and `restart`.
- Diagnostics: print functions for GGTT, contexts, doorbells, LMEM, and available GGTT.

## Integration and Risks
This header is the contract used by PF provisioning, debugfs, migration, and control modules. Locked APIs require the PF master mutex to already be held; misuse can deadlock or trip lockdep assertions. Callers must distinguish PFID (`0`) spare/self configuration from VFIDs (`1..n`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config_types.h

## Purpose
Defines persistent configuration data structures used by the SR-IOV PF provisioning module.

## Important Types and Fields
- `struct xe_gt_sriov_config` stores per-PF/VF assigned resources: GGTT node, LMEM BO, GuC context range, doorbell range, per-scheduler-group execution quantum and preempt timeout, scheduler priority, and GuC threshold values.
- `struct xe_gt_sriov_spare_config` stores PF spare reservations for GGTT, LMEM, context IDs, and doorbells that constrain fair/available provisioning.

## State and Persistence
Instances live under `gt->sriov.pf.vfs[]` for PF/VF config and `gt->sriov.pf.spare` for spare config. Pointers reference resources owned elsewhere (`xe_ggtt_node`, `xe_bo`) and must be released by config teardown.

## Dependencies and Integration
Depends on GuC scheduler ABI group count, GGTT node type, and GuC KLV threshold count. The structures are mutated under the PF master mutex by `xe_gt_sriov_pf_config.c`.

## Risks and Test Signals
- Array sizes are ABI-coupled to GuC scheduler groups and threshold enumerations; KLV encoding has build-time checks for group lengths.
- Tests should verify zero-initialized config means no assigned VF resources except PF self config prepared at init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_config_types.h -->
