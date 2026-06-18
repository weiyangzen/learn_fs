# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/libglusterfs-messages.h

## Purpose
Defines the LIBGLUSTERFS component log message catalog: stable legacy message IDs, newer typed messages, and legacy string constants used by libglusterfs logging sites.

## APIs, Types, and Functions
Starts `GLFS_COMPONENT(LIBGLUSTERFS)` and lists many `GLFS_MIG()` IDs for dictionary, memory, file, graph, event, thread, inode, fd, lock, network, option, timer, and async failures. New typed `GLFS_NEW()` messages cover I/O call failure, thread priority/CPU/name errors, slow callbacks, no engine, io_uring unsupported/invalid/missing features/too small/unrecoverable enter failure, sync timeout/abort/completion, bad errno/return, file-descriptor limit failure, unlink failure, and `inet_net_pton()` failure. The trailing `LG_MSG_*_STR` constants preserve old string text for many log sites.

## Control Flow, State, and Persistence
This header generates compile-time log identifiers and inline message constructors. Message IDs are persistent operational contracts for log parsing and support tooling; string constants remain compatibility text for older `gf_msg()` style logging.

## Dependencies and Integration
Depends on `glfs-message-id.h`. Used by compatibility, dict, event, graph, inode, iobuf, gf-io, and common-utils code when emitting `LG_MSG_*`.

## Risks and Test Signals
Risks include deleting/reordering IDs, mismatch between typed messages and call sites, duplicated stale string constants, and component segment exhaustion. Test signals include compile-time ID-range checks, logging call compilation, log-format tests for typed messages, and review that new messages append rather than reuse IDs.
