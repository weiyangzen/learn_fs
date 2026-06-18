# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpc_module.c

Purpose: module lifecycle entry point for Lustre PTLRPC, lock management, security PTLRPC, NRS, and optional server target/nodemap support.

Important APIs/types/functions: `ptlrpc_init()` is registered with `late_initcall_sync()`, and `ptlrpc_exit()` is registered with `module_exit()`. Module metadata declares author, description, version, and GPL license.

Control flow: initialization asserts wire constants, initializes global mutexes and XID/early-message sizing, then brings up libcfs support, request layouts, high-resolution timeout support, request cache, portals, lprocfs, connection cache, pinger, LDLM, security PTLRPC, NRS, and optional target/nodemap modules. Each failure path unwinds previously initialized layers in reverse order. Exit tears down optional server modules, NRS, security, LDLM, pinger, portals, request cache, high-resolution support, connection/lprocfs, and request layouts.

State/persistence: establishes process-global kernel-module state and subsystem registrations. No durable state is written, but initialization order controls availability of all PTLRPC runtime services.

Dependencies/integration: depends on wire-test constants, `req_layout_init()`, portal/event setup, pinger, LDLM, SPTLRPC, NRS policy registration, target and nodemap modules under `CONFIG_LUSTRE_FS_SERVER`, and shared mutexes declared in `ptlrpc_internal.h`.

Risks/test signals: teardown order must mirror initialization, especially for pinger/portal/request-cache interactions and server-only modules. Tests should cover successful load/unload, injected failures at every init stage with leak-free unwinding, server and non-server builds, repeated load/unload, and verification that NRS and pinger globals are usable after startup.
