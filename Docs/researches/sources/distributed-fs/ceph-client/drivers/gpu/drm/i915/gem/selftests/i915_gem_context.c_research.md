# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_context.c

## Purpose
Provides live selftests for i915 GEM context behavior: logical context switching, parallel submission, per-context and shared-VM execution, readonly object enforcement, SSEU reconfiguration, and VM scratch isolation.

## APIs And Control Flow
Major tests are `live_nop_switch()`, `live_parallel_switch()`, `igt_ctx_exec()`, `igt_shared_ctx_exec()`, `igt_ctx_readonly()`, `igt_ctx_sseu()`, and `igt_vm_isolation()`. Helpers build huge fake objects, fill through GPU store batches, throttle outstanding requests, query RPCS registers, drive spinners, reset engines, and write/read scratch-space offsets. The live entry skips a wedged GT and dispatches the suite through `i915_live_subtests()`.

## State, Dependencies, Integration, Risks, And Tests
State lives in contexts, per-context VMs, huge GEM objects, engine power refs, requests, spinners, scratch pages, and file-private IDs. Dependencies include context/proto-context creation, VM binding, engine reset, render register commands, live-test guards, and `igt_gem_utils`. Risks are ordered fence chaining, request throttling, VM lifetime, readonly VMA enforcement, SSEU restore after reset/idle, and scratch offsets overlapping real nodes. Signals include context-switch timeouts, CPU readback mismatches, SSEU RPCS count errors, and VM-isolation leakage.
