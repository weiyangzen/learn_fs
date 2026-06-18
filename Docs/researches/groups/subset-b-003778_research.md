# subset-b-003778 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.c

## Purpose
Implements the GuC doorbell ID manager used by Xe GuC submission and SR-IOV provisioning. It tracks a finite set of hardware doorbell IDs with a bitmap, supports single-ID allocations for normal submission, and supports contiguous range reservations for PF-to-VF resource assignment.

## Important APIs, Types, And Functions
The exported API is `xe_guc_db_mgr_init`, `xe_guc_db_mgr_reserve_id_locked`, `xe_guc_db_mgr_release_id_locked`, `xe_guc_db_mgr_reserve_range`, `xe_guc_db_mgr_release_range`, and `xe_guc_db_mgr_print`. Internal helpers convert the embedded `xe_guc_db_mgr` back to `xe_guc`, `xe_gt`, and `xe_device`, and the common allocation path is `dbm_reserve_chunk_locked`.

## Control Flow
Initialization converts `~0` to `GUC_NUM_DOORBELLS`, allocates a zeroed bitmap when count is non-zero, stores the count, and registers `__fini_dbm` with DRM managed cleanup. Reservation validates count and manager capacity, optionally checks that `spare` IDs remain, finds a contiguous zero area, and sets bits. Release asserts that the relevant bits are set in debug builds, then clears them. Printing walks clear and set bit ranges under the submission mutex.

## State And Persistence
The persistent state is `dbm->bitmap` plus `dbm->count`; both live for the DRM-managed device lifetime. All access is serialized with `guc->submission_state.lock`, including teardown, allocation, release, and printing.

## Dependencies And Integration Points
The file depends on Linux bitmap helpers, `drmm_add_action_or_reset`, `GUC_NUM_DOORBELLS`, `xe_gt` assertions/printing, and the GuC submission lock. SR-IOV PF code can reserve contiguous doorbell ranges with spare capacity guarantees; normal submission code uses the locked single-ID API.

## Risks And Test Signals
Correctness depends on callers using the locked single-ID APIs only while holding the submission lock. Fragmentation can cause `-ENOSPC` even when enough IDs are free non-contiguously, which is intentional for range provisioning. `CONFIG_DRM_XE_DEBUG` adds release-time bit assertions, and built-in KUnit coverage is included through `tests/xe_guc_db_mgr_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.h

## Purpose
Declares the public interface for the GuC doorbell manager implemented in `xe_guc_db_mgr.c`.

## Important APIs, Types, And Functions
It forward-declares `struct drm_printer` and `struct xe_guc_db_mgr`, then exposes initialization, locked single-ID reserve/release, unlocked range reserve/release, and printer functions.

## Control Flow
The header itself has no runtime flow, but its API split documents locking expectations: `_locked` calls are for submission code already holding the GuC submission lock, while range operations take the manager lock internally.

## State And Persistence
State is opaque to users of this header and owned by `struct xe_guc_db_mgr`. The caller receives only integer IDs/ranges and must later release them through the paired API.

## Dependencies And Integration Points
Included by GuC submission, SR-IOV provisioning, debug printing, and tests that need doorbell allocation services.

## Risks And Test Signals
The main API risk is mixing the locked and unlocked forms incorrectly. Header contract tests are indirect through compile coverage and the KUnit test included by the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_db_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.c

## Purpose
Registers GuC-specific debugfs files under a GT `uc` directory and adapts DRM debugfs callbacks to `struct xe_guc` printers.

## Important APIs, Types, And Functions
The exported entry point is `xe_guc_debugfs_register`. `guc_debugfs_show` resolves the `xe_gt` from the debugfs dentry hierarchy, takes a runtime PM guard, and calls the function stored in `drm_info_list.data`. Thin wrappers expose GuC log, LFD log, dmesg log dump, CTB, and PC printers.

## Control Flow
Registration always creates VF-safe files `guc_info` and `guc_ctb`. On non-VF devices it also creates PF-only log files. If GuC PC is not skipped, it adds `guc_pc`. File reads enter `guc_debugfs_show`, construct a `drm_printer`, resolve GT and GuC context, hold runtime PM, then invoke the selected print callback.

## State And Persistence
The file does not own persistent device state. It creates debugfs entries whose callbacks observe live GuC, CTB, log, and PC state. Runtime PM guarding is used so reads see accessible hardware-backed data.

## Dependencies And Integration Points
Depends on DRM debugfs helpers, `xe_pm`, `xe_guc_ct`, `xe_guc_log`, `xe_guc_pc`, and GuC info printing. It integrates with the GT debugfs tree layout by assuming `dent->d_parent->d_parent->d_inode->i_private` is the `xe_gt`.

## Risks And Test Signals
The dentry-parent assumption is fragile if debugfs layout changes. The PF/VF split avoids exposing PF-only or privileged paths on VFs. Tests are mainly debugfs smoke/runtime tests and manual reads of `guc_info`, `guc_ctb`, `guc_log*`, and `guc_pc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.h

## Purpose
Provides the public declaration for GuC debugfs registration.

## Important APIs, Types, And Functions
It forward-declares `struct dentry` and `struct xe_guc`, then declares `xe_guc_debugfs_register`.

