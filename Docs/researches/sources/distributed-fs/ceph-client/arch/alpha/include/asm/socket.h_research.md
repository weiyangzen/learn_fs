<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h

**Purpose:** Imports Alpha socket UAPI and fixes the nonblocking socket type flag to avoid conflict with Alpha `O_NONBLOCK` bits.

**Important APIs/types/functions:** `SOCK_NONBLOCK` set to `0x40000000`.

**Control flow:** Socket creation flag validation uses this architecture-specific value when translating userspace `SOCK_NONBLOCK` into file flags.

**State and persistence behavior:** No local state.

**Dependencies and integration points:** Depends on UAPI socket constants and generic socket code.

**Risks:** Using the generic `SOCK_NONBLOCK` value would collide with Alpha file flag bits and misinterpret socket types.

**Test signals:** Create sockets with `SOCK_NONBLOCK`, verify nonblocking behavior and no type-bit corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/socket.h -->
