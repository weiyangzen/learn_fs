# subset-b-003615 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_workarounds.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_workarounds.c

### Purpose
`selftest_workarounds.c` is the live i915 GT workaround validation suite. It proves that hardware workaround lists and per-engine RING_NONPRIV whitelists are programmed as expected, remain valid across engine/GPU/GuC reset paths, and preserve context isolation semantics.

### Important APIs, Types, And Functions
The public entry is `intel_workarounds_live_selftests()`, which runs `live_dirty_whitelist()`, `live_reset_whitelist()`, `live_isolated_whitelist()`, `live_gpu_reset_workarounds()`, and `live_engine_reset_workarounds()`. Supporting helpers include `reference_lists_init()`, `verify_wa_lists()`, `read_nonprivs()`, `check_whitelist()`, `check_dirty_whitelist()`, `read_whitelisted_registers()`, `scrub_whitelisted_registers()`, and reset adapters for device, engine, and GuC paths. Core types include `struct wa_lists`, `struct intel_context`, `struct intel_engine_cs`, `struct i915_vma`, and `struct igt_spinner`.

### Control Flow
The tests build reference GT, engine, and context workaround lists, create temporary contexts and scratch objects, submit MI commands that read or write whitelisted registers, and compare GPU-written results with expected register offsets or write-mask behavior. Reset tests start spinner requests to force active reset handling, perform engine/GPU/GuC resets under runtime PM and the global reset lock, then verify both existing and fresh contexts. Isolation tests scrub writable whitelist registers in one context and confirm another context still reads defaults.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is transient except for GPU register/context state observed during requests. The file depends on i915 GEM internal objects, VMA pinning, ring command emission, workaround list builders, scheduler selftest policy hooks, spinner helpers, and reset APIs. It integrates with i915 live selftests and intentionally wedges or reports errors when register programming hangs or mismatches. Risks center on command buffer math, reserved/write-only/read-only register exceptions, reset timing, GuC scheduling differences, and platform-specific pardon lists. Useful signals are whitelist slot dumps, mismatch logs, reset failure messages, `igt_flush_test()`, and wedge detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_workarounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.c

### Purpose
`mock_timeline.c` provides a tiny initializer/finalizer for `struct intel_timeline` instances used by selftests that do not need a full GT-backed timeline.

### Important APIs, Types, And Functions
It exports `mock_timeline_init()` and `mock_timeline_fini()`. The code initializes `timeline->fence_context`, `timeline->mutex`, `timeline->last_request`, `timeline->requests`, `timeline->sync`, and `timeline->link`, while deliberately leaving `timeline->gt` as `NULL`.

### Control Flow
Initialization is direct field setup followed by `i915_syncmap_init()`. Finalization releases only the sync map via `i915_syncmap_free()`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The object is caller-owned and persists only for the selftest lifetime. It depends on `intel_timeline.h`, active fence/list primitives, mutexes, and sync maps. It integrates with mock request/timeline tests that require a valid fence context without hardware. Risks are limited to callers expecting GT-backed behavior or forgetting to call the finalizer. Test signals are leak-free sync-map teardown and correct fence-context propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.h

### Purpose
`mock_timeline.h` declares the mock timeline lifecycle helpers for i915 selftest code.

### Important APIs, Types, And Functions
It forward-declares `struct intel_timeline` and declares `mock_timeline_init(struct intel_timeline *timeline, u64 context)` plus `mock_timeline_fini(struct intel_timeline *timeline)`.

### Control Flow
The header has no runtime control flow; it gates inclusion with `__MOCK_TIMELINE__`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends only on Linux integer types. It integrates with selftest modules that want mock timelines without pulling implementation details into every test. Risks are prototype drift with `mock_timeline.c` or accidental use outside selftest-only contexts. Test signals are compile-time coverage by mock timeline users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftests/mock_timeline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/hsw.asm -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/hsw.asm

### Purpose
`hsw.asm` is a Haswell EU assembly clear kernel for PAVP buffer/cache clearing. It clears assigned GRFs with a caller-provided word and writes zeroes to a 32x16 render-target block to indirectly clear 512 bytes of render/data cache.

### Important APIs, Types, And Functions
The file is raw GPU assembly, not C. Its contract is the documented curbe layout in `g1`, BTI 0 for the 2D cache-clearing surface, and optional BTI 1 instrumentation storage. It uses state register fields, media block read/write sends, a delay loop, address register `a0`, and thread spawner EOT.

### Control Flow
The kernel stores the clear word, optionally records per-EU/thread instrumentation by deriving slice, half-slice, EU, and thread slot IDs from `sr0`, executes a programmable delay, writes two 16x16 zero media blocks, loops through GRF ranges clearing them, and terminates the thread.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State exists in EU registers and the render/instrumentation surfaces for one dispatch. It depends on HSW send message descriptors and state-register bit layout; the HSW jump distances differ from IVB. It integrates with i915 PAVP/GSC-style clear-kernel dispatch code and generated shader binaries. Risks include generation-specific instruction encoding, off-by-one jump offsets, instrumentation buffer sizing, and curbe/BTI mismatch. Test signals are successful cache clearing, valid instrumentation counts, no EU hangs, and correct EOT completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/hsw.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/ivb.asm -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/ivb.asm

