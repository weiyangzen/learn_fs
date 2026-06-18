# Research: subset-b-003616

This grouped report covers the GuC capture, command transport, debugfs, firmware upload, firmware ABI, hardware configuration, logging, runtime control, register, and SLPC files listed for `subset-b-003616`. Each source section is bounded by reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.c

Purpose: implements GuC error-state capture support for i915. It defines platform-specific MMIO register capture lists, converts them into GuC ADS input lists, parses GuC-produced capture output from the capture log buffer, keeps parsed capture nodes for later matching to engine coredumps, and prints matched captures into the i915 error state.

Important APIs, types, and functions:
- Static register descriptor tables cover Gen8 and Xe-LP global, engine-class, and engine-instance registers. Macros such as `MAKE_REGLIST`, `COMMON_BASE_ENGINE_INSTANCE`, and `COMMON_GEN12BASE_GLOBAL` build `__guc_mmio_reg_descr_group` arrays consumed by ADS.
- `guc_capture_alloc_steered_lists()` dynamically builds extra render-class MCR/steered register entries per slice/subslice and stores them in `guc->capture->extlists`.
- `intel_guc_capture_getlistsize()`, `intel_guc_capture_getlist()`, and `intel_guc_capture_getnullheader()` are ADS-facing entry points. They size, allocate, populate, and cache GuC capture list blobs.
- `intel_guc_capture_process()` drives runtime parsing by calling `__guc_capture_process_output()` on the capture section of the GuC log buffer.
- `guc_capture_extract_reglists()` parses GuC capture group headers, per-list headers, and `guc_mmio_reg` entries into `__guc_capture_parsed_output` nodes.
- `intel_guc_capture_is_matching_engine()` and `intel_guc_capture_get_matching_node()` match parsed GuC nodes to an i915 context/engine by GuC engine class, instance, context id, and masked LRCA.
- `intel_guc_capture_print_engine_node()` prints capture contents under `CONFIG_DRM_I915_CAPTURE_ERROR`.
- `intel_guc_capture_init()` allocates `guc->capture`, chooses device register lists, initializes output/cache lists, and warns if the capture log section may be undersized. `intel_guc_capture_destroy()` frees ADS caches, parsed nodes, extension lists, and state.

Control flow:
- Initialization allocates `intel_guc_state_capture`, chooses Gen8 or Xe-LP register groups by graphics version, optionally builds steered extension lists, and estimates the minimum capture output footprint against `intel_guc_log_section_size_capture()`.
- ADS population calls `intel_guc_capture_getlist()` repeatedly for owner/type/class combinations. The function preallocates parsed-output nodes on first use, checks/caches list size, fills a `guc_debug_capture_list` header and descriptors, and stores the blob in `ads_cache`.
- Runtime G2H state-capture notifications arrive through CT handling and eventually call `intel_guc_capture_process()`. The code snapshots the GuC log buffer state, detects overflow with `intel_guc_check_log_buf_overflow()`, constructs a byte-ring view, and repeatedly parses capture groups until no complete group remains.
- Parsed output nodes are added to `outlist`; coredump capture later removes the matching node from `outlist`, attaches it to `intel_engine_coredump`, derives legacy `ipehr`/`instdone` values, prints it, then returns the node to `cachelist`.

State and persistence:
- Persistent driver state hangs off `guc->capture`: selected static `reglists`, dynamic `extlists`, ADS list cache (`ads_cache`), null header cache, maximum MMIO entries per parsed node, reusable `cachelist`, and pending parsed `outlist`.
- GuC capture data itself is transient and resides in the capture subsection of the shared GuC log VMA. The host advances `read_ptr` to `sampled_write_ptr` after extraction and sends `INTEL_GUC_ACTION_LOG_BUFFER_FILE_FLUSH_COMPLETE`.
- Parsed output nodes are recycled instead of repeatedly allocated. If the cache is empty, the oldest unclaimed `outlist` node may be stolen, which bounds memory but can lose older unclaimed capture data.

Dependencies and integration points:
- Depends on GuC firmware ABI structs and bitfields from `guc_capture_fwif.h` and `intel_guc_fwif.h`, log-buffer helpers from `intel_guc_log.c`, GT register definitions, MCR steering iteration, engine lookup, LRC/LRCA state, and i915 GPU error capture.
- Integrated with ADS setup through capture-list accessors, CT G2H dispatch via state-capture notifications, log flush completion, and i915 coredump printing/freeing.

Risks:
- Capture parsing is sensitive to firmware ABI layout, ring wrap behavior, and dword alignment. Bad offsets force whole-buffer copies or parse failure.
- The preallocated-node cap can clip oversized register lists, and node stealing can drop older unmatched captures under bursts.
- Matching requires GuC id, engine class/instance, and LRCA to agree; racey resets or stale contexts can leave capture nodes unmatched.
- Dynamic steered register list allocation silently skips on allocation failure, reducing diagnostic coverage.

Test signals:
- Exercise GuC submission reset/error paths and verify `STATE_CAPTURE_NOTIFICATION` produces coredump register sections.
- Validate ADS capture list sizes and contents across Gen8, Gen12/Xe-LP, and Xe-HPG steering configurations.
- Stress multiple back-to-back engine resets to check node reuse, partial capture handling, overflow warnings, and no leaks on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.h

Purpose: declares the public GuC capture interface used by ADS setup, GuC notification handling, and i915 GPU coredump code.

Important APIs, types, and functions:
- Forward declares `intel_guc`, `intel_gt`, `intel_context`, `intel_engine_cs`, and `intel_engine_coredump` to avoid pulling heavy headers into users.
- Declares lifecycle APIs `intel_guc_capture_init()` and `intel_guc_capture_destroy()`.
- Declares ADS-facing list APIs `intel_guc_capture_getlistsize()`, `intel_guc_capture_getlist()`, and `intel_guc_capture_getnullheader()`.
- Declares runtime/coredump APIs `intel_guc_capture_process()`, `intel_guc_capture_is_matching_engine()`, `intel_guc_capture_get_matching_node()`, `intel_guc_capture_print_engine_node()`, and `intel_guc_capture_free_node()`.

