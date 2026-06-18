# sources/distributed-fs/ceph-client/lib/once.c

## Purpose
Backs the `DO_ONCE()` and `DO_ONCE_SLEEPABLE()` helper macros by serializing one-time execution and disabling static branches after the first successful run.

## APIs, Control Flow, and State
Exports `__do_once_start()`, `__do_once_done()`, `__do_once_sleepable_start()`, and `__do_once_sleepable_done()`. Non-sleepable once uses `once_lock` with IRQ save/restore. Start locks and returns false when `*done` is already set, with sparse lock-count annotations. Done marks `*done`, unlocks, allocates deferred work, takes a module reference, and schedules work that disables the static key and releases the module. Sleepable once uses `once_mutex`; its done path disables the static branch directly after unlocking. State is the caller-provided `done` boolean plus static key state.

## Dependencies, Integration, Risks, and Tests
Depends on spinlocks, mutexes, workqueues, static keys, module references, and slab allocation. Risks include deferred allocation failure leaving the static branch enabled, module lifetime misuse if the wrong module pointer is passed, and deadlocks if callers sleep in the non-sleepable variant. Test signals include repeated macro invocation tests, module unload while deferred work is pending, sleepable/non-sleepable lockdep coverage, and static key state checks after first execution.