### Purpose
`ivb.asm` is the Ivy Bridge variant of the PAVP/cache clear EU kernel. It performs the same GRF clearing and 32x16 zero block writes as the HSW version with IVB-appropriate branch distances and state-register assumptions.

### Important APIs, Types, And Functions
The shader consumes the documented curbe dwords, BTI 0 render target, and optional BTI 1 instrumentation buffer. It uses media block read/write messages, state register decoding, delay-loop arithmetic, indirect GRF writes through `a0`, and EOT via the thread spawner.

### Control Flow
It conditionally skips instrumentation, otherwise increments the histogram cell for the running EU/thread, delays for the requested iterations, writes zero blocks through BTI 0, loops over GRFs writing the clear word, then sends EOT.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The only persistent effect is on the bound surfaces. It depends on IVB/HSW-compatible but generation-sensitive EU assembly encodings and is consumed by i915 shader build/use paths. Risks include stale jump offsets, invalid surface layout assumptions, and register state differences across platforms. Test signals are clean kernel completion, expected render-cache clearing, and instrumentation rows matching executed threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shaders/clear_kernel/ivb.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.c

### Purpose
`shmem_utils.c` provides i915 helpers for creating shmem files from data or GEM objects, pin-vmapping shmem-backed files, and reading/writing file contents page by page.

### Important APIs, Types, And Functions
Exports are `shmem_create_from_data()`, `shmem_create_from_object()`, `shmem_pin_map()`, `shmem_unpin_map()`, `shmem_read_to_iosys_map()`, `shmem_read()`, and `shmem_write()`. Internals include `__shmem_rw()` and use `struct file`, `struct page`, `struct iosys_map`, and `struct drm_i915_gem_object`.

### Control Flow
Creation allocates a tmpfs file with `shmem_file_setup()` and writes initial data, or returns an existing shmem GEM filp with an extra ref. Non-shmem GEM objects are CPU-mapped, copied into a new shmem file, and unmapped. Mapping collects all pages, `vmap()`s them with `VM_MAP_PUT_PAGES`, and marks the mapping unevictable until unpinned. Read/write helpers iterate pages, kmap locally, copy, dirty on write, mark accessed, and drop page refs.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is the shmem file contents and temporary unevictable mapping state. Dependencies include tmpfs, page cache APIs, vmap, iosys-map copying, GEM shmem/lmem helpers, and optional included selftests. Integration points include GuC ADS golden-context copying and firmware/data staging that needs file-like shmem. Risks include file-size page alignment assumptions, `void *` pointer arithmetic, unevictable state leaks if unpin is skipped, and handling lmem with WC mappings. Test signals include `st_shmem_utils.c`, read/write round trips, map visibility of writes, and failure unwinds on page or vmap allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.h

### Purpose
`shmem_utils.h` is the public declaration surface for i915 GT shmem helper routines.

### Important APIs, Types, And Functions
It declares shmem creation, pin-map/unpin-map, iosys-map read, raw read, and raw write helpers for `struct file`, `struct drm_i915_gem_object`, and `struct iosys_map`.

### Control Flow
The header has no runtime flow beyond include guarding.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on forward declarations plus Linux types. It integrates C users such as GuC ADS and selftests with the implementation. Risks are prototype drift or misuse without honoring the pin/unpin lifetime contract. Test signals are compile coverage and the mock shmem selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/shmem_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/st_shmem_utils.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/st_shmem_utils.c

### Purpose
`st_shmem_utils.c` is the selftest companion for the shmem utilities, included only when `CONFIG_DRM_I915_SELFTEST` is enabled.

### Important APIs, Types, And Functions
It defines `igt_shmem_basic()` and `shmem_utils_mock_selftests()`. The test uses `shmem_create_from_data()`, `shmem_read()`, `shmem_write()`, `shmem_pin_map()`, `shmem_unpin_map()`, and `fput()`.

### Control Flow
The test creates a shmem file from `0xdeadbeef`, reads it back, overwrites it with `0xc0ffee`, maps the file, verifies mapped contents, then unmaps and releases the file.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is a short-lived shmem file and mapping. It depends directly on the implementation file that includes it and the i915 selftest harness. It integrates as a mock selftest entry. Risks are narrow: the test is intentionally basic and does not cover partial-page, multipage, or error paths. Its signal is a simple API round-trip that catches broken copy, dirtying, and mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/st_shmem_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.c

### Purpose
`sysfs_engines.c` creates `/sys/.../engine/<engine>/` nodes exposing i915 engine identity, uABI capabilities, scheduler/reset/heartbeat tunables, and default values.

### Important APIs, Types, And Functions
The public entry is `intel_engines_add_sysfs()`. It defines `struct kobj_engine`, show/store callbacks for `name`, `class`, `instance`, `mmio_base`, `capabilities`, `known_capabilities`, `max_busywait_duration_ns`, `timeslice_duration_ms`, `stop_timeout_ms`, `preempt_timeout_ms`, and optionally `heartbeat_interval_ms`. Helpers include `__caps_show()`, `repr_trim()`, `kobj_engine()`, and `add_defaults()`.