Control flow:
- Callers initialize capture state during GuC setup, request input register-list blobs during ADS construction, invoke processing when firmware reports capture data, attach matching nodes during error-state construction, and free attached nodes when the coredump is released.

State and persistence:
- The header owns no storage; all persistent state is embedded in `struct intel_guc` and the implementation-private capture structures allocated by `intel_guc_capture_init()`.

Dependencies and integration points:
- Bridges `intel_guc_capture.c` to ADS, CT/G2H error handling, and i915 GPU error reporting without exposing private parsed-node internals.

Risks:
- API users must respect ownership: `intel_guc_capture_getlist()` returns cached memory owned by capture state, while `intel_guc_capture_free_node()` returns an attached parsed node to the reuse cache.
- The print API depends on `CONFIG_DRM_I915_CAPTURE_ERROR`; callers must handle disabled or missing capture state.

Test signals:
- Compile coverage for all users of this header.
- Runtime capture tests should verify init/destroy pairing, ADS list retrieval, matching, print, and free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.c

Purpose: implements GuC Command Transport (CT), the shared-buffer transport replacing many MMIO command paths. It allocates H2G and G2H circular buffers, registers them with GuC, sends synchronous and nonblocking HXG messages, receives GuC events/responses, dispatches events to subsystem handlers, and reports dead CT conditions in debug builds.

Important APIs, types, and functions:
- Internal `ct_request` tracks synchronous request fence, status, and optional response buffer. `ct_incoming_msg` stores copied G2H messages for response/event processing.
- Lifecycle: `intel_guc_ct_init_early()`, `intel_guc_ct_init()`, `intel_guc_ct_enable()`, `intel_guc_ct_disable()`, and `intel_guc_ct_fini()`.
- Send path: `intel_guc_ct_send()` chooses `ct_send()` or `ct_send_nb()`. `ct_write()` encodes the CT header, HXG header, action data, fence, updates local/firmware tails, and notifies GuC.
- Flow control: `h2g_has_room()`, `g2h_has_room()`, G2H credit reserve/release helpers, `has_room_nb()`, and `ct_deadlocked()`.
- Receive path: `intel_guc_ct_event_handler()`, `ct_receive_tasklet_func()`, `ct_read()`, `ct_handle_msg()`, `ct_handle_hxg()`, `ct_handle_response()`, and `ct_handle_event()`.
- Event dispatch: `ct_process_request()` calls GuC submission, deregistration, context reset, state capture, engine failure, log flush, crash, and TLB invalidation handlers.
- Diagnostics: `intel_guc_ct_print_info()` and debug-only `ct_dead_ct_worker_func()` with `CT_DEAD()` reasons.

Control flow:
- Early init initializes locks, pending/incoming lists, work items, tasklet, and waitqueue.
- Full init allocates one GuC-mapped blob containing send/receive descriptors and buffers. Send is 4 KiB, receive is 16 KiB, and receive reserves one quarter for unexpected G2H traffic.
- Enable resets descriptors, registers receive then send buffer addresses/sizes via self-config KLVs, sends CTB enable over MMIO, and marks CT enabled.
- Synchronous sends reserve maximal G2H response space, insert a stack `ct_request` into the pending list, write the H2G message, notify GuC, wait for matching response by fence, handle retry responses, copy payload/status, then unlink and release credits.
- Nonblocking sends use `MAKE_SEND_FLAGS()`-style credit sizing, reserve expected G2H space, write with `FAST_REQUEST` type, notify GuC, and return without a pending request.
- Interrupt/event handling reads one G2H CTB message at a time under the receive lock. Responses update pending `ct_request`s. Events either release reserved credits and queue a work item, or process TLB invalidation completion immediately to unblock other flows.

State and persistence:
- `ct->vma` persists the descriptor/buffer blob until fini. Local `head`, `tail`, and `space` shadow firmware descriptor state.
- `ct->requests.pending` holds stack-backed synchronous requests while blocked. `ct->requests.incoming` holds heap-allocated G2H events waiting for workqueue processing.
- `ct->enabled`, per-buffer `broken`, and `stall_time` gate operations and deadlock detection. Debug builds keep lost-and-found fence/action records and dead-CT reporting state.

Dependencies and integration points:
- Uses GuC ABI headers for CTB/HXG bitfields and action ids, `intel_guc_send_mmio()` for CTB enable/disable, GuC self-config KLV helpers for buffer registration, and `intel_guc_notify()` for doorbell/interrupt notification.
- Dispatches to GuC submission, scheduling, deregistration, context reset, error capture, engine failure, log, crash, and TLB invalidation code.
- Uses Linux tasklets, workqueues, spinlocks, atomics, wait helpers, and circular-buffer macros.

Risks:
- CT is concurrency-sensitive: descriptor head/tail corruption, missed barriers, wrong G2H credit accounting, or processing events in the wrong context can deadlock GuC communication.
- Synchronous request objects are stack allocated; response handling must only reference them while linked and the caller is waiting.
- `ct_deadlocked()` has a probable typo assigning both `send` and `recv` descriptor pointers from `ct->ctbs.send.desc`, which can misreport receive descriptor status.
- Event dispatch failures mark CT dead in debug builds and can force broad error capture.

Test signals:
- Unit/selftest CT send paths for synchronous, retry, response payload, nonblocking, no-room, and disabled cases.
- Fault injection on `intel_guc_ct_init()` allocation and corrupted descriptor status/head/tail.
- Stress GuC submission with high G2H traffic, TLB invalidations, log flushes, and state capture notifications.
- Verify `intel_guc_ct_print_info()` and dead-CT klog capture under debug configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.h

