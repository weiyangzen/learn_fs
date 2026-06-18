## sources/distributed-fs/ceph-client/fs/smb/smbdirect/Makefile

Purpose: builds the common SMBDirect support module/object set when `CONFIG_SMBDIRECT` is enabled.

Important APIs and types: maps `obj-$(CONFIG_SMBDIRECT)` to `smbdirect.o` and composes it from `socket.o`, `connection.o`, `mr.o`, `rw.o`, `debug.o`, `connect.o`, `listen.o`, `accept.o`, `devices.o`, and `main.o`.

Control flow: the kernel build system links the listed objects into the smbdirect unit according to the Kconfig value. The resulting namespace/functions are consumed by server `transport_rdma.c` and likely SMB client RDMA code.

State and persistence behavior: build metadata only; no runtime state.

Dependencies and integration points: tied to `fs/smb/smbdirect/Kconfig`, Linux RDMA/SMBDirect APIs, and module namespace import by ksmbd RDMA transport.

Risks: missing an object can remove essential socket, connection, memory-registration, read/write, listener, accept, device, or module initialization code. Object ordering should keep initialization/namespace behavior compatible with the kernel build.

Test signals: `CONFIG_SMBDIRECT=m` and `=y` builds, modpost namespace checks, RDMA client/server smoke tests, and symbol availability for server `transport_rdma.c`.
