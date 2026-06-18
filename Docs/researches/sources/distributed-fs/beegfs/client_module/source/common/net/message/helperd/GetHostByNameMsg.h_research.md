# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.h

## Research
`GetHostByNameMsg.h` declares the helper-daemon hostname lookup request. `struct GetHostByNameMsg` embeds `NetMessage` and stores `hostnameLen` plus non-owned `hostname`. Inline init sets `NETMSGTYPE_GetHostByName`, while `initFromHostname` binds a caller-provided C string and computes its length.

Control flow is construction and later payload ops in the `.c` file. State is non-owning and not persisted. Dependencies are `NetMessage.h`. Integration points are client code that asks a helper process to resolve a management or peer hostname into an address string. Risks are dangling hostname pointers, inability to carry embedded NULs, and no local validation for empty names. Test signals are correct message type and length when resolving configured hostnames and safe failure for malformed receive buffers.