Purpose: defines the public Command Transport structures, flags, and entry points used by GuC subsystems to initialize CT, send actions, receive events, and print transport state.

Important APIs, types, and functions:
- `struct intel_guc_ct_buffer` models one CT buffer descriptor and circular command area, including lock, descriptor pointer, command pointer, dword size, reserved space, local head/tail/space shadows, and broken flag.
- `struct intel_guc_ct` owns the GuC VMA blob, enabled flag, send/receive buffers, receive tasklet, waitqueue, pending/incoming request lists, worker, stall time, and optional debug tracking.
- `INTEL_GUC_CT_SEND_NB` marks fast/nonblocking sends; `INTEL_GUC_CT_SEND_G2H_DW_MASK` encodes expected G2H payload length; `MAKE_SEND_FLAGS(len)` builds checked nonblocking flags.
- Public APIs include `intel_guc_ct_init_early()`, `intel_guc_ct_init()`, `intel_guc_ct_enable()`, `intel_guc_ct_disable()`, `intel_guc_ct_fini()`, `intel_guc_ct_send()`, `intel_guc_ct_event_handler()`, `intel_guc_ct_print_info()`, and `intel_guc_ct_max_queue_time_jiffies()`.

Control flow:
- Subsystems call init early before hardware access, full init after GuC allocation support is available, enable when GuC is ready, send actions while enabled, handle GuC interrupts through `intel_guc_ct_event_handler()`, then disable/fini during teardown/reset.

State and persistence:
- CT buffer state persists inside `struct intel_guc`. The header exposes enough state for inline enabled/sanitize checks but keeps message parsing and request internals in the C file.

Dependencies and integration points:
- Includes Linux interrupt/spinlock/stackdepot/workqueue/time/wait headers and `intel_guc_fwif.h` for CT descriptor ABI.
- Used by GuC action send wrappers and debugfs status paths.

Risks:
- Direct field access by external code should remain limited; misusing `enabled`, local head/tail, or send flags can break CT invariants.
- `MAKE_SEND_FLAGS()` relies on callers supplying payload dwords without the HXG header length; mismatches affect G2H credit accounting.

Test signals:
- Compile coverage with debug and non-debug configurations.
- Send-flag users should be audited or tested for correct expected G2H length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.c

Purpose: registers GuC debugfs files for status, registered contexts, SLPC status, scheduler-disable tuning, and GuC log debugfs integration.

Important APIs, types, and functions:
- `guc_info_show()` prints firmware load status, log info, and, when GuC submission is used, CT state, submission info, and ADS policy info.
- `guc_registered_contexts_show()` prints GuC-registered context information when GuC submission is active.
- `guc_slpc_info_show()` prints SLPC state via `intel_guc_slpc_print_info()`.
- `guc_sched_disable_delay_ms_get/set()` exposes and clamps scheduler disable delay to 60 seconds.
- `guc_sched_disable_gucid_threshold_get/set()` exposes scheduler-disable GuC-id threshold and clamps to `intel_guc_sched_disable_gucid_threshold_max()`.
- `intel_guc_debugfs_register()` registers the file table and delegates GuC log files to `intel_guc_log_debugfs_register()`.

Control flow:
- Registration is skipped if GuC is unsupported. Reads route through `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE` helpers. SLPC file visibility is guarded by an eval callback that checks `intel_guc_slpc_is_used()`.

State and persistence:
- Debugfs files mutate runtime `guc->submission_state.sched_disable_delay_ms` and `sched_disable_gucid_threshold`. Other files are read-only status projections.

Dependencies and integration points:
- Depends on GT debugfs helpers, GuC ADS, CT, SLPC, submission, log debugfs, and DRM printer/seq_file integration.

Risks:
- Debugfs setters can change scheduling behavior at runtime; clamping prevents extreme delay/threshold values but does not validate workload-specific impact.
- Status reads may return `-ENODEV` when GuC submission or SLPC is not used.

Test signals:
- Mount debugfs and verify file presence based on GuC/SLPC enablement.
- Read `guc_info`, `guc_registered_contexts`, and `guc_slpc_info` under supported/unsupported configurations.
- Write boundary values to scheduler tuning files and confirm clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.h

Purpose: declares the GuC debugfs registration entry point.

Important APIs, types, and functions:
- Forward declares `struct intel_guc` and `struct dentry`.
- Exposes `intel_guc_debugfs_register(struct intel_guc *guc, struct dentry *root)`.

Control flow:
- GT/debugfs setup calls this function with the GuC instance and root dentry. The implementation decides which files to register based on GuC support and feature use.

State and persistence:
- No owned state; debugfs dentries are created by the implementation and tied to the parent root.

Dependencies and integration points:
- Integrates the GuC-specific debugfs file table into the broader GT debugfs hierarchy.

Risks:
- Minimal header risk; the main risk is keeping declaration and implementation signatures synchronized.

Test signals:
- Build coverage and runtime verification that GuC debugfs files appear under the GT debugfs root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.c

Purpose: prepares hardware for GuC firmware transfer, supplies the RSA signature to hardware, uploads GuC ucode, polls load status, decodes boot/ukernel failures, and transitions firmware status to running or load-failed.

Important APIs, types, and functions:
- `guc_prepare_xfer()` programs GuC shim/cache/clock-gating/doorbell registers, Gen9 RC6 timing, and GuC debug register mirroring on newer IP.
- `guc_xfer_rsa_mmio()` copies RSA data into `UOS_RSA_SCRATCH()` registers for smaller keys.
- `guc_xfer_rsa_vma()` writes the GGTT offset of a GuC RSA VMA for larger keys.
- `guc_xfer_rsa()` selects the RSA transfer mode.
- `guc_load_done()` reads `GUC_STATUS`, decodes bootrom and ukernel fields, and tells the wait loop when success or a known terminal failure has occurred.
- `guc_wait_ucode()` polls load completion with retry limits, timing/frequency diagnostics, and detailed error mapping.
- `intel_guc_fw_upload()` is the public load entry point used by driver load, resume, and reset flows.

