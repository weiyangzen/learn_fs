# sources/distributed-fs/ceph-client/arch/sh/kernel/unwinder.c

Purpose: arbitrates among registered SuperH stack unwinders and provides a fault-tolerant `unwind_stack` entry point.

Important APIs and types: `struct unwinder`, `unwinder_register`, exported `unwind_stack`, default `stack_reader`, global `curr_unwinder`, sorted `unwinder_list`, `unwinder_lock`, and `unwinder_faulted`.

Control flow: registrations enqueue unwinders by rating under a spinlock, then select the current highest-rated unwinder. `unwind_stack` checks whether the active unwinder faulted; if so, it removes that unwinder from the list and downgrades to the next available implementation before calling the selected `dump` callback.

State and persistence: maintains process-wide in-kernel list state and a global fault flag. There is no disk persistence; state lasts until reboot/module lifetime.

Dependencies and integration: integrates with `asm/unwinder.h`, the architecture stack trace path, module registration, and fallback `stack_reader_dump`.

Risks: `unwinder_register` assigns `curr_unwinder = select_unwinder()`, but `select_unwinder` can return `NULL` when the current unwinder is already best; callers rely on list/rating behavior to avoid a null current unwinder. Fault downgrade permanently removes the faulting unwinder from the active list.

Test signals: stack-trace output during oops/panic, registration of alternate unwinders, and forced unwinder fault injection would validate behavior; no direct tests are present.