## Control Flow
No runtime control flow lives in the header; callers pass the GuC object and parent debugfs directory to the implementation.

## State And Persistence
The header owns no state. Debugfs entry lifetime is managed by DRM/debugfs infrastructure in the implementation.

## Dependencies And Integration Points
Included by GuC or GT debugfs setup code when the `uc` debugfs subtree is populated.

## Risks And Test Signals
The interface is narrow. Compile-time include coverage and debugfs registration/read smoke tests are the practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.c

## Purpose
Implements GuC engine activity accounting. It allocates GGTT-visible buffers for GuC-written activity metadata and per-engine counters, enables GuC reporting, and exposes active and total tick queries for native and SR-IOV PF per-function views.

## Important APIs, Types, And Functions
Exports `xe_guc_engine_activity_init`, `xe_guc_engine_activity_supported`, `xe_guc_engine_activity_enable_stats`, `xe_guc_engine_activity_function_stats`, `xe_guc_engine_activity_active_ticks`, and `xe_guc_engine_activity_total_ticks`. Core helpers include `allocate_engine_activity_group`, `allocate_engine_activity_buffers`, `enable_engine_activity_stats`, `enable_function_engine_activity_stats`, `get_engine_active_ticks`, and `get_engine_total_ticks`.

## Control Flow
Initialization checks that the driver is not a VF and that the GuC submission interface is at least 1.14.1. It allocates software activity groups, allocates one device-level metadata buffer and one activity buffer, computes the GPM timestamp shift from `RPM_CONFIG0`, and registers teardown. Enabling sends a blocking GuC CT action with buffer GGTT addresses. Per-function stats allocate buffers for PF plus VFs, send the function-buffer action, and seed CPU timestamps for non-PF functions. Queries map the appropriate buffer slice, read metadata and activity fields, cache change counters, accumulate deltas, and derive running active ticks from `MISC_STATUS_0` when GuC says an engine is currently running.

## State And Persistence
Persistent state lives in `guc->engine_activity`: support flag, timestamp shift, allocated groups, BO pointers, function count, cached metadata/activity snapshots, CPU timestamps, accumulated active totals, and quanta totals. BOs are pinned/mapped until explicit disable for function stats or device-managed teardown for the global buffers.

## Dependencies And Integration Points
Depends on GuC CT actions `XE_GUC_ACTION_SET_DEVICE_ENGINE_ACTIVITY_BUFFER` and `XE_GUC_ACTION_SET_FUNCTION_ENGINE_ACTIVITY_BUFFER`, firmware ABI structs from `xe_guc_fwif.h`, engine class mapping, MMIO timestamp registers, Xe BO helpers, SR-IOV PF helpers, and tracepoints.

## Risks And Test Signals
Counter logic relies on GuC change numbers to avoid double counting. Function queries must be rejected for non-PF or out-of-range IDs. The active calculation uses lower 32 bits of the shifted GPM timestamp, so wrap behavior is implicit in unsigned arithmetic. Test signals include GuC interface version gating, trace output from `trace_xe_guc_engine_activity`, PF/VF enable-disable paths, and runtime validation that active ticks never regress across samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.h

## Purpose
Declares the public GuC engine activity statistics interface.

## Important APIs, Types, And Functions
The header declares initialization, support query, device-level enable, per-function enable/disable, and active/total tick query APIs. It forward-declares `struct xe_hw_engine` and `struct xe_guc`.

## Control Flow
Callers initialize first, enable stats after GuC is ready, optionally enable per-function buffers on PFs, then query active or total ticks for a hardware engine and function ID.

## State And Persistence
The header exposes no data layout; state is owned by `struct xe_guc_engine_activity` in the types header and embedded in `struct xe_guc`.

## Dependencies And Integration Points
Used by GT accounting, SR-IOV PF telemetry, and any code that reports engine active/quanta data from GuC.

## Risks And Test Signals
The API silently returns zero for unsupported or invalid function cases through the implementation. Compile coverage plus runtime telemetry sanity checks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity_types.h

## Purpose
Defines the software state containers used by GuC engine activity accounting.

## Important APIs, Types, And Functions
Key types are `struct engine_activity`, `struct engine_activity_group`, `struct engine_activity_buffer`, and `struct xe_guc_engine_activity`. `engine_activity` combines accumulated driver counters with snapshots of GuC metadata and activity records. `xe_guc_engine_activity` tracks support, buffer ownership, number of functions, number of activity groups, and the GPM timestamp shift.

## Control Flow
The structures are populated by `xe_guc_engine_activity.c`: allocation creates groups and buffers, enable registers GGTT addresses with GuC, and query paths update cached fields and accumulated counters.

## State And Persistence
State persists in the embedded GuC object across stats queries. Device buffers live until managed teardown; function buffers live while per-function stats are enabled. `quanta_remainder_ns` persists to keep CPU-time scaling precise across samples.

## Dependencies And Integration Points
Includes `xe_guc_fwif.h` for firmware metadata and activity record layouts. References `struct xe_bo` without including its full definition through pointer members.

## Risks And Test Signals
The two-dimensional engine arrays must be indexed with GuC engine class and logical instance, matching the firmware layout. Tests should validate PF plus VF group sizing and that cached snapshots correctly handle unchanged GuC change numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_exec_queue_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_exec_queue_types.h

