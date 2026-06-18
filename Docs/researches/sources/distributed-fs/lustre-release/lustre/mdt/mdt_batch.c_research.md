# sources/distributed-fs/lustre-release/lustre/mdt/mdt_batch.c

## Purpose

`mdt_batch.c` implements the MDT-side handler for Lustre batch metadata update RPCs, currently with a very narrow supported operation set. The registered top-level MDT handler is `mdt_batch(struct tgt_session_info *tsi)`, wired from the normal MDT target handler table as `MDS_BATCH`. It parses a `BUT_HEADER_MAGIC` batch update request, optionally receives large request buffers through PTLRPC bulk GET, creates a batched reply capsule, iterates embedded Lustre messages, and dispatches each subrequest through a local `struct tgt_handler` table.

The only concrete batch suboperation in this file is `BUT_GETATTR`, implemented as an LDLM enqueue/getattr-style lock operation through `ldlm_handle_enqueue()`. The file is therefore a batch framing and dispatch layer more than a metadata mutation engine.

## Important APIs, Types, And Functions

`mdt_batch()` is the exported entry point. It uses `struct but_update_header`, `struct but_update_buffer`, `struct batch_update_request`, and `struct batch_update_reply` request/reply formats, together with `req_capsule` subrequest machinery.

`mdt_batch_unpack()` extracts opcode-specific fields from the subrequest capsule. For `BUT_GETATTR`, it fetches `RMF_DLM_REQ` into `info->mti_dlm_req`; any other opcode returns `-EOPNOTSUPP`.

`mdt_batch_getattr()` is the concrete handler. It passes the MDT export namespace, subrequest capsule, DLM request, and MDT LDLM callback suite (`ldlm_server_completion_ast`, `tgt_blocking_ast`, `ldlm_server_glimpse_ast`) to `ldlm_handle_enqueue()`.

`mdt_batch_handler_find()` maps `BUT_FIRST_OPC <= opc < BUT_LAST_OPC` onto `mdt_batch_handlers[]` and asserts that the table entry opcode matches the request opcode. The handler macro `TGT_BUT_HDL()` initializes `struct tgt_handler` with `HAS_KEY | HAS_REPLY`, `LUSTRE_MDS_VERSION`, and an `RQF_<opcode>` capsule format.

`mdt_batch_reconstruct()` is a replay/reconstruction hook for mutable batched subrequests. The current handler table has only read-only `BUT_GETATTR`, so the reconstructor array is structurally present but not exercised by the current operation set.

## Control Flow

`mdt_batch()` first validates that the client capsule has an MDT batch header, checks the magic, and rejects zero update-buffer counts. It allocates an array of update buffer pointers sized by `buh_count`.

The request payload arrives either inline or by bulk transfer. If `buh_inline_length > 0`, the first update buffer points directly into `buh_inline_data`. Otherwise the server reads an array of `but_update_buffer` descriptors from `RMF_BUT_BUF`, estimates a page-fragment count, prepares a bulk sink descriptor on `MDS_BULK_PORTAL`, allocates one large buffer per update descriptor, wires those buffers into the bulk descriptor, prepares secure bulk state with `sptlrpc_svc_prep_bulk()`, and receives the payload with `target_bulk_io()`.

After payload acquisition, the function sizes `RMF_BUT_REPLY` from `buh_reply_size`, packs the server reply capsule, initializes `batch_update_reply`, switches the MDT thread/session into batch mode (`mti_batch_env`, `mti_pill`, `tsi_batch_env`), allocates `tg_reply_data`, and checks whether the RPC is resent.

The nested loop walks each `batch_update_request` buffer and every embedded Lustre message inside it using `batch_update_reqmsg_next()` and `batch_update_repmsg_next()`. For each submessage it validates message magic, finds a handler, initializes a subrequest capsule over the embedded request/reply message pair, unpacks opcode-specific fields, optionally reconstructs already committed mutable subrequests on resent RPCs, and otherwise invokes `h->th_act(tsi)`. If the reply capsule grows and changes `pill->rc_repmsg`, the code reloads the current reply message pointer before calculating packed reply length.

On success, the function records each subreply result, resets per-subrequest MDT thread state, tracks the packed reply length, and shrinks the reply field if the client-provided reply allocation was larger than needed. Exit cleanup sets the reply count, frees bulk buffers, frees the `tg_reply_data`, frees the PTLRPC bulk descriptor, finalizes MDT thread info, and sets `tsi_reply_fail_id` to the batch update network-reply fail injection ID.

## State And Persistence Behavior

This file does not create durable metadata state directly. Its state is request scoped: allocated payload buffers, capsule state, `mti_batch_env`, `tsi_batch_env`, `tsi_batch_idx`, and the batched reply count. Durable behavior is delegated to subhandlers; in the current file the concrete subhandler enters the LDLM server path rather than updating persistent MDT objects.

Resend/replay awareness is present through `tgt_check_resent()` and `tg_reply_data.lrd_batch_idx`. For mutable future handlers, `mdt_batch()` would reconstruct replies for subrequests already covered by the last reply data and re-execute uncommitted or read-only subrequests. Because `BUT_GETATTR` is not flagged `IS_MUTABLE`, it is re-executed on resent RPCs.

## Dependencies And Integration Points

The file depends on Lustre PTLRPC request capsules, bulk I/O, LDLM server callbacks, target handler dispatch, and MDT per-thread state from `mdt_internal.h`. It integrates with `mdt_handler.c` via the `MDS_BATCH` operation and with the batch wire formats and helpers that provide `BUT_*`, `RMF_BUT_*`, `batch_update_reqmsg_next()`, and `batch_update_repmsg_next()`.

The DLM callback suite makes the batch getattr path participate in normal server-side LDLM completion, blocking, and glimpse handling. Error reporting follows Lustre target conventions using `RETURN`, `GOTO`, `err_serious()`, `CERROR`, and `DEBUG_REQ`.

## Risks And Edge Cases

Payload trust boundaries are important. The function validates top-level header presence, magic, nonzero buffer count, bulk buffer sizes below `OUT_MAXREQSIZE`, embedded message magic, and opcode support, but correctness also depends on the batch-format iterators respecting the declared buffer bounds. Tests should stress malformed `burq_count`, truncated embedded messages, reply-size underestimation, and mismatched `buh_update_count`.

The inline path only assigns `update_bufs[0]` from `buh_inline_data`; any inline request with `buh_count > 1` relies on the encoded inline payload being traversed from that first buffer or would expose invalid uninitialized update-buffer pointers. That is a format contract worth verifying at the wire-format layer.

The check `handled_update_count > buh->buh_update_count` happens before processing the next subrequest. Boundary behavior for exactly equal counts should be tested because a malformed request may try to produce more subreplies than advertised.

Bulk page-count accumulation and reply packed-length accumulation use integer-sized locals; very large counts are mostly constrained by request formats and allocation failures, but fuzzing should include overflow-shaped descriptors.

## Test Signals

Useful tests include valid one-op `BUT_GETATTR` batches, unsupported opcodes, zero-count headers, bad magic, malformed bulk descriptors, bulk receive failures, too-small and too-large reply buffers, resent read-only batches, and fail injection around `OBD_FAIL_BUT_UPDATE_NET_REP`. Integration tests should confirm LDLM enqueue semantics are identical when issued through a batch versus the non-batch path and that all allocated bulk buffers and descriptors are released on every error exit.
