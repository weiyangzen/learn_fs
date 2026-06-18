<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user-return-notifier.c -->
# sources/distributed-fs/ceph-client/kernel/user-return-notifier.c

Purpose: implements per-CPU notifier lists for callbacks that must run when the current CPU returns to userspace.

Important APIs: `user_return_notifier_register()`, `user_return_notifier_unregister()`, and `fire_user_return_notifiers()`.

Control flow: registration sets `TIF_USER_RETURN_NOTIFY` on current and links the notifier into the current CPU's per-CPU hlist. Unregistration removes the node and clears the thread flag if the current CPU list is empty. Firing pins the current CPU with `get_cpu_var()`, iterates safely over the hlist, invokes each notifier's `on_user_return()` callback, and releases the CPU variable.

State and persistence: state is per-CPU `return_notifier_list`; notifiers are caller-owned. Thread flag state marks whether return-to-user code should call the dispatcher.

Dependencies and integration: depends on scheduler thread flags, per-CPU storage, hlist helpers, and architecture return-to-user paths.

Risks: register/unregister must be called in atomic context and unregister must occur on the same CPU. Callback list mutation during firing is handled by safe iteration, but caller-owned lifetime remains critical. Test signals include same-CPU unregister, list-empty flag clearing, multiple notifiers firing, and callbacks unregistering themselves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user-return-notifier.c -->