## Purpose
Defines GuC-specific state attached to each `xe_exec_queue`.

## Important APIs, Types, And Functions
The main type is `struct xe_guc_exec_queue`, containing a parent queue pointer, RCU head, GPU scheduler, scheduler entity, static scheduler messages, async destroy work, resume timestamp, atomic state, work queue item head/tail, GuC ID, suspend wait queue and flags, and VF migration recovery flags.

## Control Flow
This header has no functions, but the fields indicate control-flow roles: scheduler messages travel through the GPU scheduler when allocations are disallowed, `destroy_async` defers final cleanup, wait queues coordinate suspends, and recovery flags drive cleanup/suspend/resume after VF migration.

## State And Persistence
The struct persists for the lifetime of the parent execution queue. `id` is allocated from the GuC ID manager, `state` is atomic for concurrent submission state transitions, and `needs_*` flags preserve recovery work across migration handling.

## Dependencies And Integration Points
Depends on scheduler types, Linux RCU, spinlock/workqueue/waitqueue infrastructure, and `struct xe_exec_queue`. Used by GuC submission, scheduling, suspend/resume, and SR-IOV migration recovery code.

## Risks And Test Signals
Risks center on lifetime and concurrency: exported fences require RCU-safe freeing, static messages must not exceed `MAX_STATIC_MSG_TYPE`, and suspend/resume flags must be cleared exactly once. Tests should exercise queue destruction, migration recovery, and suspend wait wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_exec_queue_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_fwif.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_fwif.h

## Purpose
Collects host-side GuC firmware interface definitions used by Xe GuC submission, logging, policy, hardware config, engine activity, and page-fault handling.

## Important APIs, Types, And Functions
The header defines G2H message lengths, generic KLV structs, execution-queue policy update packets, GuC control dword fields, global scheduler policy structures, GT system-info and ADS layouts, engine usage/activity records, GuC receive-message bits, UM queue parameters, page-fault descriptors/replies, and access-counter descriptors.

## Control Flow
No executable flow is present. The layouts drive CT/MMIO command construction and parsing elsewhere. For example, `xe_guc_pagefault.c` parses `xe_guc_pagefault_desc` fields and builds `xe_guc_pagefault_reply`; `xe_guc_engine_activity.c` maps GuC activity metadata and records; GuC load code fills control/ADS fields.

## State And Persistence
All structs describe persistent shared memory or wire-format state owned by GuC and the host. Most are `__packed`, making ABI layout stability the central requirement.

## Dependencies And Integration Points
Includes GuC capture, KLV, scheduler ABI headers and engine class types. It is a core integration point between Xe driver code and GuC firmware protocol, including SR-IOV and page-fault UM queue setup.

## Risks And Test Signals
Any field-width, mask, packing, or length mismatch can break firmware communication. Page-fault comments note that some values currently match Xe pagefault enums by coincidence and would need remapping if enums diverge. Test signals are firmware boot success, CT action success, page-fault response handling, engine activity reads, and ABI compile assertions in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_fwif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.c

## Purpose
Obtains, stores, copies, dumps, and searches the GuC hardware configuration table.

## Important APIs, Types, And Functions
Exports `xe_guc_hwconfig_init`, `xe_guc_hwconfig_size`, `xe_guc_hwconfig_copy`, `xe_guc_hwconfig_dump`, and `xe_guc_hwconfig_lookup_u32`. Internal helpers send `XE_GUC_ACTION_GET_HWCONFIG` first to query size and then to copy the table into a GGTT BO.

## Control Flow
Initialization is idempotent, runs only on GT0, and only on ADL-P or graphics version 12.55 and newer. It queries size, rejects zero size, allocates a managed pinned/mapped system GGTT BO, stores it in `guc->hwconfig`, and asks GuC to copy the table into it. Dump and lookup allocate temporary host memory, copy from the BO mapping, then iterate key-length-value entries.

## State And Persistence
Persistent state is `guc->hwconfig.bo` and `guc->hwconfig.size`, managed for the device lifetime. The table is copied once and then read through mapped BO memory.

## Dependencies And Integration Points
Depends on GuC MMIO send, GuC action ABI, Xe BO/pin/map helpers, GT/tile/device metadata, and DRM printer APIs. Consumers use the size/copy/lookup APIs for platform feature data.

## Risks And Test Signals
The KLV-style parser checks for truncated entries during dumps but `lookup_u32` assumes the matched key has at least one value dword. Initialization is platform-gated; test signals include successful table size query, nonzero size, dump output without truncation errors, and expected attribute lookup results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.h

## Purpose
Declares the GuC hardware configuration table API.

## Important APIs, Types, And Functions
The header exposes initialization, table size, table copy, debug dump, and 32-bit attribute lookup functions. It forward-declares `struct drm_printer` and `struct xe_guc`.

## Control Flow
The intended flow is initialize once, check size, optionally copy or dump the full table, and use lookup for individual attributes.

## State And Persistence
State is hidden in `guc->hwconfig` and owned by the implementation.

## Dependencies And Integration Points
Included by GuC init and feature-detection code that needs firmware-provided hardware attributes.

## Risks And Test Signals
The lookup API reports `-EINVAL`, `-ENOMEM`, or `-ENOENT`; callers must distinguish missing table from missing attribute. Compile coverage and platform boot with hwconfig-enabled firmware validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hxg_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hxg_helpers.h