### Control Flow
Initialization creates an `engine` kobject under the DRM primary device, iterates uABI engines, creates one kobject per engine, installs base files, conditionally installs timeslice/preempt files, and creates a `.defaults` child with read-only default attributes. Store callbacks parse integers, clamp against engine-specific limits, reject unclamped values with `-EINVAL`, update `engine->props`, and adjust active timers or heartbeat state when needed.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is in the sysfs kobjects and mutable `engine->props`; defaults are read from `engine->defaults`. Dependencies include Linux kobject/sysfs APIs, i915 timer utilities, execlists scheduling state, heartbeat control, and engine uABI metadata. Integration is user/admin-facing sysfs tuning. Risks include partial sysfs creation on failures, capability string truncation, concurrent property reads/writes using `READ_ONCE`/`WRITE_ONCE`, and exposing invalid timings. Test signals are sysfs file presence by engine capability, rejected out-of-range writes, timer updates on active engines, and correct `.defaults` contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.h

### Purpose
`sysfs_engines.h` declares the i915 engine sysfs registration entry point.

### Important APIs, Types, And Functions
It forward-declares `struct drm_i915_private` and declares `intel_engines_add_sysfs(struct drm_i915_private *i915)`.

### Control Flow
There is no runtime flow; the include guard protects the declaration.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state. It integrates GT/device setup code with `sysfs_engines.c`. Risks are limited to declaration mismatch. Compile-time users provide the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/sysfs_engines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_abi.h

### Purpose
`guc_actions_abi.h` defines GuC host-to-firmware action IDs and message field layouts for self-configuration, CTB control, legacy GuC actions, logging, reset, HuC auth, scheduling, capture, TLB invalidation, and power-management commands.

### Important APIs, Types, And Functions
Key definitions include `GUC_ACTION_HOST2GUC_SELF_CFG`, `HOST2GUC_SELF_CFG_*`, `GUC_ACTION_HOST2GUC_CONTROL_CTB`, `GUC_CTB_CONTROL_*`, `enum intel_guc_action`, response/status enums, log-control bit masks, state-capture event status, and TLB invalidation type/mode flags.

### Control Flow
The header has no executable flow; it encodes request and response dword contracts used by GuC MMIO/CT senders and G2H handlers.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
No state is stored here. It depends on HXG message definitions included by users and integrates with `intel_guc.c`, CT communication, SLPC, HuC auth, and submission code. Risks are ABI drift with firmware, wrong bit masks, and legacy action compatibility. Test signals are successful GuC boot/self-config, CTB enablement, expected firmware responses, and error handling for retry/failure statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_slpc_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_slpc_abi.h

### Purpose
`guc_actions_slpc_abi.h` defines the GuC SLPC shared-data layout, task/frequency/override structures, event IDs, parameter IDs, and H2G request format used for firmware-driven GT power management.

### Important APIs, Types, And Functions
Important definitions include `SLPC_SHARED_DATA_SIZE_*`, `SLPC_MAX_OVERRIDE_PARAMETERS`, `enum slpc_param_id`, `enum slpc_event_id`, task-state flags, `struct slpc_task_state_data`, `struct slpc_shared_data_header`, `struct slpc_override_params`, `struct slpc_shared_data`, `struct slpc_context_frequency_request`, and `GUC_ACTION_HOST2GUC_PC_SLPC_REQUEST` field masks.

### Control Flow
There is no C control flow. The layout describes how host and GuC exchange SLPC state and how host emits SLPC events with an event ID, argument count, and event data dwords.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state lives in the shared data buffer allocated elsewhere and interpreted through these structs. Dependencies are Linux packed types and GuC HXG definitions used by senders. Integration points are `intel_guc_slpc` initialization, frequency controls, RC6/media-ratio policy, and power-profile handling. Risks include packed layout mismatch, size/alignment mistakes, and firmware parameter ID drift. Test signals include SLPC reaching `RUNNING`, valid task-state/frequency fields, accepted parameter set/unset events, and power-management behavior matching requested limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_slpc_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_ctb_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_ctb_abi.h

### Purpose
`guc_communication_ctb_abi.h` defines the command transport buffer ABI used for GuC host/firmware message streaming after early MMIO setup.

### Important APIs, Types, And Functions
It defines `struct guc_ct_buffer_desc`, CTB status bits, CTB header length/min/max constants, `GUC_CTB_MSG_0_*` field masks, `GUC_CTB_FORMAT_HXG`, and CTB HXG min/max lengths.

### Control Flow
There is no executable flow. The descriptor contract assigns `head` to the receiver and `tail` to the sender, while each stream record carries a header with fence, format, reserved bits, and payload length followed by embedded HXG dwords.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent shared state is the descriptor and circular buffer memory managed by `intel_guc_ct`. It depends on `guc_messages_abi.h` and packed layout rules. Integration points include GuC self-config KLVs, CT send/receive workers, and G2H event handling. Risks are head/tail corruption, overflow/underflow status handling, length mismatch, and firmware/header ABI drift. Test signals are CTB enablement, successful H2G/G2H traffic, status remaining `NO_ERROR`, and robust recovery from overflow or mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_ctb_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_mmio_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_mmio_abi.h

### Purpose
`guc_communication_mmio_abi.h` documents and bounds early GuC communication through software scratch registers.

