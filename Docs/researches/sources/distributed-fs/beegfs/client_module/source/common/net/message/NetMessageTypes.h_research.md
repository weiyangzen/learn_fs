# sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessageTypes.h

## Research
`NetMessageTypes.h` is the numeric BeeGFS protocol message registry for the client module. It defines constants for invalid, node-management, storage, session, control, monitoring, and fsck message IDs, with comments requiring synchronization with the user-space/common library. The file also conditionally includes NVFS RDMA message IDs when `BEEGFS_NVFS` is enabled.

There is no runtime control flow or state; the header is a compile-time integration contract used by every concrete message initializer and by receive-side dispatch. Dependencies are minimal, but semantic dependency on server and common library definitions is strong. Risks are severe compatibility failures if IDs are reused, renumbered, omitted, or conditionally compiled inconsistently. Because the protocol prefix includes `BEEGFS_DATA_VERSION` but message numbers remain separate, both must be considered for interoperability. Test signals are successful client-server handshakes, registration, metadata/storage requests, and dispatch tests that map wire IDs to the expected message class.
