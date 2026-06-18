# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.c

Purpose: provides a small container-of helper that maps a `glusterd_conn_t *` back to its owning `glusterd_svc_t`.

Important APIs/types/functions: `glusterd_conn_get_svc_object()` uses `cds_list_entry(conn, glusterd_svc_t, conn)`.

Control flow: connection initialization calls this helper to obtain the service name and object from the embedded connection field.

State and persistence behavior: no state is stored. It relies on struct embedding layout.

Dependencies and integration points: includes `glusterd-conn-mgmt.h`, `glusterd-svc-mgmt.h`, and userspace-RCU list macros. It is used by `glusterd-conn-mgmt.c`.

Risks and edge cases: passing a connection not embedded in `glusterd_svc_t` yields invalid memory. The helper is tightly coupled to `glusterd_svc_t` layout.

Test signals: initialize service connections for every daemon type and verify the derived service name/object is correct under sanitizers.