### Important APIs, Types, And Functions
The key definition is `GUC_MAX_MMIO_MSG_LEN` set to 4. The header documents that MMIO messages embed HXG messages and that Gen11+ scratch registers are preferred where available.

### Control Flow
No code executes here. Runtime users write request dwords into scratch registers, trigger a GuC interrupt, and poll the first register for GuC-originated HXG response state.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is hardware scratch-register contents, not header-owned memory. Integration is through `intel_guc_send_mmio()` and early CTB/self-config setup. Risks include exceeding firmware-supported length, choosing wrong scratch base per generation/GT, and confusing MMIO with CTB once CT is enabled. Test signals are successful self-config and CTB setup before CT channel use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_mmio_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_errors_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_errors_abi.h

### Purpose
`guc_errors_abi.h` names GuC response, load, and bootrom status codes so driver diagnostics can interpret firmware boot and command failures.

### Important APIs, Types, And Functions
It defines `enum intel_guc_response_status`, `enum intel_guc_load_status`, and `enum intel_bootrom_load_status`, including ready, exception, invalid init-data, KLV workaround errors, and bootrom cryptographic/load-location failures.

### Control Flow
The header has no executable logic; values are consumed by status dump and load-failure handling code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
No state is stored. It integrates with GuC load-status registers and log/debug output. Risks are stale status names or overlapping ranges that mislead diagnostics. Test signals are meaningful `GUC_STATUS` decoding after boot, load failure, and firmware exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_errors_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_klvs_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_klvs_abi.h

### Purpose
`guc_klvs_abi.h` defines GuC key-length-value encodings for self-config, scheduling policy, context policy, and workaround KLVs.

### Important APIs, Types, And Functions
Important constants are `GUC_KLV_0_KEY`, `GUC_KLV_0_LEN`, self-config keys for H2G/G2H CTB addresses, descriptor addresses, and sizes, scheduling policy IDs, context policy IDs, and workaround keys such as serialized RA mode, block interrupts when MGSR blocked, and avoid GFX clear while active.

### Control Flow
No runtime flow exists; users pack key and length into the first dword and pass one or more value dwords through HOST2GUC self-config or ADS workaround KLV storage.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State lives in GuC self-config messages or ADS KLV sections. Integration includes `intel_guc_self_cfg32/64()` and `intel_guc_ads.c` workaround KLV setup. Risks are key/length mismatch, firmware version gating mistakes, and invalid GGTT addresses for CT buffers. Test signals include GuC acknowledging recognized KLVs, CT channel initialization, and platform workarounds taking effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_klvs_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_messages_abi.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_messages_abi.h

### Purpose
`guc_messages_abi.h` defines the HXG message grammar used by both MMIO and CTB GuC communication.

### Important APIs, Types, And Functions
It defines origin/type/aux masks, host and GuC origins, request/event/fast-request/busy/retry/failure/success types, request and event action/data masks, busy/retry fields, failure hint/error fields, response data fields, and deprecated message type macros.

### Control Flow
No executable flow exists. Runtime senders construct request or event dwords; receivers inspect origin and type, then branch between busy wait, retry, failure, or success handling.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The header owns no state but defines the wire format for `intel_guc_send_mmio()`, CT send/receive paths, SLPC requests, self-config, and G2H events. Risks are incorrect field extraction, failing to handle busy/retry, and mixing deprecated and HXG type encodings. Test signals are protocol-correct GuC replies, busy/retry handling, failure-code logging, and CT/MMIO interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_messages_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/guc_capture_fwif.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/guc_capture_fwif.h

### Purpose
`guc_capture_fwif.h` defines the firmware interface and driver-side bookkeeping for GuC error-state capture before engine resets.

### Important APIs, Types, And Functions
Key types include `struct __guc_capture_bufstate`, `struct __guc_capture_parsed_output`, `struct guc_debug_capture_list_header`, `struct guc_debug_capture_list`, `struct __guc_mmio_reg_descr`, `struct __guc_mmio_reg_descr_group`, `struct guc_state_capture_header_t`, `struct guc_state_capture_t`, `struct guc_state_capture_group_header_t`, `struct guc_state_capture_group_t`, `struct __guc_capture_ads_cache`, and `struct intel_guc_state_capture`.

### Control Flow
The header describes two flows: ADS registration of register lists for GuC to capture, and runtime parsing of logged capture groups into preallocated per-engine parsed-output nodes. It has no executable code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is owned by `intel_guc_state_capture`: static/ext register lists, ADS caches, null cache, preallocated cachelist, output list, and max register count. Dependencies include GuC firmware interface types, list heads, engine classes, and MMIO register descriptors. Integration points are `intel_guc_capture`, ADS capture-list population, G2H state capture notifications, and i915 GPU coredump reporting. Risks include packed layout mismatch, allocation constraints during reset/G2H handling, partial captures, and steered-register list validity. Test signals are populated ADS capture pointers, parsed coredump register groups, partial-capture flags, and no allocations in reset-sensitive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/guc_capture_fwif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_binary_headers.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_binary_headers.h

### Purpose
`intel_gsc_binary_headers.h` defines packed structures used to parse Intel GSC firmware binaries and extract partition, directory, and manifest metadata.

