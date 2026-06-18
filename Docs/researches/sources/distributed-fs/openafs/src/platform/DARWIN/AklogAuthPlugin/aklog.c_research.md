# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AklogAuthPlugin/aklog.c

Purpose: Authorization Services plugin mechanism that runs `aklog` during login so users get AFS tokens after authentication.

Important APIs and control flow: defines `PluginRef` with callbacks and `MechanismRef` with plugin, engine, and mechanism argument. `AuthorizationPluginCreate` returns `pluginInterface`. `mechanismCreate` stores the mechanism id string as an optional cell argument. `mechanismInvoke` calls `invokeAklog`. `invokeAklog` reads `kDS1AttrUniqueID` and `kDS1AttrPrimaryGroupID` from the authorization context, temporarily switches credentials with `pthread_setugid_np`, runs `do_aklog`, restores uid/gid, and sets authorization result allow. `do_aklog` uses `system("/usr/bin/aklog ...")`.

State and persistence: no persistent state. Runtime state is one mechanism instance per login mechanism invocation.

Dependencies and integration: uses Security AuthorizationPlugin APIs, DirectoryService attribute keys, syslog, `pthread_setugid_np`, and `/usr/bin/aklog`. Built as `aklog.bundle` by the Darwin Makefile/Xcode project.

Risks: `system()` with a mechanism-supplied cell string is command-injection sensitive. Fixed `/usr/bin/aklog` may not match install paths. Failure returns internal authorization errors that can affect login. The code comments note a desired future `libaklog` replacement.

Test signals: plugin load/unload, context values present/missing, uid/gid switch success/failure, default and cell-specific mechanisms, aklog failure behavior, and injection-resistant handling of mechanism arguments.
