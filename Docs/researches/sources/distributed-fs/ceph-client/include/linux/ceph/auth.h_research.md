## sources/distributed-fs/ceph-client/include/linux/ceph/auth.h

**Purpose:** This header defines the Ceph client authentication abstraction used to negotiate with monitors and create service authorizers for MDS/OSD/other peers.

**Important APIs/types/functions:** `struct ceph_authorizer` has a destroy hook. `struct ceph_auth_handshake` stores an authorizer, request/reply buffers, and optional message signing/checking callbacks. `struct ceph_auth_client_ops` is the protocol vtable for authentication status, request/reply exchange, authorizer creation/update/challenge/verification/invalidation, reset, destroy, and message signing. `struct ceph_auth_client` stores selected protocol, private implementation state, ops, negotiation flag, entity name, global ID, key, wanted keys, preferred/fallback connection modes, and mutex. Public APIs initialize/destroy/reset, build hello/auth messages, handle monitor replies, manage authorizers, process service replies, handle bad methods/authorizers, and sign/check messages.

**Control flow, state, persistence:** Authentication proceeds through monitor hello/request/reply loops; `handle_reply()` may request another round with `-EAGAIN`. Service connection setup obtains/upgrades authorizers and verifies server replies. Auth state persists in `ceph_auth_client` and protocol-private tickets/keys until reset/destroy.

**Dependencies/integration:** Depends on Ceph types, buffers, crypto keys, messages, and connection modes. Integrated by Ceph monitor/client connection code.

**Risks and test signals:** Risks include mutex violations, stale tickets, global ID changes, authorizer buffer lifetime errors, missing signature checks, and bad fallback mode handling. Test signals include Ceph auth integration tests, monitor reconnect/reauth, service challenge/reply flows, message signing verification, bad-method negotiation, and key rotation/expiry cases.
