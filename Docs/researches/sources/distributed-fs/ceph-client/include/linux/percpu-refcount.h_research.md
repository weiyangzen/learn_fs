<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h

## Purpose
Defines the percpu refcount API: a scalable reference counter that uses per-CPU increments/decrements while live and switches to atomic mode for shutdown, zero detection, and release callback execution.

## Important APIs, Types, And Functions
- Mode/state bits in `percpu_count_ptr`: `__PERCPU_REF_ATOMIC`, `__PERCPU_REF_DEAD`, and `__PERCPU_REF_ATOMIC_DEAD`.
- Init flags: `PERCPU_REF_INIT_ATOMIC`, `PERCPU_REF_INIT_DEAD`, and `PERCPU_REF_ALLOW_REINIT`.
- `struct percpu_ref_data` stores atomic count, release and confirm callbacks, force/allow flags, RCU head, and backpointer.
- `struct percpu_ref` stores the tagged percpu pointer and pointer to data.
- Lifecycle APIs: `percpu_ref_init()`, `percpu_ref_exit()`, `percpu_ref_switch_to_atomic()`, `percpu_ref_switch_to_atomic_sync()`, `percpu_ref_switch_to_percpu()`, `percpu_ref_kill_and_confirm()`, `percpu_ref_kill()`, `percpu_ref_resurrect()`, `percpu_ref_reinit()`, and `percpu_ref_is_zero()`.
- Fast paths: `percpu_ref_get_many()`, `percpu_ref_get()`, `percpu_ref_tryget_many()`, `percpu_ref_tryget()`, `percpu_ref_tryget_live_rcu()`, `percpu_ref_tryget_live()`, `percpu_ref_put_many()`, `percpu_ref_put()`, and `percpu_ref_is_dying()`.

## Control Flow
Users initialize with an initial reference and a release callback. While live in percpu mode, get/put operations run inside RCU read-side sections and update per-CPU counters without checking for zero. Shutdown calls `percpu_ref_kill()` before dropping the initial reference; kill switches to atomic mode, aggregates per-CPU counts, marks dead, and then puts can detect zero and invoke release. Try-get-live can reject references after confirmed kill.

## State And Persistence
State is split between the tagged pointer in the embedded `struct percpu_ref`, allocated per-CPU counters, and `percpu_ref_data`. RCU protects switching and data lifetime. The initial reference and dead/atomic mode are part of the lifecycle protocol and must be tracked by the owner.

## Dependencies And Integration Points
Depends on atomics, percpu allocation/access, RCU, GFP allocation, and release callbacks. It integrates with high-concurrency objects such as async I/O contexts, block devices, cgroups, or kernel objects that need cheap live references and orderly two-stage teardown.

## Risks And Edge Cases
Risks include dropping the initial reference before kill, calling kill more than once without synchronization, assuming kill implies an RCU grace period, using tryget instead of tryget_live during teardown, refcount overflow beyond the documented one-bit-reduced range, force-atomic performance regressions, and use-after-exit if callers access after `percpu_ref_exit()`.

## Test Signals
Test init modes, percpu get/put under CPU migration, switch-to-atomic aggregation, kill-and-confirm ordering, release callback exactly once, resurrect/reinit paths, RCU-protected lookup patterns, CPU hotplug, and fault injection for allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu-refcount.h -->