## Purpose
Provides small helpers for GuC HXG message sizing, type classification, stringification, and host-side response encoding.

## Important APIs, Types, And Functions
Defines `hxg_sizeof`, `guc_hxg_type_to_string`, `guc_hxg_type_is_action`, `guc_hxg_type_is_reply`, and encoders for success, failure, busy, and retry messages. The encoders fill message dword 0 with host origin, HXG type, and type-specific data fields, returning the encoded message length.

## Control Flow
Callers inspect the type field with the classifier helpers or build a response with one of the inline encoders. `hxg_sizeof` forces compile-time failure if a type is not u32-aligned.

## State And Persistence
No persistent state is owned by this header; it operates on caller-provided message buffers.

## Dependencies And Integration Points
Depends on GuC messages ABI masks and Linux bitfield helpers. Used by relay and other GuC communication paths that exchange HXG messages.

## Risks And Test Signals
The helpers assume the ABI masks match firmware. Message-buffer callers must provide enough space for the returned length. Relay KUnit paths and CT message protocol tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hxg_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.c

## Purpose
Implements a GuC context ID manager for normal submission allocation and SR-IOV PF range provisioning.

## Important APIs, Types, And Functions
Exports `xe_guc_id_mgr_init`, locked reserve/release APIs, unlocked PF reserve/release APIs, and `xe_guc_id_mgr_print`. Internal helpers include `find_last_zero_area`, `idm_reserve_chunk_locked`, `idm_release_chunk_locked`, and `__fini_idm`.

## Control Flow
Initialization validates the requested limit, converts `~0` to `GUC_ID_MAX`, allocates a bitmap, records total count, and registers DRM-managed cleanup. Normal submission reservations search from low IDs. PF reservations with a nonzero retain requirement first ensure `used + count + retain <= total`, then reserve the highest suitable free range to leave low IDs available. Release checks bounds and bit state in debug builds, clears bits, and decrements `used`.

## State And Persistence
State is `idm->bitmap`, `idm->total`, and `idm->used`, protected by `guc->submission_state.lock`. The manager persists until DRM cleanup; teardown reports unclean allocations when debug is enabled.

## Dependencies And Integration Points
Depends on bitmap helpers, DRM managed cleanup, GuC submission lock, `GUC_ID_MAX`, and GT printing/assertion helpers. It backs GuC execution queue IDs and PF-to-VF context ID partitioning.

