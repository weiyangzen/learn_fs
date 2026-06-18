# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_userptr.h

Purpose: Defines VM-level and VMA-level userptr state and declares userptr APIs, with stubs when DRM GPUSVM is disabled.

Important APIs/types/functions: `struct xe_userptr_vm` stores `repin_list`, `invalidated_lock`, and `invalidated`. `struct xe_userptr` stores invalidation/repin links, `drm_gpusvm_pages`, MMU interval notifier, embedded notifier finish, TLB invalidation batch, flags for finish/TLB state, `initial_bind`, and optional injection divisor. Declares setup/remove/destroy, VM pin/check, VMA pin/check, and optional force-invalidate functions.

Control flow: VM and VMA code use the structs for invalidation-to-repin-to-rebind flow. When `CONFIG_DRM_GPUSVM` is disabled, setup and pinning return errors/no-ops so callers can compile without userptr support. Force invalidation compiles only under its injection option.

State and persistence behavior: The structs are embedded in VM/VMA objects and persist for their lifetimes. Comments document lock ownership for list manipulation, finish state, TLB batch state, and `initial_bind`.

Dependencies and integration points: Includes list/mutex/notifier/scatterlist/spinlock, DRM GPUSVM, and Xe TLB invalidation types. Consumed by VM/VMA binding, SVM, and notifier code.

Risks: The lock contract in comments is part of correctness; violating it risks list corruption, stale GPU mappings, or notifier races. Stubbed functions must match real-function semantics closely enough for disabled-GPUSVM builds.

Test signals: Compile both GPUSVM enabled/disabled configurations, run userptr bind/rebind/invalidation tests, and lockdep tests for invalidated and repin list manipulation.
