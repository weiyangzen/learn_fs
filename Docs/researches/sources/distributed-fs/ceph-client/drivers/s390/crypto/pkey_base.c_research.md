## sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_base.c

Purpose: provides pkey module initialization, debug feature setup, and the RCU-protected protected-key handler registry. It lets independent handlers such as CCA, EP11, PCKMO, and UV plug into common pkey APIs.

Important APIs/types/functions: exports `pkey_dbf_info`, `pkey_handler_register()`, `pkey_handler_unregister()`, `pkey_handler_get_keybased()`, `pkey_handler_get_keytypebased()`, `pkey_handler_put()`, all `pkey_handler_*` invocation wrappers, and `pkey_handler_request_modules()`.

Control flow: handlers register after validation and duplicate checks under a spinlock, then `synchronize_rcu()` publishes the update. Lookup walks the RCU list, pins candidate modules with `try_module_get()`, and returns the first handler supporting a key blob or key subtype. Wrapper functions acquire a handler, call the relevant operation if present, then drop the module reference. Slowpath conversion snapshots up to ten handlers supporting slowpath conversion and tries them until one succeeds. Module init registers the debug feature and pkey misc API; CPU feature matching requires MSA.

State and persistence: persistent state is the global handler list protected by RCU and a write spinlock, plus the debug feature. Module references protect handlers while callbacks execute.

Dependencies and integration: depends on Linux module/RCU/list APIs, s390 debug, pkey API init/exit, and optional handler module names matching the Makefile.

Risks and test signals: risks include handler unregister races, module reference leaks, slowpath ten-handler cap, and missing callbacks returning `-ENODEV`. Test concurrent register/unregister with ioctl activity, handler autoload, duplicate registration, missing optional operations, and module unload after pkey use.