## Risks And Test Signals
`used` must remain synchronized with bitmap state; double release or out-of-range release is caught only by assertions. High-end PF allocations intentionally differ from low-end submission allocations, so tests should verify both strategies. Built-in KUnit coverage is included through `tests/xe_guc_id_mgr_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.h

## Purpose
Declares the public interface for the GuC context ID manager.

## Important APIs, Types, And Functions
The header forward-declares `struct drm_printer` and `struct xe_guc_id_mgr`, then declares initialization, locked reserve/release, unlocked PF range reserve/release, and print APIs.

## Control Flow
The split between `_locked` and non-locked functions mirrors the C implementation: submission paths use the locked form under the GuC submission lock; PF provisioning calls the range APIs that lock internally.

## State And Persistence
The state layout is opaque to callers. Callers own allocated IDs/ranges until released through the paired functions.

## Dependencies And Integration Points
Included by GuC submission and SR-IOV resource management code.

## Risks And Test Signals
Misusing locking variants is the main interface risk. Compile-time users plus the C file’s KUnit tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_id_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.c

## Purpose
Implements helper routines for printing and counting GuC KLV buffers and mapping known KLV keys to readable names.

## Important APIs, Types, And Functions
Exports `xe_guc_klv_key_to_string`, `xe_guc_klv_print`, and `xe_guc_klv_count`. The key-to-string switch covers global config, VGT policy, VF config, and generated VF threshold keys.

## Control Flow
Printing iterates while at least a minimum KLV header remains, extracts key and length with bitfield helpers, validates that the value fits in the remaining dwords, and prints no-value, 32-bit, 64-bit, or byte-dump forms. Counting walks the same length encoding and returns `-ENODATA` if any trailing/truncated data remains.

## State And Persistence
No persistent state is stored. Functions parse caller-provided u32 buffers.

## Dependencies And Integration Points
Depends on `abi/guc_klvs_abi.h`, DRM printers, and threshold macros from `xe_guc_klv_thresholds_set.h`. Used by SR-IOV policy/config debug and validation paths that need readable KLV diagnostics.

## Risks And Test Signals
Parsing trusts ABI length encoding and avoids overruns by checking remaining dwords. `xe_guc_klv_print` intentionally stops on truncation. Tests should include zero-length, 32-bit, 64-bit, long payload, unknown key, generated threshold key, and truncated buffer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.h

## Purpose
Declares KLV helper functions and defines macros for constructing GuC KLV headers and tag-derived constants.

## Important APIs, Types, And Functions
Declares key stringification, printing, and counting. Defines `PREP_GUC_KLV`, `PREP_GUC_KLV_CONST`, `MAKE_GUC_KLV_KEY`, `MAKE_GUC_KLV_LEN`, and `PREP_GUC_KLV_TAG`.

## Control Flow
The macros expand ABI key/length names and field-prep operations at compile time, allowing callers to build KLV headers consistently.

## State And Persistence
No state is owned. Macros and functions operate on caller-owned KLV buffers.

## Dependencies And Integration Points
Uses Linux argument/concatenation utilities, types, and GuC KLV bit masks. It is a shared dependency for threshold helpers and SR-IOV GuC KLV construction.

## Risks And Test Signals
Macro correctness depends on ABI naming conventions such as `GUC_KLV_<TAG>_KEY` and `_LEN`. Compile failures are expected if a tag is not defined, which is a useful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set.h

## Purpose
Provides generated-style conversion helpers between tracked VF adverse-event threshold KLV keys and driver enum indexes.

## Important APIs, Types, And Functions
Defines `MAKE_GUC_KLV_VF_CFG_THRESHOLD_KEY`, `MAKE_GUC_KLV_VF_CFG_THRESHOLD_LEN`, `xe_guc_klv_threshold_key_to_index`, and `xe_guc_klv_threshold_index_to_key`. Both conversion functions expand `MAKE_XE_GUC_KLV_THRESHOLDS_SET`.

## Control Flow
Key-to-index switches over ABI-derived threshold keys and returns `-1` for untracked keys. Index-to-key switches over generated enum values and returns zero for malformed indexes.

## State And Persistence
No runtime state is held; the source of truth is the threshold set macro in the companion types header.

## Dependencies And Integration Points
Depends on GuC KLV ABI definitions, generic KLV helper macros, and threshold index definitions. Used by code that stores threshold values by compact driver index while exchanging ABI keys with GuC.

## Risks And Test Signals
The generated conversions must stay in lockstep with the threshold set macro and firmware ABI. Tests should check every threshold key round-trips key to index to key and that unknown keys fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set_types.h

## Purpose
Defines the single macro list of tracked GuC VF adverse-event threshold KLVs and derives the count and enum indexes from it.

## Important APIs, Types, And Functions
`MAKE_XE_GUC_KLV_THRESHOLDS_SET` lists thresholds for CAT errors, engine resets, page faults, H2G storms, IRQ storms, doorbell storms, and multi-LRC count with a firmware-version annotation. `XE_GUC_KLV_NUM_THRESHOLDS` computes the count, and `enum xe_guc_klv_threshold_index` generates indexes.

## Control Flow
There is no runtime flow. Other headers expand the macro list to generate switch cases, string names, and indexes.

## State And Persistence
No state is stored; this file is a compile-time source of truth.

## Dependencies And Integration Points
Depends on `xe_args.h` macro utilities. Integrated with KLV stringification and threshold key/index helpers.

## Risks And Test Signals
Adding a threshold in one place updates generated users, but ABI key and length definitions must exist. Compile-time failures catch missing ABI constants; round-trip conversion tests catch ordering or count mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_klv_thresholds_set_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.c

## Purpose
Manages the GuC log buffer, captures host snapshots, prints them as ASCII85 debug dumps or binary LFD streams, and tracks GuC log buffer overflow counters.

## Important APIs, Types, And Functions
Exports `xe_guc_log_init`, `xe_guc_log_print`, `xe_guc_log_print_lfd`, `xe_guc_log_print_dmesg`, `xe_guc_log_snapshot_capture`, `xe_guc_log_snapshot_print`, `xe_guc_log_snapshot_free`, and `xe_guc_check_log_buf_overflow`. Internal LFD helpers parse log-init configuration, find buffer markers, emit typed payloads, and stream wrapped event/crash buffers.

## Control Flow
Initialization allocates a managed pinned/mapped system GGTT BO of `GUC_LOG_SIZE`, zeros it, and stores the module log level. Snapshot capture refuses missing BOs, allocates a snapshot object and 2 MiB chunks, copies the mapped BO into those chunks, samples GuC timestamp under forcewake if possible, and records kernel time and firmware version metadata. Printing emits metadata plus an ASCII85 blob. LFD printing loads LIC/config data from the state header, emits required FW and OS payloads, then emits event and crash dump payloads when present. Overflow checking compares a sampled full counter to the previous sample and compensates for 4-bit wrap.

## State And Persistence
Persistent log state is `log->bo`, `log->level`, and per-log-type overflow stats. Snapshots are independent heap allocations that persist until explicitly freed and can be produced from atomic or non-atomic contexts using chunked allocation.

## Dependencies And Integration Points
Depends on GuC log and LFD ABI headers, Xe BO/map/MMIO/forcewake helpers, firmware version state, module parameters, DRM printers, and devcoredump/debugfs users. Debugfs exposes text, LFD, and dmesg dump entry points.

## Risks And Test Signals
Snapshot allocation can fail partially and must free all chunks. LFD parsing trusts marker/header layout in the GuC log buffer; malformed pointers could produce bad output if firmware layout changes. Overflow tracking assumes a 4-bit full counter. Test signals include debugfs log dump readability, LFD decoder acceptance, fault-injected init failures, and overflow notices when GuC reports full-count changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.h

## Purpose
Declares GuC log APIs and compile-time log buffer sizing for debug, crash dump, and state capture data.

## Important APIs, Types, And Functions
Defines per-build buffer sizes, aggregate `GUC_LOG_SIZE`, offsets for event/crash/state capture areas, log-level conversion macros, and public init/print/snapshot/overflow APIs. It also provides inline `xe_guc_log_get_level`.

## Control Flow
Callers initialize the log object, use print or snapshot APIs to inspect it, and call overflow checking when GuC reports buffer-full counters. Log level macros translate between driver log levels and GuC verbosity fields.

## State And Persistence
State is in `struct xe_guc_log` from the types header. Buffer size choices persist for the compiled kernel configuration.

## Dependencies And Integration Points
Includes GuC log ABI and log type definitions. Used by GuC load parameter construction, debugfs, devcoredump, and overflow monitoring.

## Risks And Test Signals
Size and offset constants must match firmware expectations and control dword encoding. Build variants change memory footprint substantially. Tests should cover log-level conversions and ensure offsets remain contiguous within `GUC_LOG_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log_types.h

