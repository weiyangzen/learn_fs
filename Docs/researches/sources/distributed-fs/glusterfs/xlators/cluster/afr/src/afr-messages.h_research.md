# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-messages.h

## Purpose
Defines stable AFR log message IDs and shared message strings for structured Gluster logging.

## Important APIs, types, and functions
The `GLFS_MSGID(AFR, ...)` macro enumerates AFR message identifiers for quorum, child state, locks, split-brain, self-heal, thin arbiter, fsync, xattr, replace/add brick, and many error paths. The following `#define` string constants provide reusable text for common log messages.

## Control flow
No executable control flow is present. The file is included by AFR source files that call `gf_msg()`, `gf_smsg()`, and related logging helpers with stable message IDs.

## State and persistence behavior
Message IDs are a persistent observability contract: comments require appending new IDs and never deleting existing IDs to avoid ID reuse. Strings affect logs and downstream tooling but not filesystem state.

## Dependencies and integration points
Includes `glusterfs/glfs-message-id.h`. Integrated throughout AFR read, write, lock, open, heal, transaction, and thin-arbiter code paths.

## Risks and test signals
Risks include deleting/reordering IDs, typos in user-visible diagnostics, duplicate semantics, and callers using mismatched IDs for a failure mode. Tests are mainly compile-time plus log-oriented tests or static checks that message IDs remain append-only.
