# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/lib_sw_fence.h

Purpose: declares the selftest fence helper interface and lockdep-aware stack initialization macro.

Important APIs/types: `onstack_fence_init()` wraps `__onstack_fence_init()` with a static `lock_class_key` under `CONFIG_LOCKDEP`. `struct timed_fence` embeds an `i915_sw_fence` and `timer_list`. Public helpers are `__onstack_fence_init()`, `onstack_fence_fini()`, `timed_fence_init()`, `timed_fence_fini()`, `heap_fence_create()`, and `heap_fence_put()`.

Control flow and state: the header defines only caller-visible contracts. Stack fences are owned by the caller; timed fences own an on-stack timer; heap fences return an `i915_sw_fence *` whose allocation lifetime is managed by `heap_fence_put()` plus fence notifications.

Dependencies and integration: includes Linux timer support and i915 software fence internals. It is intended for selftest-only synchronization scenarios, not production driver paths.

Risks: callers must pair init/fini correctly and must not use a timed fence after the stack timer is destroyed. Lockdep naming is macro-based, so unusual call patterns can produce less useful diagnostics.

Test signals: compile coverage under lockdep and non-lockdep builds, plus downstream selftests that exercise delayed and heap fence dependency paths.
