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
