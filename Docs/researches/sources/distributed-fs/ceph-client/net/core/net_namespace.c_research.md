# sources/distributed-fs/ceph-client/net/core/net_namespace.c

## Purpose

`net_namespace.c` implements network namespace lifetime, per-namespace subsystem registration, generic pernet storage, namespace ID mapping, namespace rtnetlink operations, proc namespace operations, ownership helpers, and cleanup sequencing.

## Important APIs, Types, And Functions

Core globals include `init_net`, `net_namespace_list`, `net_rwsem`, `pernet_list`, `pernet_ops_rwsem`, and the generic ID allocator. Exported APIs include `peernet2id_alloc()`, `peernet2id()`, `peernet_has_id()`, `get_net_ns_by_id()`, `get_net_ns_by_pid()`, `get_net_ns_by_fd()`, `net_ns_get_ownership()`, `net_ns_barrier()`, `__put_net()`, `get_net_ns()`, `register_pernet_subsys()`, `unregister_pernet_subsys()`, `register_pernet_device()`, and `unregister_pernet_device()`.

Important internal functions include `net_alloc_generic()`, `net_assign_generic()`, `ops_init()`, `ops_undo_list()`, `preinit_net()`, `setup_net()`, `copy_net_ns()`, `cleanup_net()`, `unhash_nsid()`, rtnetlink handlers `rtnl_net_newid()`, `rtnl_net_getid()`, `rtnl_net_dumpid()`, and boot initializer `net_ns_init()`.

## Control Flow

Boot initialization allocates generic storage for `init_net`, preinitializes core fields, runs all registered pernet operations through `setup_net()`, adds the namespace to global lists/tree, registers netns pernet debug ops, and registers rtnetlink NSID handlers.

Creating a namespace through `copy_net_ns()` checks `CLONE_NEWNET`, charges the user namespace ucount, allocates `struct net` and generic storage, initializes namespace metadata, takes `pernet_ops_rwsem` for a consistent initializer list, and calls `setup_net()`. Failure unwinds user namespace references, ucounts, key domains, namespace common state, and passive references.

Destruction starts in `__put_net()`, which queues `cleanup_net()` on a single-thread workqueue. Cleanup removes namespaces from the global list and namespace tree, marks them dying, deletes peer nsid references from other namespaces, destroys IDRs, calls pernet `pre_exit`, `exit_rtnl`, `exit`, `exit_batch`, and generic free callbacks in reverse registration order, waits for RCU callbacks, frees deferred namespaces, drops ucounts/userns/key-domain references, and decrements passive references.

Pernet registration inserts operations either before device operations for subsystems or at the device boundary for pernet devices. Registration initializes all existing namespaces; failure undoes only those already initialized. Unregistration removes the operation and runs exit callbacks for all namespaces.

## State And Persistence Behavior

Network namespace state is in-memory and reference counted with active and passive references. `net->gen` is an RCU-managed expandable pointer array for subsystem private data. `net->netns_ids` is an IDR mapping peer namespaces to local NSIDs, protected by `nsid_lock`. Namespace membership is tracked in `net_namespace_list` under `net_rwsem` and in the namespace tree. State persists only while references exist; cleanup is asynchronous.

## Dependencies And Integration Points

The file integrates with nsproxy, proc namespace operations, rtnetlink, user namespaces and ucounts, key domains, debugfs ref tracker support, IDR, RCU, RTNL, workqueues, and every network subsystem using `struct pernet_operations`. It also provides sysfs ownership data consumed by net sysfs code.

## Risks

Ordering is critical. Pernet init/exit must be serialized against namespace creation/destruction; `pernet_ops_rwsem` and reverse unwinding enforce this. Cleanup must remove namespaces from discoverable lists before running exits to prevent new nsid references to dying namespaces. Generic storage resizing relies on RCU and never-changing assigned pointers. `copy_net_ns()` error paths are easy to leak references. Rtnetlink NSID operations must validate target and peer references while respecting namespace capability and lifetime rules.

## Test Signals

Signals include namespace create/destroy stress, module pernet register/unregister under concurrent namespace churn, NSID add/get/dump netlink tests, setns permission tests, user namespace ownership checks, refcount tracker leak checks, RCU/lockdep coverage, and fault-injection of setup failures.