### Important APIs, Types, And Functions
It defines `struct intel_gsc_version`, `struct intel_gsc_partition`, `struct intel_gsc_layout_pointers`, `struct intel_gsc_bpdt_header`, `struct intel_gsc_bpdt_entry`, `struct intel_gsc_cpd_header_v2`, `struct intel_gsc_cpd_entry`, and `struct intel_gsc_manifest_header`, plus BPDT, CPD, entry type, offset, and compression masks.

### Control Flow
No code executes here. The structures support walking layout pointers, boot partitions, BPDT entries, CPD entries, and the manifest header in `intel_gsc_fw_get_binary_info()`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The header owns no state and depends only on packed integer types and bit macros. Integration is with GSC firmware selection/version parsing. Risks are binary-format drift, wrong packed layout, unchecked offsets in users, and string matching CPD entry names. Test signals include successful extraction of release/security versions and rejection of malformed signatures or undersized images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_binary_headers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.c

### Purpose
`intel_gsc_fw.c` manages GSC firmware status probing, binary metadata parsing, firmware copy/load submission, post-load compatibility query, and proxy-readiness status reporting.

### Important APIs, Types, And Functions
Exports are `intel_gsc_fw_get_binary_info()`, `intel_gsc_uc_fw_upload()`, `intel_gsc_uc_fw_init_done()`, `intel_gsc_uc_fw_proxy_init_done()`, and `intel_gsc_uc_fw_proxy_get_status()`. Important helpers include `gsc_is_in_reset()`, `gsc_uc_get_fw_status()`, `gsc_fw_load_prepare()`, `gsc_fw_load()`, `gsc_fw_wait()`, and `gsc_fw_query_compatibility_version()`. Local MKHI/GSC version message structs define the compatibility query payload.

### Control Flow
Binary parsing validates layout size, boot1 bounds, BPDT signature and entries, CPD marker and entries, finds `RBEP.man`, extracts release/security versions, and enforces MTL/ARL version rules. Upload skips if already initialized, sanitizes firmware state, requires GSC reset state, copies firmware into dedicated local memory, marks FLR-on-fini, submits `GSC_FW_LOAD`, waits for init complete, sends an MKHI compatibility query through HECI, verifies selected file version, and marks the firmware transferred pending proxy initialization.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `gsc->fw`, `gsc->release`, `gsc->security_version`, file-selected compatibility version, `gsc->local`, and uncore FLR cleanup intent. Dependencies include GSC binary headers, stolen/local memory mapping, GSC engine command submission, HECI packet submit, GuC VMA allocation, runtime PM, and HECI status registers. Integration points are `intel_gsc_uc` workqueue loading, MEI proxy setup, HuC-by-GSC auth, debugfs status, and firmware core version selection. Risks include malformed image offsets, stale firmware already running with inconsistent driver state, load timeouts, GSC not in reset, too-old ARL firmware, and compatibility-query protocol errors. Test signals are FWSTS init/proxy states, logged release/cv/SVN, load failure status, and valid MKHI reply size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.h

### Purpose
`intel_gsc_fw.h` declares the GSC firmware management API used by the GSC uC coordinator and status paths.

### Important APIs, Types, And Functions
It declares binary-info parsing, upload, init-done, proxy-init-done, and proxy status functions for `struct intel_gsc_uc`, `struct intel_uc_fw`, and `struct intel_uncore`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on forward declarations plus Linux types. It integrates `intel_gsc_uc.c`, debugfs, and proxy readiness checks with the firmware implementation. Risks are declaration drift or exposing status helpers without the necessary runtime-PM context. Compile coverage and GSC load/proxy tests are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.c

### Purpose
`intel_gsc_proxy.c` implements the i915 software proxy that relays messages between GT-integrated GSC firmware and CSME through the MEI GSC proxy component.

### Important APIs, Types, And Functions
Exports are `intel_gsc_proxy_init()`, `intel_gsc_proxy_fini()`, `intel_gsc_proxy_request_handler()`, and `intel_gsc_proxy_irq_handler()`. Internal pieces include `struct intel_gsc_proxy_header`, `struct gsc_proxy_msg`, `proxy_channel_alloc/free()`, `proxy_send_to_gsc()`, `proxy_send_to_csme()`, `validate_proxy_header()`, `proxy_query()`, and component bind/unbind callbacks.

### Control Flow
Initialization allocates a two-buffer GuC VMA channel and registers a typed component. Bind enables HECI2 interrupts and stores the MEI component; unbind clears it and disables interrupts. IRQ handling queues GSC work. The request handler waits for component binding, clears the HECI2 status bit, and runs `proxy_query()`: send query or CSME reply to GSC, wait for GSC output marker, validate GSC-to-CSME proxy header, send payload through MEI, receive CSME reply, validate CSME-to-GSC header, and repeat until GSC emits `PROXY_END`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state lives in `gsc->proxy`: component pointer, component-added flag, channel VMA, two mapped buffers, and mutex. Dependencies include Linux component framework, MEI proxy ops, GSC HECI submit, runtime PM, uncore HECI2 registers, and ordered GSC workqueue. Integration includes firmware-load proxy establishment and later proxy interrupts. Risks include component bind timeout, invalid message sizes, header source/destination mismatches, marker visibility/order, MEI send/recv failures, and interrupt handling before binding. Test signals are proxy init FWSTS normal state, HECI2 IRQ flow, MEI exchange success, and firmware status transition to running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.h

