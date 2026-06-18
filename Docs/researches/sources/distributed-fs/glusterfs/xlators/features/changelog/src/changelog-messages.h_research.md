# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-messages.h

## Purpose
Defines structured log message IDs and canonical message strings for the changelog xlator.

## APIs, Types, and Functions
Uses `GLFS_MSGID(CHANGELOG, ...)` to reserve IDs for open/rename/read/write/fsync errors, barrier state, pthread failures, HTIME operations, RPC lifecycle, cleanup, event dispatch, and snapshot logging. String macros provide reusable human-readable messages such as `CHANGELOG_MSG_HTIME_ERROR_STR`, `CHANGELOG_MSG_RPC_CONNECT_ERROR_STR`, and `CHANGELOG_MSG_BARRIER_TIMEOUT_STR`.

## Control Flow, State, and Persistence
No runtime state. The comment documents the stability rule: append new message IDs and never remove existing IDs to avoid reuse.

## Dependencies and Integration
Includes `glusterfs/glfs-message-id.h` and is included throughout the changelog xlator implementation. Library-side files use a separate `changelog-lib-messages.h`.

## Risks and Test Signals
Risks include accidental ID deletion/reordering, missing string macros for new IDs, and inconsistent structured key usage in `gf_smsg()` calls. Test signals are build-time ID generation, log-format checks, and review of appended-only message changes.
