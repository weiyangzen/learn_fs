<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/notifier.c -->
# sources/distributed-fs/ceph-client/kernel/notifier.c

Purpose: Implements the Linux notifier-chain core: priority-ordered callback lists for atomic, blocking, raw, and SRCU execution contexts, plus the global die notifier chain used by low-level exception paths.

Important APIs/types/functions: `notifier_chain_register()`, `notifier_chain_unregister()`, `notifier_call_chain()`, and `notifier_call_chain_robust()` are the shared internals. Exported families include `atomic_notifier_chain_register()`, `atomic_notifier_chain_unregister()`, `atomic_notifier_call_chain()`, `blocking_notifier_chain_register()`, `blocking_notifier_call_chain()`, `blocking_notifier_call_chain_robust()`, `raw_notifier_*()`, `srcu_notifier_*()`, `srcu_init_notifier_head()`, `notify_die()`, `register_die_notifier()`, and `unregister_die_notifier()`. The file relies on `struct notifier_block` and notifier head types from `<linux/notifier.h>`.

Control flow: registration walks the callback list by descending priority, rejects duplicate block pointers, optionally rejects duplicate priorities, then publishes with `rcu_assign_pointer()`. Calls dereference the head, run callbacks in order, count calls if requested, and stop when a return value contains `NOTIFY_STOP_MASK`. Robust calls first issue an up event, then replay a down event over already-called notifiers on stop/error. Atomic chains protect mutation with a spinlock and use RCU for lockless calls. Blocking chains use `rwsem`, with boot-time bypass before scheduling works. Raw chains delegate all locking to callers. SRCU chains protect mutation with a mutex and readers with SRCU.

State and persistence: notifier chains are in-memory linked lists owned by their heads. The die chain is a static `ATOMIC_NOTIFIER_HEAD(die_chain)`. Unregister waits for RCU/SRCU grace periods for atomic/SRCU heads. Tracepoints record register, unregister, and run events.

Dependencies/integration: Used by subsystems that need event fan-out without tight coupling. Integrates with RCU, SRCU, lock primitives, `CONFIG_DEBUG_NOTIFIERS`, trace events, and kdebug die handling. `notify_die()` packages `struct die_args` and dispatches through the atomic die chain in exception-sensitive paths.

Risks: Callback context rules are critical: atomic callbacks must not sleep, blocking callbacks must be process-context safe, and raw chains must be externally synchronized. Robust rollback assumes the chain does not change between passes and explicitly rules out RCU mutation. Priority uniqueness is optional, so callers depending on total ordering must choose the unique-priority APIs. Debug notifier checks only catch invalid function pointers when configured.

Test signals: Register/unregister order and duplicate handling, priority insertion, `NOTIFY_STOP_MASK` short-circuiting, robust rollback call counts, unregister while readers are active, SRCU cleanup requirements, boot-time blocking/SRCU registration paths, and `notify_die()` delivery under RCU-watching conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/notifier.c -->
