# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-mgmt.h

Purpose: declares the glusterd service RPC connection abstraction and notification APIs.

Important APIs/types/functions: `glusterd_conn_t` contains `struct rpc_clnt *rpc`, a `glusterd_conn_notify_t notify` callback, and `sockpath[PATH_MAX]`. The header declares init/term/connect/disconnect, regular and mux notification trampolines, and socket filepath construction.

Control flow: service code embeds `glusterd_conn_t`, initializes it with a Unix socket and callback, then uses connect/disconnect wrappers while RPC events call the declared notify functions.

State and persistence behavior: describes volatile connection state only. Socket path strings refer to runtime filesystem sockets.

Dependencies and integration points: includes `rpc-clnt.h`; implemented by `glusterd-conn-mgmt.c`; consumed by service management modules.

Risks and edge cases: callback type only receives `conn` and event, so service-specific data must be recovered from embedding/context. Fixed `PATH_MAX` buffer requires careful path generation.

Test signals: compile service modules against the header and run lifecycle tests for each service connection.
