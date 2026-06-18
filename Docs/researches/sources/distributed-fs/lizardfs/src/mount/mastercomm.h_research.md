## sources/distributed-fs/lizardfs/src/mount/mastercomm.h

Purpose: declares the mount client's master communication API. It is the narrow public surface for metadata RPCs, chunk location/write-end RPCs, xattrs, ACLs, trash/reserved meta operations, locks, snapshots, goal management, custom packet forwarding, lifecycle initialization, and async packet handlers.

Important APIs and types: declares dozens of `uint8_t fs_*` status-returning functions plus `fs_statfs`, `fs_getmasterlocation`, `fs_getsrcip`, `fs_notify_sendremoved`, lifecycle functions, and `PacketHandler` with virtual `handle(MessageBuffer)`. It exposes overloads for legacy byte-buffer directory/trash listings and newer vector forms (`DirectoryEntry`, `NamedInodeEntry`, `ChunkTypeWithAddress`, `ChunkserverListEntry`).

Control flow and integration: callers create no object; they call global functions backed by process-wide state in `mastercomm.cc`. FUSE/client code uses these functions synchronously, while lock interruption and packet handlers support asynchronous interactions. `masterproxy` uses `fs_custom` to forward arbitrary master packets.

State and persistence: header owns no state but its API implies per-process master connection state and per-thread request matching. Returned `const uint8_t **` buffers are owned by the communication layer and should be treated as transient.

Dependencies: includes ACL, attributes, chunk address, group cache, `LizardClient`, packet, lock, directory, and named inode protocol types. This makes the header a central coupling point between mount and common/protocol code.

Risks and tests: broad C-style global API increases coupling and makes lifetime rules easy to misuse. Separate send/recv lock APIs require callers to pair calls correctly. There are no direct tests here; interface changes require broad compile and integration coverage.
