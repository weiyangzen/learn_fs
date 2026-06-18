# sources/distributed-fs/ceph-client/fs/smb/client/smb2proto.h

## Purpose
`smb2proto.h` is the internal declaration surface for the SMB2/SMB3 Linux CIFS client. It connects higher-level CIFS operations, transport code, PDU builders, crypto helpers, parsing helpers, and reconnect/oplock handlers.

## Important APIs, Types, And Functions
The prototypes cover error mapping, message validation and sizing, path conversion, signature verification, request setup, tcon lookup, oplock/lease handling, reparse/symlink handling, open/path metadata helpers, directory and filesystem operations, create/open/query/set/close/flush/ioctl/read/write workers, async IO, echo, reconnect, SMB3 key/AEAD allocation, compounding helpers, replay helpers, security selection, negotiate validation, response validation, preauth hashing, POSIX info parsing, and pending-delete rename handling.

The header also exposes KUnit-only error mapping hooks under `CONFIG_SMB_KUNIT_TESTS`, allowing tests to inspect SMB2 status-to-POSIX mappings.

## Control Flow
There is no runtime logic here, but the grouping documents the layering: upper CIFS VFS code calls these prototypes, `smb2pdu.c` builds command PDUs, `smb2transport.c` signs/verifies and creates MIDs, and lower transport code sends requests. Init/free pairs support compounding and async send paths.

## State And Persistence Behavior
The declared functions mutate SMB client state through `TCP_Server_Info`, `cifs_ses`, `cifs_tcon`, inode, dentry, file, search, and IO-subrequest structures. The header itself persists no state, but defines contracts for request buffers, response buffers, FIDs, replay counters, lease state, preauth hashes, and parsed POSIX metadata.

## Dependencies And Integration Points
The header includes NLS/key support and cached directory declarations, and refers to many CIFS/SMB core types. It is the integration point between authentication, transport signing, PDU construction, DFS/reparse behavior, POSIX extensions, SMBDirect-enabled IO, netfs IO completion, and filesystem stat/query code.

## Risks
Prototype drift is a practical risk: buffer ownership and response lifetime are encoded in signatures but not type-enforced. Several calls take raw pointers plus lengths, so callers must preserve implementation validation and free conventions. Replay, compounding, or init/free signature changes can ripple widely.

## Test Signals
Build coverage across CIFS feature flags, KUnit status mapping tests, compounding tests, mount/auth variants, async IO, POSIX extension mounts, and reconnect tests signal whether this declaration layer remains consistent with implementations.
