# sources/distributed-fs/ceph-client/lib/percpu-refcount.c

## Purpose
Implements scalable percpu reference counts that run as cheap per-CPU counters while live and switch to an atomic counter for shutdown, kill, and zero detection.

## APIs, Control Flow, and State
Exports init/exit, mode-switch, kill, zero-test, reinit, and resurrect helpers. State lives in `struct percpu_ref`: a flagged percpu pointer, `percpu_ref_data`, atomic global count, release callback, confirm callback, and allow/force flags. Init allocates per-CPU counters, allocates data, chooses live/atomic/dead start state, and seeds the count with `PERCPU_COUNT_BIAS` plus the initial ref. Switching to atomic sets the atomic flag, pins a ref, schedules expedited RCU, sums all per-CPU counters, subtracts the bias, warns on underflow, invokes confirmation, wakes waiters, and optionally frees percpu storage. Switching to percpu adds the bias, zeros counters on all CPUs, and clears the atomic flag with release ordering. Kill marks dead, switches atomic, and drops the initial ref.

## Dependencies, Integration, Risks, and Tests
Depends on per-CPU allocation, RCU, spinlocks, waitqueues, scheduler context, memory-ordering primitives, and `linux/percpu-refcount.h`. Risks include killing twice, exiting during a pending switch, release callbacks that sleep, missed initial-ref protocol, underflow during mode transition, and reinit without `PERCPU_REF_ALLOW_REINIT`. Test signals include percpu-ref selftests in block/memory users, RCU race tests, kill/reinit cycles, underflow warning coverage, and lockdep checks around switch wait paths.