Control flow:
- Upload begins by programming shim/doorbell state.
- RSA signature is transferred either through MMIO scratch registers or a GGTT-pinned VMA offset.
- `intel_uc_fw_upload()` DMA-loads the CSS header plus uKernel code at offset `0x2000` using `UOS_MOVE`.
- `guc_wait_ucode()` polls `GUC_STATUS` in up to 1-second chunks. Debug GEM builds allow more retries. On success the firmware status becomes `INTEL_UC_FIRMWARE_RUNNING`; on failure it becomes `INTEL_UC_FIRMWARE_LOAD_FAIL`.

State and persistence:
- Hardware registers retain prepared GuC shim/doorbell/debug state.
- Firmware object status is updated through `intel_uc_fw_change_status()`.
- Diagnostics include load time, actual/requested GT frequencies, perf-limit reasons, bootrom status, ukernel status, and scratch EIP for exceptions.

Dependencies and integration points:
- Depends on GT uncore register access, RPS frequency helpers, GuC register definitions, Intel UC firmware upload helpers, and wait utilities.
- Called from higher-level `intel_uc_init_hw()`-style flows.

Risks:
- Load timing is sensitive to GT frequency and thermal/firmware conditions; excessive load time warnings distinguish slow success from failure.
- RSA transfer mode must match platform bootrom expectations.
- Status decoding must track firmware ABI values; unknown failures fall back to `-ENXIO`.
- Hardware register programming differs by graphics version and IP version.

Test signals:
- Firmware load success on cold boot, resume, and GT reset.
- Negative tests for RSA failure, key mismatch, invalid workaround KLV, HWConfig error, and firmware exception status.
- Confirm status transitions and diagnostic logs under timeout and slow-load scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.h

Purpose: declares the GuC firmware upload entry point.

Important APIs, types, and functions:
- Forward declares `struct intel_guc`.
- Exposes `int intel_guc_fw_upload(struct intel_guc *guc)`.

Control flow:
- Higher-level UC initialization, resume, or reset code calls `intel_guc_fw_upload()` after firmware fetch/preparation has succeeded.

State and persistence:
- No header-owned state. The implementation updates GuC firmware status and hardware registers.

Dependencies and integration points:
- Provides a narrow boundary between generic UC firmware orchestration and GuC-specific upload/status logic.

Risks:
- Minimal header risk; callers must interpret nonzero returns as firmware load failure and trigger the correct fallback/reset path.

