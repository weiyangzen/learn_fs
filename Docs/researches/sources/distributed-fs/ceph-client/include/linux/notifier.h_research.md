
# sources/distributed-fs/ceph-client/include/linux/notifier.h

Purpose: defines the generic Linux notifier-chain API used by subsystems to publish status changes to registered callbacks without hard-coded call lists. It covers atomic, blocking, raw, and SRCU-protected chains.

Important APIs/types/functions: `struct notifier_block` carries the callback, next pointer, and priority. `struct atomic_notifier_head`, `blocking_notifier_head`, `raw_notifier_head`, and `srcu_notifier_head` encode the locking model. Initialization macros create static or dynamic heads. Register/unregister functions add and remove callbacks, call-chain functions dispatch events, robust call-chain variants roll back with a second event, and `notifier_from_errno()` / `notifier_to_errno()` map errno values to notifier return codes. `NOTIFY_DONE`, `NOTIFY_OK`, `NOTIFY_STOP`, and `NOTIFY_BAD` define callback semantics.

Control flow: a subsystem initializes a head, modules register `notifier_block` entries ordered by priority, and the owner calls the relevant `*_notifier_call_chain()` when an event occurs. Dispatch stops when a callback returns a value with `NOTIFY_STOP_MASK`. Atomic chains use a spinlock and are callable in atomic context; blocking chains use an rwsem; SRCU chains make calls cheap and unregisters expensive; raw chains require caller-provided serialization.

State and persistence: state is in-memory list membership and head locking state only. It persists for the lifetime of the head or registered module and must be torn down before callback code or backing objects disappear.

Dependencies and integration points: depends on errno, mutexes, rwsems, SRCU, spinlocks, and RCU annotations. Integration points include CPU, netdevice, reboot, suspend, VT keyboard, netlink release, NVMEM, and many other subsystem event streams.

Risks and test signals: risks include unregistering from inside a running chain, blocking inside atomic callbacks, missing SRCU cleanup, priority collisions when unique-priority registration is required, and callback lifetime races during module unload. Test signals include lockdep coverage for context misuse, notifier ordering tests, stop/errno conversion tests, robust rollback tests, and build coverage for `CONFIG_TREE_SRCU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/notifier.h -->
