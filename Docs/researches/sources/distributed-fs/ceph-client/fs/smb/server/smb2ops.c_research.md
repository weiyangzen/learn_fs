# sources/distributed-fs/ceph-client/fs/smb/server/smb2ops.c

## Purpose
Defines dialect-specific SMB2/SMB3 server value tables, operation vectors, command dispatch table, dialect initialization functions, and runtime tuners for I/O sizes and credits. It connects the generic server dispatch loop to SMB2 command handlers and SMB3 signing/encryption implementations.

## Important APIs, Types, and Functions
- `smb21_server_values`, `smb30_server_values`, `smb302_server_values`, and `smb311_server_values` define dialect strings, protocol ids, capabilities, max read/write/transaction sizes, max credits, lock flags, header sizes, read response size, create-context response sizes, and feature bits.
- `smb2_0_server_ops` provides basic SMB2 operation callbacks: command lookup, request counters, response header/status/buffer/credits, session/tree validation, and SMB2 signing.
- `smb3_0_server_ops` adds SMB3 signing key generation, encryption key generation, transform-header detection, decrypt, and encrypt callbacks.
- `smb3_11_server_ops` switches key derivation to SMB 3.1.1 functions and otherwise mirrors SMB3 encrypted operation support.
- `smb2_0_server_cmds[]` maps SMB2 command indices to handlers such as negotiate, session setup, tree connect/disconnect, logoff, create, query info, query directory, close, echo, set info, read, write, flush, cancel, lock, ioctl, oplock break, and change notify.
- Dialect init functions `init_smb2_1_server()`, `init_smb3_0_server()`, `init_smb3_02_server()`, and `init_smb3_11_server()` attach values/ops/commands to `struct ksmbd_conn`, set signing algorithm, and enable capabilities according to `server_conf.flags` and client capabilities.
- Runtime tuners `init_smb2_max_read_size()`, `init_smb2_max_write_size()`, `init_smb2_max_trans_size()`, and `init_smb2_max_credits()` update all dialect value tables.

## Control Flow
After negotiation selects a dialect, connection initialization calls the matching init function. The generic server path then uses `conn->ops` for verification, response setup, signing/encryption, session/tree lookup, credits, and request counters, and `conn->cmds` for actual command dispatch. SMB3 dialects enable encryption capability only when server policy and client capability allow it, enable leasing/directory leasing and multichannel according to global flags, and enable persistent handles for SMB 3.0.2/3.1.1 when durable handles are configured. SMB 3.1.1 initializes the connection preauth session list.

## State and Persistence
The dialect value tables are static global mutable structures. Runtime tuner functions modify the same tables for future and possibly existing connections referencing them. Per-connection selected pointers in `conn->vals`, `conn->ops`, and `conn->cmds` are not copies. No persistent storage is used.

## Dependencies and Integration Points
This file depends on auth/crypto signing and encryption functions, connection structures, SMB common/PDU constants, server global configuration, and stats counters. It is used by negotiation/common server initialization and by `server.c` request dispatch. Command handlers live primarily in `smb2pdu.c` and related modules.

## Risks and Edge Cases
- Because `conn->vals` points at shared static tables, capability bits ORed during one connection initialization can persist for later connections even when their `server_conf` or `cli_cap` differs. This is particularly sensitive for encryption, leasing, multichannel, and persistent handle capabilities.
- Runtime size/credit tuners mutate shared tables without visible locking; concurrent negotiation/request paths may observe partial changes.
- `init_smb3_0_server()` contains two encryption capability checks, one redundant with slightly different condition; policy interpretation must be tested for `ENCRYPTION` and `ENCRYPTION_OFF` flags.
- Command table holes produce `STATUS_NOT_IMPLEMENTED` in `server.c`; command indices must stay aligned with SMB2 constants and counter ordering.
- SMB 3.1.1 preauth list initialization must happen before any preauth session allocation.

## Test Signals
Negotiate each dialect and verify selected protocol id, signing algorithm, max sizes, command table, create-context sizes, and capabilities under combinations of leasing, encryption, encryption-off, multichannel, durable handle, and client encryption capability. Test runtime max read/write/trans/credit tuners before and during connections. Regression tests should verify one connection's enabled capabilities do not leak incorrectly into later connections with different policy.