Test signals:
- Build coverage and load-path tests that mock or exercise `intel_guc_fw_upload()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fwif.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fwif.h

Purpose: defines the driver-side GuC firmware interface constants, helper mappings, packed shared-memory structures, ADS layout, logging buffer state, engine class ids, work queue formats, policy formats, and capture-list enumerations that connect i915 to GuC firmware ABI headers.

Important APIs, types, and functions:
- Includes GuC ABI headers for actions, SLPC actions, errors, MMIO communication, CTB communication, KLVs, and messages.
- Defines GuC engine classes, maximum classes/instances, context ids, client priorities, doorbell constants, work queue item/status/type bitfields, and stage descriptor attributes.
- Defines GuC control dword indices and bitfields for log params, workarounds, feature enablement, debug verbosity, ADS address, and device id.
- Provides `MAKE_GUC_ID()`, `GUC_ID_TO_ENGINE_CLASS()`, `GUC_ID_TO_ENGINE_INSTANCE()`, `engine_class_to_guc_class()`, and `guc_class_to_engine_class()`.
- Defines packed structs: `guc_wq_item`, `guc_process_desc_v69`, `guc_sched_wq_desc`, `guc_ctxt_registration_info`, `guc_lrc_desc_v69`, `guc_klv_generic_dw_t`, context/scheduling policy update packets, `guc_policies`, `guc_mmio_reg`, `guc_mmio_reg_set`, `guc_gt_system_info`, `guc_ads`, `guc_engine_usage_record`, `guc_engine_usage`, and `guc_log_buffer_state`.
- Defines capture list owner/type/class enums and GuC log buffer type enum.
- Provides `SLPC_EVENT()` for composing SLPC event id/argument-count fields and policy timeout helpers returning max milliseconds.

Control flow:
- This header does not execute control flow, but its structures are used throughout GuC initialization: ADS construction, context registration, scheduling policy updates, submission work queues, CT send/receive, logging/capture buffer handling, and SLPC requests.

State and persistence:
- Packed structures describe persistent shared-memory contracts between host and GuC firmware. `guc_ads` points GuC at policy, system info, register state, capture lists, and workaround KLVs. `guc_log_buffer_state` is shared mutable state for log/capture producer-consumer coordination.

Dependencies and integration points:
- Used by GuC CT, ADS, submission, log, capture, SLPC, and register/save-restore code. It maps i915 engine classes from `intel_engine_types.h` to firmware class ids.

Risks:
- ABI drift is the largest risk. Packed layout, bitfields, enum values, and unit conversions must exactly match firmware expectations.
- The static engine-class maps assume array sizes matching driver and GuC class ranges; `BUILD_BUG_ON` and `GEM_BUG_ON` catch some misuse.
- Shared log buffer state is firmware-owned in places and host-owned in others; incorrect read/write ownership can lose logs or stall firmware.

Test signals:
- Compile-time layout and array-size checks.
- Firmware integration tests for context registration, scheduling policy updates, ADS parsing, work queue submission, logging, capture, and SLPC event requests.
- ABI review whenever GuC firmware ABI headers are updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fwif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_hwconfig.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_hwconfig.c

Purpose: retrieves the GuC-provided hardware configuration KLV table, stores it in `gt->info.hwconfig`, and frees it at teardown.

Important APIs, types, and functions:
- `__guc_action_get_hwconfig()` sends `INTEL_GUC_ACTION_GET_HWCONFIG` over MMIO with a GGTT address/size. `-ENXIO` is mapped to `-ENOENT`.
- `guc_hwconfig_discover_size()` queries with zero offset/size and stores the returned blob size.
- `guc_hwconfig_fill_buffer()` allocates a temporary GuC-mapped VMA, asks GuC to write the table into it, copies it into host memory, then releases the VMA.
- `has_table()` gates supported platforms: Alder Lake-P except ADL-P-N and graphics IP >= 12.55.
- `intel_gt_init_hwconfig()` initializes only when UC uses GuC; `intel_gt_fini_hwconfig()` frees `ptr` and clears size.

Control flow:
- Init skips unsupported platforms or non-GuC mode.
- Size discovery must return a positive size.
- Host memory is allocated with `kmalloc()`, a temporary GGTT buffer receives firmware data, and success persists the copied table in `gt->info.hwconfig`.
- On fill failure, fini is called to release partial state.

State and persistence:
- The retrieved KLV blob persists in `gt->info.hwconfig.ptr` with byte count `size` until `intel_gt_fini_hwconfig()`.

Dependencies and integration points:
- Uses GuC MMIO send path, GuC VMA allocation/mapping, GGTT offset helpers, i915 memcpy, and generic `intel_hwconfig` storage consumed by other GT discovery code.

Risks:
- Platform gating must match firmware availability. Querying unsupported firmware returns errors.
- The firmware-returned size is trusted for allocation and transfer; zero size is rejected.
- Data is copied from a temporary VMA without parsing here, so downstream users must validate KLV contents/lengths.

Test signals:
- Boot on supported and unsupported platforms and verify init returns expected values.
- Validate KLV table presence/size and downstream feature queries.
- Fault injection for VMA allocation, host allocation, zero-size discovery, and GuC action failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_hwconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.c

Purpose: manages the shared GuC log buffer, log-size programming values, log verbosity control, relayfs streaming to debugfs, flush handling, overflow accounting, and raw log dumping.

Important APIs, types, and functions:
- `_guc_log_init_sizes()` calculates crash/debug/capture section sizes, API unit flags/counts, field clipping, and crash/debug unit consistency based on build config defaults.
- `intel_guc_log_section_size_capture()`, `intel_guc_get_log_buffer_size()`, and `intel_guc_get_log_buffer_offset()` expose section sizing/offsets.
- `intel_guc_log_create()` allocates the combined log VMA, pins a WC map for critical reads, and initializes log level from `i915->params.guc_log_level`.
- `intel_guc_log_destroy()` releases the map/VMA.
- `intel_guc_log_set_level()` sends GuC log-control action under `guc_lock`.
- Relay support includes `guc_log_relay_create()`, `intel_guc_log_relay_open()`, `intel_guc_log_relay_start()`, `intel_guc_log_relay_flush()`, `intel_guc_log_relay_close()`, and `intel_guc_log_handle_flush_event()`.
- `_guc_log_copy_debuglogs_for_relay()` snapshots debug/crash log state, handles overflows and wraparound, copies data from WC log memory into relay subbuffers, advances read pointers, and acknowledges flush completion.
- `intel_guc_log_info()` reports relay/log stats. `intel_guc_log_dump()` prints raw log object or saved load-error log.

Control flow:
- Create computes the layout: one page of `guc_log_buffer_state` headers followed by debug, crash, and capture sections. It allocates a GuC VMA and pins WC mapping for direct reads during error paths.
- Log level changes use runtime PM, send `INTEL_GUC_ACTION_UK_LOG_ENABLE_LOGGING`, and update cached level only on success.
- Relay open creates a single global relay file under GuC debugfs, maps the log object for relay bookkeeping, and requires fast WC memcpy support.
- Firmware flush notifications queue high-priority work. The worker copies debug/crash sections, not capture, then sends `INTEL_GUC_ACTION_LOG_BUFFER_FILE_FLUSH_COMPLETE`.
- Forced relay flush waits for pending work, sends force-flush action, and copies the updated data.
- Raw dumping pins the selected log object WC, copies page by page, and emits four dwords per line.

State and persistence:
- `intel_guc_log` stores configured level, size units/counts, log VMA, WC map, relay channel/open/started flags, work item, relay full count, and per-buffer overflow/flush stats.
- Shared `guc_log_buffer_state` fields coordinate producer/consumer state with firmware; host updates read pointers and clears flush flags.

Dependencies and integration points:
- Uses debugfs/relayfs, runtime PM, GuC CT/MMIO action wrappers, i915 GEM VMA mapping, WC memcpy, capture sizing, and GuC print helpers.
- Integrated with CT event handling for `INTEL_GUC_ACTION_NOTIFY_FLUSH_LOG_BUFFER_TO_FILE` and with capture parsing via the capture log section.

Risks:
- Relay no-overwrite mode can drop copying when user space is too slow; `full_count` tracks this.
- Incorrect size/unit programming can misconfigure firmware log buffers; code logs alignment, zero, clipping, and unit mismatch errors.
- Log buffer state can be invalid or overflowed; code falls back to whole-buffer copy but may include stale/garbled data.
- WC mapping and relay lifecycle require careful locking and object refs.

Test signals:
- Verify log allocation sizes under normal, DEBUG_GEM, and DEBUG_GUC builds.
- Exercise debugfs log level changes, relay open/start/flush/close, slow consumer behavior, and firmware flush events.
- Validate raw log dump and saved load-error dump.
- Inject overflow and invalid read/write offsets to observe recovery/warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.h

Purpose: defines the GuC log state structure, log-level conversion macros, section identifiers, and public log/relay/dump APIs.

Important APIs, types, and functions:
- Log level macros map i915 levels to GuC enable/default/verbosity semantics: disabled, non-verbose, verbose, `GUC_LOG_LEVEL_TO_VERBOSITY()`, and `GUC_LOG_LEVEL_MAX`.
- Section enum indexes crash, debug, and capture sections.
- `struct intel_guc_log` stores level, `guc_lock`, per-section size/unit/count/flag data, VMA/map, relay state, and stats.
- Public APIs cover early init, overflow detection, buffer size/offset queries, create/destroy, set/get level, relay create/open/start/flush/close state, flush event handling, info printing, raw dump, and capture section size.

Control flow:
- GuC setup initializes the struct early, creates the backing buffer before firmware configuration, handles firmware flush notifications during runtime, and destroys the VMA during teardown.
- Debugfs routes user operations through set-level, relay, info, and dump APIs.

State and persistence:
- The header documents persistent host-side log state. Shared firmware log state is represented by `guc_log_buffer_state` from `intel_guc_fwif.h`.

Dependencies and integration points:
- Includes Linux mutex/relay/workqueue APIs, `intel_guc_fwif.h` for log buffer types, and GEM declarations.
- Used by GuC logging implementation, capture code, debugfs, and CT event handling.

Risks:
- Exposed state must remain consistent with locking rules: `guc_lock` for `level`, `relay.lock` for relay channel/object ref state.
- Log-level macros must align with GuC firmware control semantics where default logging is separate from enable.

Test signals:
- Build coverage for callers.
- Runtime debugfs tests for log level, relay, dump, and flush notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.c

Purpose: exposes GuC logging controls and dumps through debugfs.

Important APIs, types, and functions:
- `obj_to_guc_log_dump_size()` estimates seq_file buffer size for a raw dword log dump.
- `guc_log_dump_size()` and `guc_load_err_dump_size()` size normal and load-error dumps.
- `guc_log_dump_show()` and `guc_load_err_log_dump_show()` call `intel_guc_log_dump()` with the appropriate source.
- `guc_log_level_get/set()` expose `intel_guc_log_get_level()` and `intel_guc_log_set_level()`.
- `guc_log_relay_open()`, `guc_log_relay_write()`, and `guc_log_relay_release()` implement a debugfs relay control file: open creates relay state, writing `1` starts relay, other writes force flush, release closes relay.
- `intel_guc_log_debugfs_register()` registers `guc_log_dump`, `guc_load_err_log_dump`, `guc_log_level`, and `guc_log_relay`.

Control flow:
- Registration is skipped when GuC is unsupported.
- Dump reads preallocate based on backing object size. DEBUG_GEM builds warn once if the seq_file overflows the estimate.
- Relay open requires `intel_guc_is_ready()`, stores the log pointer in `file->private_data`, then delegates lifecycle to `intel_guc_log.c`.

State and persistence:
- Debugfs writes mutate log verbosity and relay state. The relay file is session-scoped: open creates, writes start/flush, release closes.

Dependencies and integration points:
- Depends on GT debugfs helpers, GuC support/ready checks, log implementation, and UC load-error log storage.

Risks:
- Large log objects can produce large textual dumps; size estimation must keep seq_file usable.
- Relay open/close must be balanced; release always calls close.
- Userspace can force flushes while firmware/runtime PM state changes, so lower-level log code must handle readiness.

Test signals:
- Read both dump files with/without log objects and saved load-error logs.
- Set legal/illegal log levels through debugfs.
- Open relay, write `1`, write other values to flush, then close; verify no leaked relay channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.h

Purpose: declares the GuC log debugfs registration function.

Important APIs, types, and functions:
- Forward declares `struct intel_guc_log` and `struct dentry`.
- Exposes `intel_guc_log_debugfs_register(struct intel_guc_log *log, struct dentry *root)`.

Control flow:
- GuC debugfs setup calls this helper after registering general GuC files.

State and persistence:
- No owned state; implementation creates debugfs entries tied to the provided root and log object.

Dependencies and integration points:
- Connects `intel_guc_debugfs.c` to log-specific dump, level, and relay controls.

Risks:
- Minimal header risk; runtime availability is enforced in the implementation.

Test signals:
- Build coverage and debugfs registration checks for GuC log files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_log_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_print.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_print.h

Purpose: provides GuC-prefixed logging and warning macros layered on GT print helpers.

Important APIs, types, and functions:
- `guc_printk()` maps a GuC pointer to GT print functions with `"GUC: "` prefix.
- Convenience macros include `guc_err`, `guc_warn`, `guc_notice`, `guc_info`, `guc_dbg`, rate-limited variants, and `guc_probe_error`.
- Warning helpers include `guc_WARN`, `guc_WARN_ONCE`, `guc_WARN_ON`, and `guc_WARN_ON_ONCE`.

Control flow:
- No runtime logic beyond macro expansion. Callers use these macros for consistent GuC diagnostics.

State and persistence:
- No state. Messages flow through GT/i915 logging infrastructure.

Dependencies and integration points:
- Includes `gt/intel_gt.h` and `gt/intel_gt_print.h`, and requires `guc_to_gt()` to be valid for the provided GuC pointer.

Risks:
- Macros evaluate the GuC expression in logging context; callers should avoid side-effect expressions.
- Wrong GuC pointer leads to wrong GT association or crash in diagnostics.

Test signals:
- Compile coverage and log output inspection in GuC init/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_print.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.c

Purpose: manages GuC RC (render/GT power state control) support selection and toggling between firmware-controlled and host-controlled RC modes.

Important APIs, types, and functions:
- `__guc_rc_supported()` allows GuC RC only when GuC submission is supported and graphics version is Gen12+.
- `__guc_rc_selected()` requires support and GuC submission selection.
- `intel_guc_rc_init_early()` stores support/selection booleans on `struct intel_guc`.
- `guc_action_control_gucrc()` sends `INTEL_GUC_ACTION_SETUP_PC_GUCRC` with `INTEL_GUCRC_FIRMWARE_CONTROL` or `INTEL_GUCRC_HOST_CONTROL`.
- `__guc_rc_control()` checks `intel_uc_uses_guc_rc()`, GuC readiness, sends control action, logs failures/success.
- `intel_guc_rc_enable()` and `intel_guc_rc_disable()` are public wrappers.

Control flow:
- Early init derives capability. Enable/disable are called once GuC is ready and UC policy says GuC RC is used.
- Control action is synchronous over the GuC send path and positive firmware return is normalized to `-EPROTO`.

State and persistence:
- Persistent selection state is `guc->rc_supported` and `guc->rc_selected`. Runtime hardware/firmware RC mode changes after successful control action.

Dependencies and integration points:
- Depends on GuC submission selection, UC policy checks, GuC readiness, GuC send path, and GuC print helpers.

Risks:
- Calling enable/disable before GuC readiness returns `-EINVAL`.
- Platform/support gating must remain aligned with firmware capabilities.
- RC mode changes affect power management behavior and can interact with reset/suspend flows.

Test signals:
- Gen12+ GuC submission boot should enable RC successfully when policy selects it.
- Unsupported/pre-Gen12 and GuC-submission-disabled paths should return/use false selectors.
- Fault GuC action failures and verify probe-error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.h

Purpose: declares GuC RC support/selection helpers and enable/disable entry points.

Important APIs, types, and functions:
- `intel_guc_rc_init_early()` initializes support and selection booleans.
- Inline helpers `intel_guc_rc_is_supported()`, `intel_guc_rc_is_wanted()`, and `intel_guc_rc_is_used()` compose support, GuC submission selection, and actual GuC submission use.
- `intel_guc_rc_enable()` and `intel_guc_rc_disable()` control firmware/host RC mode.

Control flow:
- Higher-level UC init code checks these helpers to decide whether to invoke GuC RC enable/disable.

State and persistence:
- Reads `guc->rc_supported`, `guc->rc_selected`, and submission state; no header-owned state.

Dependencies and integration points:
- Includes `intel_guc_submission.h` to access `struct intel_guc` and submission predicates.

Risks:
- `intel_guc_rc_is_wanted()` depends on `submission_selected`; if selection changes after early init, callers need current state consistency.

Test signals:
- Compile coverage and policy matrix tests for supported/wanted/used combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_reg.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_reg.h

Purpose: centralizes GuC and HuC MMIO register offsets, status bitfields, DMA controls, scratch registers, shim controls, interrupts, TLB invalidation controls, doorbells, and a packed doorbell cacheline format.

Important APIs, types, and functions:
- Status and scratch definitions: `GUC_STATUS`, `GS_*` masks/shifts, `GUC_HEADER_INFO`, `SOFT_SCRATCH()`, `GEN11_SOFT_SCRATCH()`, `MEDIA_SOFT_SCRATCH()`, and scratch counts.
- RSA/DMA/load definitions: `UOS_RSA_SCRATCH()`, DMA address/copy/control registers, `UOS_MOVE`, `START_DMA`, `DMA_GUC_WOPCM_OFFSET`, WOPCM size/lock fields, HuC status/load info.
- PM/shim/interrupt definitions: GT PM config doorbell enable bits, `GUC_ARAT_C6DIS`, `GUC_SHIM_CONTROL`, `GUC_SHIM_CONTROL2`, `GUC_SEND_INTERRUPT`, host interrupt registers, semaphore interrupt enables, and TLB invalidation controls.
- Doorbell and interrupt definitions include `struct guc_doorbell_info`, Gen8 doorbell registers, Gen12 distributed doorbell population fields, GuC interrupt enable registers, and GuC interrupt vector bits such as `GUC_INTR_GUC2HOST`, DMA done, fatal error, notification error, and software interrupts.

Control flow:
- Register constants are consumed by firmware upload, notification, interrupt, TLB invalidation, HuC load, and GuC runtime setup code.

State and persistence:
- This header defines hardware state addresses and bit meanings, not driver-owned state.

Dependencies and integration points:
- Includes `i915_reg_defs.h` for `_MMIO()` and kernel integer/compiler headers.
- Shared by GuC firmware loading, CT notification, power-management setup, and GuC/HuC authentication flows.

Risks:
- Incorrect offsets or masks can break firmware loading, status decoding, interrupts, or power management.
- Some registers vary by generation/media tile; users must select the correct macro for platform context.

Test signals:
- Firmware load/status tests validate `GUC_STATUS` and scratch usage.
- Interrupt/doorbell tests validate `GUC_SEND_INTERRUPT`, doorbell register programming, and `GUC_INTR_*` handling paths.
- Platform bring-up should review any new GuC IP register changes against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.c

Purpose: implements GuC Single Loop Power Control (SLPC) support for dynamic GT frequency management, including initialization, reset/start, min/max/boost frequency controls, efficient-frequency policy, media ratio mode, power profiles, task-state queries, PM interrupt setup, and debug printing.

Important APIs, types, and functions:
- Support/selection: `__detect_slpc_supported()`, `__guc_slpc_selected()`, and `intel_guc_slpc_init_early()`.
- Shared memory helpers: `slpc_mem_set_param()`, enable/disable helpers, `slpc_shared_data_reset()`, and `slpc_get_state()`.
- GuC action wrappers: `guc_action_slpc_set_param[_nb]()`, `guc_action_slpc_query()`, and `guc_action_slpc_reset()`.
- Lifecycle: `intel_guc_slpc_init()`, `intel_guc_slpc_enable()`, and `intel_guc_slpc_fini()`.
- Frequency APIs: `intel_guc_slpc_set_max_freq()`, `intel_guc_slpc_get_max_freq()`, `intel_guc_slpc_set_min_freq()`, `intel_guc_slpc_get_min_freq()`, `intel_guc_slpc_set_boost_freq()`, `intel_guc_slpc_boost()`, and `intel_guc_slpc_dec_waiters()`.
- Policy APIs: `intel_guc_slpc_set_ignore_eff_freq()`, `intel_guc_slpc_set_strategy()`, `intel_guc_slpc_set_media_ratio_mode()`, and `intel_guc_slpc_set_power_profile()`.
- Diagnostics: `intel_guc_slpc_print_info()` prints SLPC task status, decoded min/max frequencies, and waitboost counters.

Control flow:
- Early init marks SLPC supported only for Gen12+ GuC submission and selected when GuC submission is selected.
- Full init allocates a GuC-mapped shared data page, initializes softlimit/cache fields, mutex, boost work, waiter count, media ratio mode, and base power profile.
- Enable zeros and seeds shared data overrides, sends a reset event, waits for running state, queries task state, enables PM interrupt delivery to GuC, reads RP values from RPS caps, handles server RPMax-min case, sets max to fused RP0, restores cached efficient-frequency/media/strategy/power-profile/softlimit state, and returns errors on failed critical steps.
- Frequency setters validate against platform limits and current softlimits, use runtime PM, send SLPC parameter actions, and update cached softlimits on success. Min updates are locked because waitboost can temporarily force min frequency.
- Waitboost increments waiters, schedules boost work, raises min to boost/RP0 while waiters exist, and restores min softlimit when the last waiter retires.

State and persistence:
- `intel_guc_slpc` persists the shared VMA pointer/address, support/selection flags, platform RP/min frequencies, softlimits, efficient-frequency ignore flag, boost frequency, media ratio mode, power profile, lock, work item, waiter count, and boost count.
- GuC shared memory stores SLPC global/task state and override parameters; host flushes/queries it around firmware actions.

Dependencies and integration points:
- Depends on GuC CT send helpers, runtime PM, RPS frequency capability conversion, GT PM interrupt mask register, SLPC firmware ABI constants, media ratio support predicate, and DRM printer.
- Integrates with sysfs/debugfs frequency controls and request waitboost paths.

Risks:
- Frequency validation must keep min/max/boost within platform limits and softlimits; wrong ordering can reject valid sysfs requests or send invalid firmware parameters.
- Nonblocking boost actions can fail without making request retirement fail; diagnostics are notices.
- Shared data is read after cache flushes; missing cache maintenance can report stale state.
- Enable sequence has several best-effort cached parameter restores whose failures may be ignored or only logged in some calls.

Test signals:
- Boot with GuC submission on Gen12+ and confirm SLPC reaches running state.
- Sysfs min/max/boost tests for boundary values, invalid values, and persistence across reset/re-enable.
- Waitboost tests for waiter increment/decrement and min-frequency restore.
- Debugfs `guc_slpc_info` should reflect task state and decoded frequencies.
- Platform tests for media ratio support, server RPMax-min handling, and power saving/base profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.h

Purpose: declares SLPC feature predicates and public lifecycle, frequency, policy, PM interrupt, waitboost, and diagnostic APIs.

Important APIs, types, and functions:
- `SLPC_MAX_FREQ_MHZ` defines the special/upper frequency constant used by SLPC code.
- Inline predicates `intel_guc_slpc_is_supported()`, `intel_guc_slpc_is_wanted()`, and `intel_guc_slpc_is_used()` combine `guc->slpc` support/selection with GuC submission use.
- Public APIs include early/full init, enable, fini, max/min/boost set/get, info print, media ratio mode, PM interrupt mask enable, boost/decrement waiters, efficient-frequency ignore, strategy, and power profile setters.

Control flow:
- Higher-level UC and GT PM code use predicates to decide whether to allocate, enable, expose sysfs/debugfs controls, and route waitboost/policy requests through SLPC.

State and persistence:
- No header-owned state; it exposes operations on `struct intel_guc_slpc` defined in `intel_guc_slpc_types.h`.

Dependencies and integration points:
- Includes GuC submission predicates and SLPC type definition. Used by GuC debugfs, PM/sysfs, request wait paths, and UC init.

Risks:
- `intel_guc_slpc_is_used()` must only be true when GuC submission is actually active; exposing controls too early can lead to `-ENODEV`.
- API users must understand which setters are cached/persistent across reset and which are immediate firmware commands.

Test signals:
- Compile and policy matrix tests for support/wanted/used.
- Runtime tests for each public setter/getter through sysfs/debugfs and reset/re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc_types.h

Purpose: defines `struct intel_guc_slpc`, the persistent host-side state for GuC SLPC.

Important APIs, types, and functions:
- `SLPC_RESET_TIMEOUT_MS` sets the wait timeout for SLPC reset/start.
- `struct intel_guc_slpc` fields include shared-data VMA/address, support and selection booleans, server-min marker, platform frequencies, boost frequency, min/max softlimits, efficient-frequency ignore flag, power profile, media ratio mode, mutex, boost work, waiter count, and boost count.

Control flow:
- The struct is initialized early for support/selection, allocated/configured in full init, used by enable and runtime setters, and released in fini.

State and persistence:
- Softlimits, boost frequency, efficient-frequency flag, media ratio mode, and power profile are cached across SLPC re-enable/reset so enable can reapply policy to firmware.
- `num_waiters` and `boost_work` coordinate transient waitboost state.

Dependencies and integration points:
- Includes atomic, workqueue, mutex, and type headers. Uses forward-declared kernel/i915 types through pointers from users.

Risks:
- Locking around `boost_freq` and `num_waiters` is documented in the struct; callers that bypass SLPC APIs could race waitboost min-frequency changes.
- Cached policy fields must be kept in sync with successful firmware updates.

Test signals:
- Reset/re-enable tests should verify cached policy replay.
- Concurrency tests around waitboost and sysfs boost/min changes should verify locking and correct `num_waiters` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc_types.h -->
