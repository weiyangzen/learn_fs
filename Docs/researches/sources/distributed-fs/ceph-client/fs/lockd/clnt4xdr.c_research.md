# sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clnt4xdr.c` implements client-side SUNRPC XDR encoding and decoding for NLM version 4. It translates internal `nlm_args` and `nlm_res` structures into the NLMv4 wire format and publishes the `rpc_version` procedure table for version 4. The source was read as a complete 582-line file.

## Important APIs, Types, and Functions

Important helpers include `nlm4_compute_offsets`, `encode_cookie`, `decode_cookie`, `encode_nlm4_lock`, `decode_nlm4_holder`, `nlm4_xdr_enc_testargs`, `nlm4_xdr_enc_lockargs`, `nlm4_xdr_enc_cancargs`, `nlm4_xdr_enc_unlockargs`, `nlm4_xdr_enc_res`, `nlm4_xdr_enc_testres`, `nlm4_xdr_dec_testres`, and `nlm4_xdr_dec_res`. The exported object is `const struct rpc_version nlm_version4`.

## Control Flow

Each RPC procedure listed in `nlm4_procedures` points at an encoder and decoder. Encoders write cookie, booleans, caller name, file handle, owner handle, pseudo pid, byte offset, byte length, reclaim flag, and state as required by the procedure. Decoders read cookies, status values, and, for denied TEST replies, a conflicting holder lock. Offset conversion maps kernel `(start,end)` locks to NLM `(offset,length)` with length zero meaning EOF.

## State and Persistence Behavior

The file owns only static procedure metadata and per-version RPC statistics counters. It does not persist lock state; encoded and decoded data live in caller-owned request/result buffers.

## Dependencies and Integration Points

It depends on `lockd.h`, NLM constants from `nlm.h`, SUNRPC XDR/client/stats helpers, and NFSv3 file-handle sizing from `uapi/linux/nfs3.h`. `clntproc.c` obtains this table through `nlm_program` when host version 4 is selected.

## Risks and Edge Cases

Offset clamping and EOF conversion must match NLMv4 semantics. Empty cookies from HPUX are normalized to a four-byte zero cookie. Invalid enum values are rejected as XDR errors. `encode_nlm4_holder` uses a read-lock/exclusive boolean that must remain consistent with protocol interpretation. Owner/caller string sizes are compile-time guarded.

## Test Signals

Use RPC encode/decode round-trip tests for TEST/LOCK/CANCEL/UNLOCK/GRANTED procedures, boundary lock ranges including EOF and overflow, invalid status enum fuzzing, empty/oversized cookie tests, and interoperability with NFSv3/NLMv4 servers.
