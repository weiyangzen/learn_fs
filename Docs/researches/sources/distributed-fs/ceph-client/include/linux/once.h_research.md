<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once.h -->
# sources/distributed-fs/ceph-client/include/linux/once.h

## Purpose
This header provides static-key-backed helpers to run a function exactly once from fast paths, with hard-IRQ-safe and sleepable variants.

## Important APIs, types, and functions
Low-level helpers are `__do_once_start()`, `__do_once_done()`, `__do_once_sleepable_start()`, and `__do_once_sleepable_done()`. Public macros are `DO_ONCE()`, `DO_ONCE_SLEEPABLE()`, `get_random_once()`, and `get_random_sleepable_once()`.

## Control flow
Each macro instantiation creates a static done flag and a static true jump label. The first caller that wins `__do_once_*_start()` runs the supplied function, then `__do_once_*_done()` marks done and patches the static branch out of the fast path. Separate macro expansion sites are separate once instances; shared one-time behavior must be wrapped in a common helper.

## State and persistence
State is per-callsite static data in `.data..do_once`: a boolean done flag and static key. Once completed, state persists for module/kernel lifetime and the branch is optimized away.

## Dependencies and integration points
It depends on jump labels/static keys, module ownership, type-safe variadic macro calls, random byte helpers for wrappers, and concurrency primitives in implementation code.

## Risks and test signals
Risks include assuming two callsites share state, running sleepable work from the IRQ-safe variant, deadlocks because hard IRQs are blocked in the generic start path, module unload interactions, and argument side effects only on the winning call. Test concurrent callers, module unload after once completion, static-key patching, sleepable contexts, and random-once wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/once.h -->
