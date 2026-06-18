# sources/distributed-fs/lizardfs/src/mount/lizard_client.h

## Purpose
This header defines the public mount-side `LizardClient` API consumed by the FUSE adapters and other mount utilities. It centralizes default mount parameters, request/response value types, and the operation surface implemented in `lizard_client.cc`.

## Important APIs, Types, And Functions
`FsInitParams` captures all runtime initialization settings with defaults for master connection, retries, chunkserver timeouts, read cache, write cache, symlink cache, FUSE cache behavior, mkdir sgid handling, sugid clearing, rw-lock use, ACL cache, verbosity, and I/O limits config. `FileInfo` mirrors per-open FUSE file state. `EntryParam`, `AttrReply`, `DirEntry`, and `XattrReply` carry operation replies. `RequestException` stores both LizardFS and system error codes. Function declarations cover normal filesystem operations, special reads, read/write/flush/fsync, directory sessions, trash/reserved reads, xattrs, access, locks and interrupts, snapshots, goals, statfs, chunk queries, chunkserver listing, and init/term.

## Control Flow
No implementation flow exists, but this header defines which operations FUSE callbacks can call and which data they must pass. `FsInitParams` is filled by `main.cc` from parsed mount options and then passed to `fs_init()`.

## State And Persistence
Types in this header represent transient mount state: contexts, open file handles, replies, and initialization parameters. Persistent filesystem changes are performed by implementation functions.

## Dependencies And Integration Points
It depends on protocol types for chunkservers, locks, named inode entries, group cache/context, read cache, and stat definitions. It is the bridge between `mfs_fuse.cc`, `main.cc`, special inode/admin callers, and the client implementation.

## Risks And Test Signals
Changing this header has broad blast radius across FUSE, admin utilities, and tests. Risks include default mismatch with `mount_config.h`, bitfield assumptions in `FileInfo`, FUSE generation type differences, and status/errno mapping through `RequestException`. Compile coverage and integration tests across normal operations are key signals.
