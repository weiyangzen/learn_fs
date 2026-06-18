<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tracepoint.c -->
# sources/distributed-fs/ceph-client/kernel/tracepoint.c

Purpose: implements the core tracepoint probe registration machinery. It manages probe arrays, static branch/static call transitions, RCU/SRCU lifetime, module tracepoint discovery, tracepoint notifiers, and syscall tracepoint work flags.

Important APIs and types: exported registration APIs are `tracepoint_probe_register_prio_may_exist()`, `tracepoint_probe_register_prio()`, `tracepoint_probe_register()`, and `tracepoint_probe_unregister()`. Iteration APIs include `for_each_kernel_tracepoint()` and module variants. `struct tp_probes` owns RCU-freed probe arrays. Transition state is tracked by `tp_transition_snapshot`.

Control flow: registration builds a new priority-ordered probe array with `func_add()`, optionally calls tracepoint regfunc, publishes it with `rcu_assign_pointer()`, updates static calls for one-probe fast paths or iterator paths, and enables the static branch. Removal builds a smaller array or stubs removed functions if allocation fails, handles transitions from one to zero or many to one, updates static calls, and releases old arrays after SRCU or Tasks Trace grace periods depending on faultability.

State and persistence: `tracepoints_mutex` protects probe updates. Module tracepoints are tracked in a local list protected by `tracepoint_module_list_mutex`. Transition snapshots preserve grace-period state across specific 1-0-1 and N-2-1 static-call transitions. Syscall tracepoint refcount toggles `SYSCALL_TRACEPOINT` work flags on all tasks.

Dependencies and integration: depends on RCU, SRCU, static keys, static calls, module notifier chains, tasklist locking, and tracepoint linker sections. Modules can register coming/going notifiers to manage probes safely.

Risks: subtle ordering bugs can call a new function with old data or free arrays too early. Module teardown requires consumers to unregister probes. Allocation failure during removal leaves stubbed functions until a later successful update. Test signals include probe priority ordering, duplicate rejection, module load/unload notifier behavior, static-call one-probe transitions, faultable tracepoints, and syscall tracepoint enable/disable across live tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/tracepoint.c -->