## Purpose
Defines persistent and snapshot state structures for GuC logging.

## Important APIs, Types, And Functions
`struct xe_guc_log_snapshot` stores copied chunks, total size, timestamps, log level, firmware versions, and firmware path. `struct xe_guc_log` stores live log level, the mapped GuC log BO, and overflow/flush stats indexed by GuC log buffer type.

## Control Flow
The implementation fills `xe_guc_log` during init and populates snapshots during capture. Snapshot users print or dump the captured data and then free it.

## State And Persistence
`xe_guc_log` persists with the GuC object. Snapshots persist independently from live GuC memory until freed, which makes them suitable for later coredump/debug output.

## Dependencies And Integration Points
Includes GuC log ABI and firmware version types, and forward-declares `struct xe_bo`.

## Risks And Test Signals
`copy` is an array of chunk pointers rather than a flat allocation, so all users must iterate by `num_chunks` and honor `size`. Test signals include snapshot capture/free under fault injection and coredump output with large buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_log_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.c

## Purpose
Bridges GuC page-fault G2H messages into the generic Xe pagefault layer and sends GuC page-fault response descriptors.

## Important APIs, Types, And Functions
Exports `xe_guc_pagefault_handler`. Internal `guc_ack_fault` implements `struct xe_pagefault_ops.ack_fault` by building `XE_GUC_ACTION_PAGE_FAULT_RES_DESC` and sending it through the GuC CT.

## Control Flow
The handler validates the message length against `struct xe_guc_pagefault_desc`, populates `xe_pagefault.consumer` fields from GuC bitfields, handles Xe2 TRVA faults as NACKs, stores the original producer message and GuC private pointer, then calls `xe_pagefault_handler`. When the generic layer acknowledges, `guc_ack_fault` reconstructs ASID, VFID, prefetch, engine, and private data fields and sends a response descriptor.

## State And Persistence
The function uses a stack `struct xe_pagefault`; persistence is limited to the original GuC message copied into the producer buffer for later ack construction.

## Dependencies And Integration Points
Depends on GuC action/page-fault ABI masks from `xe_guc_fwif.h`, `xe_guc_ct_send`, and the generic `xe_pagefault` subsystem. It integrates GuC UM page-fault producer data with host VM fault resolution.

## Risks And Test Signals
The code comments note that GuC values currently match Xe pagefault enums and require remapping if that changes. The `PFR_SUCCESS` bit is derived from `!!err`, which is a semantic hotspot worth checking against firmware ABI expectations. Tests should cover exact length validation, TRVA/NACK mapping, prefetch handling, and CT response contents for success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.h

## Purpose
Declares the GuC page-fault G2H handler.

## Important APIs, Types, And Functions
Forward-declares `struct xe_guc` and declares `xe_guc_pagefault_handler(struct xe_guc *guc, u32 *msg, u32 len)`.

## Control Flow
GuC CT message dispatchers call this handler when a page-fault message arrives.

## State And Persistence
The header owns no state. Handler state is transient in the implementation.

## Dependencies And Integration Points
Includes Linux integer types and is consumed by GuC CT receive dispatch code.

## Risks And Test Signals
The interface exposes raw message dwords and length, so callers must pass the exact GuC payload. Compile coverage and CT dispatch tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.c

## Purpose
Implements GuC Power Conservation support outside the GuC RC-specific file: SLPC startup/reset, frequency bounds and user limits, power profiles, platform workarounds, C-state/status reads, residency counters, and teardown frequency handling.

## Important APIs, Types, And Functions
Exports init/start/stop/print, generic SLPC param set/unset, frequency getters/setters, RP0/RPa/RPe/RPn getters, current/actual frequency reads, power profile get/set, RC6/MC6 residency, early RP value init, unslice raise, stashed frequency restore, and flush-frequency limit apply/remove. Important internal helpers include `wait_for_pc_state`, `pc_action_reset`, `pc_action_query_task_state`, `pc_set_min_freq`, `pc_set_max_freq`, `pc_adjust_freq_bounds`, `pc_init_freqs`, `pc_set_mert_freq_cap`, and `pc_modify_defaults`.