### Purpose
`intel_gsc_proxy.h` declares the software proxy lifecycle, request handling, and IRQ entry points for GSC-to-CSME mediation.

### Important APIs, Types, And Functions
It declares `intel_gsc_proxy_init()`, `intel_gsc_proxy_fini()`, `intel_gsc_proxy_request_handler()`, and `intel_gsc_proxy_irq_handler()` for `struct intel_gsc_uc`.

### Control Flow
The header has no runtime flow.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on Linux types plus a forward declaration. It integrates `intel_gsc_uc.c` work handling and interrupt plumbing with proxy implementation. Risks are limited to prototype drift. Compile and proxy init/IRQ coverage are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.c

### Purpose
`intel_gsc_uc.c` coordinates the GSC microcontroller lifecycle: early support detection, local memory allocation, pinned GSC context creation, delayed firmware loading, proxy servicing, HuC authentication sequencing, resume handling, teardown, and status printing.

### Important APIs, Types, And Functions
Exports include `intel_gsc_uc_init_early()`, `intel_gsc_uc_init()`, `intel_gsc_uc_fini()`, `intel_gsc_uc_flush_work()`, `intel_gsc_uc_resume()`, `intel_gsc_uc_load_start()`, and `intel_gsc_uc_load_status()`. Important internals are `gsc_work()`, `gsc_engine_supported()`, `gsc_allocate_and_map_vma()`, and `gsc_unmap_and_free_vma()`.

### Control Flow
Early init initializes `intel_uc_fw`, work item, support state, and an ordered workqueue when a GSC engine exists. Full init loads firmware metadata, allocates 4 MiB stolen memory and maps it, creates a pinned GSC engine context, initializes proxy opportunistically, and marks firmware loadable. `intel_gsc_uc_load_start()` sets `GSC_ACTION_FW_LOAD` under `gt->irq_lock` and queues work. The worker takes runtime PM, consumes action bits, uploads firmware, optionally authenticates HuC by GSC after GuC auth, runs software proxy, and marks firmware running only if proxy status reports normal.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `struct intel_gsc_uc`: firmware metadata, release/security versions, local stolen VMA and iomap, pinned context, ordered workqueue, action bits, and proxy substate. Dependencies include GSC firmware/proxy helpers, GSC engine, stolen memory, runtime PM, HuC auth, uncore FWSTS registers, and debug printing. Integration points are i915 GT/uc init, resume, FLR cleanup through firmware upload, HuC authentication, MEI proxy, and debugfs. Risks include missing GSC engine, stolen allocation failure, worker/proxy ordering deadlocks, marking firmware running before proxy is established, and teardown races with queued work. Test signals include firmware status transitions, `gsc_info`, workqueue flush behavior, HuC auth completion, and FWSTS dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.h

### Purpose
`intel_gsc_uc.h` defines the top-level GSC uC state structure and public lifecycle/status helpers.

### Important APIs, Types, And Functions
`struct intel_gsc_uc` embeds `struct intel_uc_fw`, release/security version fields, local VMA/iomap, pinned context, workqueue/work/action bits, and a proxy substructure. It declares init, fini, suspend/resume, flush, load-start, and load-status functions plus inline `is_supported`, `is_wanted`, and `is_used` helpers.

### Control Flow
The header contains inline status checks only; full lifecycle flow is implemented in `intel_gsc_uc.c`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State persists for the GT lifetime and is protected by `gt->irq_lock` for action bits and a mutex for proxy binding. Dependencies include firmware core types, VMA/context declarations, and MEI component declarations. Integration spans firmware upload, proxy, HECI submission, HuC auth, and debugfs. Risks include incorrect status interpretation and unbalanced object lifetimes. Test signals are compile coverage and consistent status transitions through supported/wanted/used helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.c

### Purpose
`intel_gsc_uc_debugfs.c` exposes GSC firmware and FWSTS status through GT debugfs.

### Important APIs, Types, And Functions
It defines `gsc_info_show()`, `DEFINE_INTEL_GT_DEBUGFS_ATTRIBUTE(gsc_info)`, and `intel_gsc_uc_debugfs_register()`.

### Control Flow
The show callback rejects unsupported GSC with `-ENODEV`, creates a `drm_printer` for the seq file, and delegates to `intel_gsc_uc_load_status()`. Registration adds a `gsc_info` debugfs file only when GSC is supported.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is just debugfs file registration with the private `intel_gsc_uc` pointer. Dependencies include DRM print, GT debugfs helpers, and GSC status printing. Integration is user-facing diagnostics. Risks are exposing unsupported devices or reading status without runtime PM, handled by the delegated printer. Test signals are presence/absence of `gsc_info` and meaningful firmware/FWSTS output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.h

### Purpose
`intel_gsc_uc_debugfs.h` declares the GSC debugfs registration helper.

### Important APIs, Types, And Functions
It forward-declares `struct intel_gsc_uc` and `struct dentry`, and declares `intel_gsc_uc_debugfs_register()`.

### Control Flow
There is no runtime flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and integrates GT debugfs setup with the implementation. Risks are limited to prototype drift. Compile coverage and `gsc_info` registration provide signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.c

