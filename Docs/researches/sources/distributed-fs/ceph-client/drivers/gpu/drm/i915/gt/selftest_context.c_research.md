# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_context.c

Purpose: provides live i915 selftests for GPU context size accounting, active context lifetime, idle barriers, and remote context activity tracking.

Important APIs/functions: entry point `intel_context_live_selftests()` runs `live_context_size`, `live_active_context`, and `live_remote_context`. Helpers include `request_sync()`, `context_sync()`, `__live_context_size()`, `__live_active_context()`, `__remote_sync()`, and `__live_remote_context()`.

Control flow: `request_sync()` manually commits and queues a request while retaining timeline lock context, then waits and retires it. `live_context_size()` iterates engines, hides default state, extends `engine->context_size` by one page, poisons a redzone at the end of the context state object, submits a request, forces a context switch with a kernel request, and checks that hardware did not write into the redzone. `live_active_context()` disables heartbeat, submits repeated requests on a context, verifies the context remains active after request completion until idle barriers run, flushes barriers, waits for kernel context synchronization, and confirms the engine parks. `live_remote_context()` verifies that `intel_context_prepare_remote_request()` remote fences do not clobber idle-barrier activity tracking.

State and persistence behavior: tests create temporary contexts, map context state objects, alter heartbeat intervals, temporarily modify `engine->default_state`, and use `ce->active` as the persistence signal for lifetime protection. All changes are restored or released on exit paths.

Dependencies and integration points: depends on `intel_engine_heartbeat`, `intel_engine_pm`, GT live subtest harness, request/timeline locking, mock context helpers, and `igt_flush_test()`. GuC submission paths skip idle-barrier assumptions because GuC signals safe unpin differently.

Risks: these tests intentionally perturb engine context size and heartbeat settings; cleanup must run even on errors. Redzone checks overlap execlists debugging behavior and assume mapped context state is coherent enough for CPU inspection. Short waits can be sensitive to very slow or wedged hardware.

Test signals: failures report redzone corruption, missing active context barriers, engines staying awake after idle barriers, or remote context activity becoming idle too early. The entry point skips work when the GT is wedged.
