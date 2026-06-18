# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-conn-helper.h

Purpose: declares the connection-to-service helper used by glusterd connection management.

Important APIs/types/functions: `glusterd_conn_get_svc_object(glusterd_conn_t *conn)` returns the owning `glusterd_svc_t *`.

Control flow: included by connection management code before creating RPC clients so the service name can be passed to RPC setup.

State and persistence behavior: no state.

Dependencies and integration points: includes `glusterd-conn-mgmt.h` and exposes a helper whose return type is `glusterd_svc_t`.

Risks and edge cases: the header assumes `glusterd_svc_t` is visible from included dependencies or caller context. Prototype drift with the implementation will break builds.

Test signals: compile all connection-management users and exercise service connection initialization.