### Purpose
`intel_gsc_uc_heci_cmd_submit.c` emits GSC HECI command packets through the GSC command streamer for privileged and non-privileged clients, and builds MTL GSC message headers.

### Important APIs, Types, And Functions
Exports are `intel_gsc_uc_heci_cmd_submit_packet()`, `intel_gsc_uc_heci_cmd_emit_mtl_header()`, and `intel_gsc_uc_heci_cmd_submit_nonpriv()`. Internal helpers include `struct gsc_heci_pkt`, `emit_gsc_heci_pkt()`, and `emit_gsc_heci_pkt_nonpriv()`.

### Control Flow
Privileged submission creates a request on `gsc->ce`, optionally emits an init breadcrumb, emits `GSC_HECI_CMD_PKT` with input/output GGTT addresses and sizes, flushes, submits, waits for request start and then completion, and returns `-ETIME` on timeout. Header emission fills validity marker, client ID, host session bits, version, size, and PXP single-session marking. Nonpriv submission locks batch and packet VMAs under ww context, pins the supplied context, writes a batch with HECI packet plus batch end, marks VMAs active, emits BB start and flush, waits interruptibly, and backs off on `-EDEADLK` up to ten trials.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is transient request/batch state plus caller-owned packet VMAs. Dependencies include GSC engine contexts, GEM ww locking, VMA active tracking, ring command emission, request waits, and GSC header protocol. Integration points are GSC firmware compatibility queries, proxy exchange, PXP/HDCP-style clients, and nonprivileged command submission paths. Risks include timeout semantics, request not starting due to GuC arbitration, unbalanced context pinning, ww retry exhaustion, invalid packet buffer sizes, and duplicated header declaration in the header. Test signals are successful MKHI/proxy/PXP replies, timeout logs, and nonprivileged path error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.h

### Purpose
`intel_gsc_uc_heci_cmd_submit.h` declares GSC HECI packet submission APIs and the MTL GSC message header format.

### Important APIs, Types, And Functions
It defines `GSC_HECI_REPLY_LATENCY_MS`, `struct intel_gsc_mtl_header` with validity marker, client IDs, host-session flags, message size, flags, and status, plus `struct intel_gsc_heci_non_priv_pkt`. It declares packet submission, header emission, and nonprivileged submission helpers.

### Control Flow
The header has no executable flow; it documents the fields consumed by GSC firmware and submit code.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is caller-owned packet/header memory. Integration includes GSC firmware load queries, proxy, PXP, HDCP, and nonprivileged clients. Risks are duplicated prototype declaration, message-size upper-bit reservation, host-session bit misuse, and client ID drift. Test signals are correct GSC replies for each client and clean timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_uc_heci_cmd_submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.c

### Purpose
`intel_guc.c` is the central GuC lifecycle and communication implementation. It initializes GuC submodules, configures firmware parameters, manages interrupts, sends MMIO/CT messages, handles early crash notifications, allocates GuC-addressable memory, authenticates HuC, and sanitizes/suspends GuC state.

### Important APIs, Types, And Functions
Important exports include `intel_guc_init_early()`, `intel_guc_init_late()`, `intel_guc_init_send_regs()`, `intel_guc_write_params()`, `intel_guc_init()`, `intel_guc_fini()`, `intel_guc_notify()`, `intel_guc_send_mmio()`, `intel_guc_to_host_process_recv_msg()`, `intel_guc_crash_process_msg()`, `intel_guc_auth_huc()`, `intel_guc_suspend()`, `intel_guc_resume()`, `intel_guc_allocate_vma()`, `intel_guc_allocate_and_map_vma()`, `intel_guc_self_cfg32()`, `intel_guc_self_cfg64()`, `intel_guc_load_status()`, `intel_guc_write_barrier()`, and `intel_guc_dump_time_info()`.

### Control Flow
Early init sets firmware/log/CT/submission/SLPC/RC structures, work items, locks, interrupt hooks, scratch-register base/count, notify register, and early message mask. Full init creates firmware, log, capture, ADS, CT, optional submission and SLPC structures, builds params, and marks firmware loadable. MMIO send serializes on `send_mutex`, writes request dwords into scratch regs, posts, notifies GuC, waits for GuC-origin HXG response, handles busy/retry/failure/success, and optionally copies response dwords. Suspend sends client soft reset when submission is used, then sanitizes CT and interrupts. Allocation creates lmem or shmem GEM objects, pins above the GuC WOPCM bias and below `GUC_GGTT_TOP`, and optionally maps them.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `struct intel_guc`: firmware, log, CT, SLPC, capture, ADS, submission state, interrupt hooks, send registers, params, message masks, timestamp worker, TLB lookup, and dead-GuC worker. Dependencies include GT uncore/interrupts/runtime PM, GuC ABI headers, GEM/VMA allocation, ADS/capture/submission/SLPC modules, and firmware core. Integration spans HuC auth, GuC submission, GT power management, CTB setup, debugfs status, reset/error handling, and GSC write barriers. Risks include protocol timeouts, incorrect busy/retry handling, forcewake domains, reserved GGTT ranges, repeated dead-GuC wedging, suspend cleanup with outstanding G2H, and platform workaround flags. Test signals include GuC boot status, scratch-register dumps, CT readiness, crash notification behavior, self-config KLV acceptance, and memory offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.h

