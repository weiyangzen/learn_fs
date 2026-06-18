# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-pmap.h

Purpose: Defines the glusterd portmap registry data structures and helper prototypes. It is the internal contract for code that allocates, registers, searches, and removes brick port mappings.

Important APIs and types: `struct pmap_ports` holds one registry entry: list node, brick name string, RPC transport pointer, and port. `struct pmap_registry` holds the list head plus configured base/max port range. Declared helpers include `pmap_port_alloc()`, `pmap_registry_get()`, `pmap_add_port_to_list()`, `pmap_port_new()`, `pmap_port_remove()`, `pmap_registry_search()`, `port_brick_bind()`, `pmap_registry_search_by_xprt()`, and `pmap_assign_port()`.

Control flow: The header has no executable flow. Its declarations support port allocation before brick start, brick sign-in binding, and sign-out cleanup.

State and persistence: The structs describe in-memory state only. Registry contents are rebuilt through runtime brick registration and are not persisted to the volume store by this module.

Dependencies and integration points: Depends on URCU list definitions, Gluster xlator types, UUID compatibility, and `gf_boolean_t`. It is used by glusterd pmap RPC code and any brick lifecycle code that needs to assign or remove ports.

Risks: Exposing raw structs and list nodes means callers can mutate registry internals without synchronization if they bypass the intended helpers. The `void *xprt` transport field is untyped and lifetime-sensitive.

Test signals: Compile-time compatibility with `glusterd-pmap.c`, brick start/stop port allocation, multiplexed brick registration, and transport-based cleanup verify the header.
