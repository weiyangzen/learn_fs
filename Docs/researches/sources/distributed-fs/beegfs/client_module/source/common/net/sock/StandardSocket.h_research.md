# sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.h

Purpose: Declares the concrete standard TCP/UDP socket implementation for the BeeGFS `SocketOps` abstraction.

Important APIs/types/functions: Exports construction/init/uninit, socket option setters, virtual operations, `StandardSocket_recvfrom`, `StandardSocket_recvfromT`, low-level `setsockopt`, and the `StandardSocket` struct containing `PooledSocket`, `struct socket*`, and socket domain.

Control flow: Callers construct/init, optionally tune options, then use either typed methods or the embedded `Socket` vtable.

State and persistence behavior: Tracks the kernel socket and domain for one live connection/listener. State is released by `_StandardSocket_uninit`.

Dependencies and integration points: Used by connection pools, message transport, datagram handling, and NIC probing for standard interfaces.

Risks: Consumers must not bypass initialization before vtable use, and option setters require a live kernel socket.

Test signals: Compile coverage plus option-setting and transport integration tests through the abstract socket interface.
