# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_workarounds.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_workarounds.c

### Purpose
`selftest_workarounds.c` is the live i915 GT workaround validation suite. It proves that hardware workaround lists and per-engine RING_NONPRIV whitelists are programmed as expected, remain valid across engine/GPU/GuC reset paths, and preserve context isolation semantics.

### Important APIs, Types, And Functions
The public entry is `intel_workarounds_live_selftests()`, which runs `live_dirty_whitelist()`, `live_reset_whitelist()`, `live_isolated_whitelist()`, `live_gpu_reset_workarounds()`, and `live_engine_reset_workarounds()`. Supporting helpers include `reference_lists_init()`, `verify_wa_lists()`, `read_nonprivs()`, `check_whitelist()`, `check_dirty_whitelist()`, `read_whitelisted_registers()`, `scrub_whitelisted_registers()`, and reset adapters for device, engine, and GuC paths. Core types include `struct wa_lists`, `struct intel_context`, `struct intel_engine_cs`, `struct i915_vma`, and `struct igt_spinner`.

### Control Flow
The tests build reference GT, engine, and context workaround lists, create temporary contexts and scratch objects, submit MI commands that read or write whitelisted registers, and compare GPU-written results with expected register offsets or write-mask behavior. Reset tests start spinner requests to force active reset handling, perform engine/GPU/GuC resets under runtime PM and the global reset lock, then verify both existing and fresh contexts. Isolation tests scrub writable whitelist registers in one context and confirm another context still reads defaults.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is transient except for GPU register/context state observed during requests. The file depends on i915 GEM internal objects, VMA pinning, ring command emission, workaround list builders, scheduler selftest policy hooks, spinner helpers, and reset APIs. It integrates with i915 live selftests and intentionally wedges or reports errors when register programming hangs or mismatches. Risks center on command buffer math, reserved/write-only/read-only register exceptions, reset timing, GuC scheduling differences, and platform-specific pardon lists. Useful signals are whitelist slot dumps, mismatch logs, reset failure messages, `igt_flush_test()`, and wedge detection.
