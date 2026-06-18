# sources/distributed-fs/ceph-client/Documentation/netlink/specs/handshake.yaml

Purpose: defines the Generic Netlink protocol used by kernel transport code to request userspace-assisted security handshakes, such as TLS handshakes.

Important APIs/types/functions: definitions include `handler-class`, `msg-type`, and `auth` enums. The `x509` nested attribute set carries certificate and private-key file descriptors or ids as signed integers. The `accept` set carries `sockfd`, handler class, message type, timeout, auth mode, repeated peer identity values, repeated X.509 certificate nests, peer name, and keyring. The `done` set carries completion `status`, `sockfd`, and repeated `remote-auth` values.

Control flow: `ready` is a notification telling handlers that a handshake request is queued. A privileged handler calls `accept` with a `handler-class` and receives the socket fd plus parameters needed to complete the handshake. After userspace finishes, it calls `done` with status, socket, and remote authentication results. This forms a queue-consume-complete protocol with fd transfer semantics implied by the socket attribute.

State and persistence: live handshake requests are queued in kernel state, and sockets move through pending, accepted, and completed states. The YAML persists only schema. Handshake results may affect kernel socket security state but not this document.

Dependencies and integration points: integrates transport-layer security consumers, userspace handshake daemons, keyrings, X.509 material, and Generic Netlink notifications. The handler class enum allows multiple handler implementations to share the family.

Risks: fd-like signed attributes require precise ownership and lifecycle handling in userspace. Timeouts and queued request ordering are not described by the schema, so daemon behavior depends on kernel implementation. Repeated peer identities/certificates/remote-auth attributes require robust multi-attribute parsing. `done` lacks `admin-perm`, so authorization relies on kernel family implementation and socket/request matching.

Test signals: exercise notification delivery, handler-class filtering, accept of queued sockets, fd lifetime on success/failure, timeout handling, multiple certificate and identity attributes, and completion status propagation.