## Control Flow
Init skips when `skip_guc_pc` is set; otherwise it initializes `freq_lock`, allocates a pinned mapped SLPC shared-data BO, sets the default power profile, and registers hardware teardown. Early init reads fused RP bounds under forcewake. Start takes forcewake, handles skip mode by requesting maximum frequency manually, clears shared data, writes the shared-data size, sends SLPC reset, waits for `SLPC_GLOBAL_STATE_RUNNING` with a short then extended timeout, modifies platform defaults, initializes and clamps frequency bounds, restores user requests, applies MERT caps, enables compute strategy, and writes the cached power profile. Stop marks frequencies not ready. Getters/setters lock `freq_lock`, query GuC task state when needed, and reject operations while reset/stop leaves `freq_ready` false.

## State And Persistence
Persistent state includes the shared-data BO, fused `rp0_freq`/`rpn_freq`, user-requested min/max, stashed min/max for unload or workarounds, `flush_freq_limit`, `freq_ready`, `freq_lock`, and `power_profile`. User-requested limits survive resets through `pc_adjust_requested_freq`; stashed values are restored by `xe_guc_pc_restore_stashed_freq`.

## Dependencies And Integration Points
Depends on SLPC GuC action ABI, GuC CT, Xe BO/map/MMIO/forcewake/pcode/PM helpers, GT throttle and idle support, generated WA tables, SR-IOV mode checks, and platform registers for TGL/PVC/MTL-class frequency data. It interacts with `xe_guc_rc.c` because GuC RC mode is controlled through SLPC messages.

## Risks And Test Signals
The state machine is timing-sensitive: startup failure disables dynamic frequency and GT sleep states. Frequency setters must respect `freq_ready`, RP bounds, user limits, and platform workarounds. The flush cap workaround serializes user max-frequency updates with `wait_var_event_timeout`, and failures can leave caps active until removal. Test signals include SLPC running state, sysfs/debugfs min/max round trips, reset recovery preserving user limits, power-profile changes, WA-specific flush frequency behavior, and teardown without wedged-device CT errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.h

## Purpose
Declares the public GuC Power Conservation API.

## Important APIs, Types, And Functions
The header exposes lifecycle functions, debug printing, generic SLPC parameter operations, frequency queries and setters, power profile operations, C-state/residency queries, early init, stashed restore, unslice raise, and flush-frequency cap controls.

## Control Flow
Typical callers perform early RP initialization under forcewake, initialize the PC object, start it after GuC is ready, use frequency/profile APIs during runtime, stop on reset/suspend, and rely on managed teardown for final hardware cleanup.

## State And Persistence
State is opaque through `struct xe_guc_pc`, whose layout is in `xe_guc_pc_types.h`.

## Dependencies And Integration Points
Used by GT power management, sysfs/debugfs controls, GuC RC, reset/suspend/resume paths, and cache-flush workaround code.

## Risks And Test Signals
Callers must respect forcewake requirements for early/current FW-only reads and handle `-EAGAIN` while PC is not ready. Compile coverage plus runtime PM/frequency sysfs tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc_types.h

## Purpose
Defines persistent state for GuC Power Conservation.

## Important APIs, Types, And Functions
`struct xe_guc_pc` stores the shared-data BO, flush-frequency atomic flag, fused RP0/RPn bounds, user requested min/max, stashed min/max, frequency mutex, readiness flag, and selected power profile.

## Control Flow
The implementation mutates these fields during early init, start, sysfs/debugfs frequency changes, reset recovery, flush workaround entry/exit, and final teardown.

## State And Persistence
The fields persist with the GuC object. `user_requested_*` preserve administrative intent, while `stashed_*` preserve temporary cap/unload values. `freq_ready` gates reads/writes during reset transitions.

## Dependencies And Integration Points
Includes Linux mutex/types and forward-references `struct xe_bo` through the BO pointer. The struct is embedded in `struct xe_guc`.

## Risks And Test Signals
The mutex must protect frequency limit fields except the atomic flush flag. Tests should validate no stale stashed limits remain after workaround removal or reset restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.c

## Purpose
Implements GuC Render C-state control, specifically enabling or disabling GuC ownership of RC6 in coordination with host GT idle logic.

## Important APIs, Types, And Functions
Exports `xe_guc_rc_init`, `xe_guc_rc_enable`, and `xe_guc_rc_disable`. Internal `guc_action_setup_gucrc` sends `GUC_ACTION_HOST2GUC_SETUP_PC_GUCRC` with either host or firmware control. `xe_guc_rc_fini_hw` disables GuC RC on managed teardown.

## Control Flow
Init asserts UC is enabled and registers hardware finalization. Enable takes GT forcewake and fails if forcewake cannot be acquired. PVC disables GuC RC and returns success. If GuC PC is skipped, it enables host C6 and does not send SLPC RC mode messages. Otherwise it requests firmware control. Disable requests host control when GuC PC is active and non-PVC, then disables host C6 through `xe_gt_idle_disable_c6`.

## State And Persistence
This file owns no dedicated struct fields; state is firmware RC mode plus host idle state. The managed action persists until device teardown and skips work on wedged devices.

## Dependencies And Integration Points
Depends on SLPC RC action ABI, GuC CT, forcewake, device wedge checks, GuC PC skip/platform flags, and `xe_gt_idle`. It is separate from `xe_guc_pc.c` but uses SLPC H2G calls for mode override.

## Risks And Test Signals
Enable/disable semantics vary by platform and `skip_guc_pc`. CT failures are logged unless caused by wedged cancellation. Test signals include RC6 residency changes, host C6 enable/disable behavior when PC is skipped, and teardown without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.h

