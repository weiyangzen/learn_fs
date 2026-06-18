# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-messages.h

## Purpose

This header declares the POSIX translator's stable GLFS message IDs. These IDs are used throughout the POSIX implementation for structured logging and must be appended, not removed or reused.

## Important APIs, Types, and Functions

The file invokes `GLFS_MSGID(POSIX, ...)` with a long list of identifiers covering xattr failures, GFID handling, fd/path operations, IO failures, aio/io_uring availability, allocation/fallocate/zerofill/copy_file_range, metadata xattr operations, locks/leases, disk-space checks, initialization and option errors, and many other POSIX translator events. The newest researched identifier in the list is `P_MSG_POSIX_IO_URING`.

## Control Flow

There is no executable flow. Compile-time macro expansion creates message IDs in the POSIX component namespace. Call sites pass these IDs to `gf_msg`, `gf_msg_debug`, or related logging macros.

## State and Persistence Behavior

No runtime state or persistent data is modified. The persistent contract is semantic: message IDs must remain stable across versions so logs and tooling remain interpretable.

## Dependencies and Integration Points

It includes `glusterfs/glfs-message-id.h` and is included by POSIX implementation files. It integrates with admin/debug workflows, automated log parsing, support tooling, and test assertions that may look for specific message IDs.

## Risks

Removing, reordering for reuse, or repurposing IDs can break log compatibility. Misusing IDs at call sites can make operational triage misleading, especially where errno is significant.

## Test Signals

Compile after adding IDs, run representative POSIX failure paths, and verify structured logs show POSIX component IDs with the expected symbolic meaning.
