# sources/distributed-fs/ceph-client/fs/nfs/callback_xdr.c

## Purpose
This file is the XDR dispatch layer for the NFSv4 callback RPC program. It decodes callback COMPOUND headers and operation arguments, enforces minor-version operation rules, dispatches to callback procedure handlers, encodes operation and compound results, and defines the callback RPC service versions.

## Important APIs, types, and functions
The central dispatch path is `nfs4_callback_compound()` -> `process_op()` -> callback operation table entries. `struct callback_op` binds `decode_args`, `process_op`, `encode_res`, and response-size accounting for each supported operation. Service version objects `nfs4_callback_version1` and `nfs4_callback_version4` are exported for `callback.c`.

Decode helpers include `decode_string()`, `decode_fh()`, `decode_bitmap()`, `decode_stateid()`, `decode_layoutrecall_args()`, `decode_devicenotify_args()`, `decode_cb_sequence_args()`, `decode_recallany_args()`, `decode_notify_lock_args()`, and optional `decode_offload_args()`. Encode helpers cover compound/op headers, GETATTR attributes, and CB_SEQUENCE results.

## Control flow
The COMPOUND handler decodes tag, minor version, callback identifier, and op count. For v4.0 it resolves the client by callback ident and validates GSS principal. It writes a placeholder compound response header, then loops operations until an error or all ops are processed.

`process_op()` decodes the opcode, applies minor-version preprocessing, decodes arguments only when enough response buffer remains, calls the operation handler, writes the per-op status, and encodes operation-specific results on success. v4.1+ preprocessing requires `CB_SEQUENCE` first and rejects non-session operations before sequence. v4.2 preprocessing adds `CB_OFFLOAD` when configured.

## State and persistence behavior
The file owns per-request decode allocations for device notification arrays and referring-call lists, but persistent state changes occur in the procedure handlers. It sets request backchannel timeouts after a successful matched client and stores DRC-related status in `cb_process_state`.

## Dependencies and integration points
Dependencies include SUNRPC svc/xdr streams, NFSv4 protocol constants, backchannel transport helpers, callback procedure prototypes, NFS client lookup, and tracepoints. It integrates with `callback.c` through service version tables and with `callback_proc.c` through the operation table.

## Risks and test signals
Risks include XDR length validation mistakes, memory leaks on partial decode failure, incorrect operation legality by minor version, response buffer overflow, invalid credential handling for v4.0, and optional v4.2 table coverage. Tests should fuzz callback XDR, verify rejected illegal op sequences, exercise resource-header overflow mapping, run GSS principal acceptance/rejection, and use KASAN/KMEMLEAK around device/referring-call decode paths.