## Purpose
Declares the GuC Render C-state control API.

## Important APIs, Types, And Functions
Forward-declares `struct xe_guc` and `enum slpc_gucrc_mode`, then declares init, enable, and disable functions.

## Control Flow
Callers initialize once, enable RC during GuC/GT power setup, and disable it during teardown or when reclaiming host control.

## State And Persistence
No state is exposed by the header; firmware and GT idle state are controlled by the implementation.

## Dependencies And Integration Points
Used by GT/GuC power-management setup and teardown paths.

## Risks And Test Signals
The header has a very small surface. Compile coverage and runtime RC enable/disable paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.c

## Purpose
Implements SR-IOV PF/VF relay communication over GuC. It wraps inner PF/VF HXG messages with GuC relay transport headers, tracks request/response transactions, queues incoming actions to a worker, and forwards PF service requests.

## Important APIs, Types, And Functions
Exports `xe_guc_relay_init`, `xe_guc_relay_send_to_pf`, `xe_guc_relay_process_guc2vf`, and, under `CONFIG_PCI_IOV`, `xe_guc_relay_send_to_vf` and `xe_guc_relay_process_guc2pf`. Internal `struct relay_transaction` stores transport buffers, inner request/response pointers, remote ID, relay ID, completion, reply status, and list link. Important helpers include `prepare_pf2guc`, `prepare_vf2guc`, `relay_send_message_and_wait`, `relay_handle_reply`, `relay_process_msg`, and `relay_process_incoming_action`.

## Control Flow
Initialization is a no-op outside SR-IOV; otherwise it initializes spinlock, worker, lists, ratelimit state, and a mempool sized for PF/VF usage. Outgoing requests allocate a transaction, assign a monotonically increasing relay ID, build the outer GuC header, queue the transaction on `pending_relays`, send via blocking CT, and wait up to 2.5 seconds for completion. Busy replies continue waiting, retry replies resend, success copies response data, and failure maps relay error to errno. Incoming GuC relay events validate mode, length, origin, data0, and VF ID, then dispatch the inner message. Requests/events are queued to the worker; replies complete pending transactions.

## State And Persistence
Persistent relay state is the spinlock, worker, `pending_relays`, `incoming_actions`, mempool, last relay ID, and diagnostic ratelimit. Transactions live in the mempool while queued, pending, or being processed. Incoming transactions may be requeued when handlers return in-progress/busy.

## Dependencies And Integration Points
Depends on SR-IOV GuC action and relay ABI headers, GuC CT, HXG helpers, Xe SR-IOV mode checks, PF service dispatch, KUnit static stubs, ratelimit infrastructure, and the device SR-IOV workqueue.

## Risks And Test Signals
Concurrency correctness depends on list operations under `relay->lock` and completions outside the lock. Incoming messages may be delivered under CTB lock, so GFP_ATOMIC/GFP_NOWAIT mempool allocation is intentional. Relay ID wrap is not specially handled beyond u32 increment. Test signals include relay KUnit tests, testloop opcodes for nop/busy/retry/echo/fail, timeout behavior, PF/VF permission checks, and response buffer length enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.h

## Purpose
Declares the GuC SR-IOV relay communication API.

## Important APIs, Types, And Functions
Declares initialization, VF-to-PF send, GuC-to-VF processing, and conditional PF-to-VF send and GuC-to-PF processing. When `CONFIG_PCI_IOV` is disabled, PF APIs are inline stubs returning `-ENODEV`.

## Control Flow
PF and VF callers use send APIs for synchronous request/response relay and GuC CT dispatchers call process APIs for incoming relay events.

## State And Persistence
The header exposes only opaque `struct xe_guc_relay`; implementation-owned lists, mempool, worker, and counters persist in that object.

## Dependencies And Integration Points
Includes Linux types and errno. Integrated with SR-IOV PF services, VF drivers, and GuC CT receive dispatch.

## Risks And Test Signals
Build configuration changes API behavior for PF calls. Callers must handle `-ENODEV` when SR-IOV relay support is unavailable. Compile coverage across PCI_IOV enabled/disabled builds is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay_types.h

## Purpose
Defines persistent state for VF-PF relay communication over GuC.

## Important APIs, Types, And Functions
`struct xe_guc_relay` contains a spinlock, worker, pending transaction list, incoming action list, transaction mempool, last relay ID, and diagnostic ratelimit state.

## Control Flow
The implementation initializes these fields only in SR-IOV mode. Send paths append to `pending_relays`; receive paths append to `incoming_actions`; the worker drains incoming actions; teardown exits the mempool.

## State And Persistence
All fields persist with the GuC object. `last_rid` is monotonically incremented for outgoing transactions, and the mempool bounds allocation in contexts where sleeping allocation is unsafe.

## Dependencies And Integration Points
Uses Linux mempool, ratelimit, spinlock, list, and workqueue types. The struct is embedded in `struct xe_guc`.

## Risks And Test Signals
The lists must be initialized before use and protected by `lock`. Mempool exhaustion affects relay availability under CTB-lock receive context. Relay KUnit and SR-IOV integration tests should verify pending and incoming list transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay_types.h -->