### Purpose
`intel_guc.h` defines the top-level `struct intel_guc`, inline messaging helpers, status predicates, GuC GGTT validation, and public APIs used across i915 GuC firmware, submission, CT, SLPC, capture, TLB invalidation, and reset code.

### Important APIs, Types, And Functions
The central type is `struct intel_guc`, containing firmware/log/CT/SLPC/capture state, debugfs node, scheduler and stalled request state, IRQ/message state, submission ID allocators and workers, ADS pointers/sizes, LRC descriptor pool, context lookup, params, send registers, timestamp tracking, and selftest fields. Inline helpers include `intel_guc_send()`, `intel_guc_send_nb()`, `intel_guc_send_and_receive()`, `intel_guc_send_busy_loop()`, `intel_guc_to_host_event_handler()`, `intel_guc_ggtt_offset()`, status predicates, interrupt wrappers, sanitize, and message mask helpers.

### Control Flow
The header's inline send helpers route to CT send, optionally busy-looping on `-EBUSY` with sleep or `cpu_relax()` depending on context. Event handling only dispatches CT events when interrupts are enabled. `intel_guc_ggtt_offset()` asserts GuC-visible memory is above the pin bias and below `GUC_GGTT_TOP`. Sanitization resets firmware status, disables interrupts, sanitizes CT, and clears pending MMIO messages.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The structure persists for the GT lifetime and is shared by many modules with explicit spinlocks, mutexes, work structs, atomics, and xarrays. Dependencies include GuC CT/log/fwif/reg/slpc types, VMA/GEM utilities, xarray/ida, and uncore APIs. Integration is broad: submission, HuC auth, reset recovery, TLB invalidation, ADS, engine usage accounting, debugfs, and G2H processing. Risks include lock-order mistakes, stale GuC ID/context state, busy-looping in atomic contexts, invalid GGTT placement, and inconsistent firmware status predicates. Test signals include compile coverage across GuC modules, CT send behavior, sanitize/resume paths, and assertions in GGTT offset helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.c

### Purpose
`intel_guc_ads.c` constructs and maintains the GuC Additional Data Struct blob: scheduling policies, GT system info, engine usage records, MMIO save/restore regsets, golden contexts, workaround KLVs, capture lists, and private firmware data.

### Important APIs, Types, And Functions
Exports include `intel_guc_ads_create()`, `intel_guc_ads_destroy()`, `intel_guc_ads_init_late()`, `intel_guc_ads_reset()`, `intel_guc_ads_print_policy_info()`, `intel_guc_global_policies_update()`, `intel_guc_engine_usage_offset()`, and `intel_guc_engine_usage_record_map()`. Important internals include `struct __guc_ads_blob`, offset/size calculators, `guc_policies_init()`, `guc_mapping_table_init()`, `guc_mmio_reg_state_create/init()`, `guc_prep_golden_context()`, `guc_init_golden_context()`, `guc_capture_prep_lists()`, `guc_waklv_init()`, and `__guc_ads_init()`.

### Control Flow
Creation first builds temporary sorted per-engine MMIO regsets from engine registers, workaround registers, whitelist slots, MOCS, and perf counters; precomputes golden-context, capture-list, and workaround-KLV sizes; allocates a GuC VMA of the combined page-aligned blob; maps it; then initializes ADS contents. Initialization writes policies, engine masks, system info, doorbell count, golden-context pointers, engine mapping table, capture-list pointers, MMIO save/restore pointers, workaround KLV address/size, private data pointer, and flushes the map. Late init copies recorded engine default states into golden-context storage once defaults exist. Reset rebuilds ADS and clears private data.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state includes `guc->ads_vma`, `ads_map`, computed sizes, `ads_regset_count`, and temporary `ads_regset` storage. Dependencies include GuC firmware interface structs, GuC capture APIs, engine workaround/whitelist data, MCR steering, shmem golden-context reads, iosys-map, GEM lmem/shmem allocation, and platform feature masks. Integration points are GuC firmware boot params, submission watchdog reset recovery, global scheduling policy updates, engine usage accounting, capture/coredump setup, and workaround delivery. Risks include size recomputation mismatch, sorted/deduplicated register list errors, MCR steering assumptions, null capture-list fallback, page-alignment mistakes, stale golden contexts before late init, and firmware-version/platform gating for WAKLVs. Test signals include GuC boot success with ADS pointer, policy update action success, engine usage mapping correctness, capture-list population, golden-context availability after defaults, and reset-time ADS reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.h

### Purpose
`intel_guc_ads.h` declares the GuC ADS lifecycle, policy-printing, reset, and engine-usage mapping APIs.

### Important APIs, Types, And Functions
It declares create/destroy/late-init/reset helpers, `intel_guc_ads_print_policy_info()`, `intel_guc_engine_usage_record_map()`, and `intel_guc_engine_usage_offset()` for `struct intel_guc`, `struct intel_engine_cs`, and `struct drm_printer`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on iosys-map and forward declarations. It integrates GuC core, debug/status code, and engine usage accounting with ADS implementation. Risks are declaration drift or callers using engine usage maps before ADS creation. Compile coverage and GuC ADS create/reset tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.h -->
