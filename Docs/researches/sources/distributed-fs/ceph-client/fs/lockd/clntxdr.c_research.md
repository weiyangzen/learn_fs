# sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clntxdr.c` implements client-side SUNRPC XDR support for NLM versions 1 and 3 and publishes the lockd RPC program table. Version 2 is intentionally absent because it is not standardized. The source was read as a complete 614-line file.

## Important APIs, Types, and Functions

Important helpers mirror the v4 file: `nlm_compute_offsets`, `encode_cookie`, `decode_cookie`, `encode_nlm_lock`, `decode_nlm_holder`, `nlm_xdr_enc_testargs`, `nlm_xdr_enc_lockargs`, `nlm_xdr_enc_cancargs`, `nlm_xdr_enc_unlockargs`, `nlm_xdr_enc_res`, `nlm_xdr_enc_testres`, `nlm_xdr_dec_testres`, and `nlm_xdr_dec_res`. It defines version tables for versions 1 and 3 and exports `const struct rpc_program nlm_program`.

## Control Flow

Procedure entries in `nlm_procedures` route each NLM procedure to an encoder/decoder. Encoders write NFSv2-sized file handles, caller/owner netobjs, pseudo-pid, 32-bit offset and length, blocking/reclaim booleans, and state. Decoders validate cookies and status and decode a holder lock when TEST returns denied. `nlm_versions` selects v1, v3, and optionally v4.

## State and Persistence Behavior

The only owned state is static RPC procedure metadata and per-version/program statistics. Request, result, and lock data are caller-owned and transient.

## Dependencies and Integration Points

The file depends on `lockd.h`, `uapi/linux/nfs2.h`, SUNRPC XDR/client/stats APIs, and the v4 table when `CONFIG_LOCKD_V4` is enabled. `host.c` RPC client creation points at `nlm_program`, and `clntproc.c` uses the selected version's procedure array.

## Risks and Edge Cases

NLM v1/v3 use 32-bit offsets, so large ranges are clamped. Empty HPUX cookies are tolerated. Invalid status enums become XDR errors. File handles are encoded as fixed NFSv2 size, so callers must provide compatible handle data for these versions.

## Test Signals

Signals include NLM v1/v3 encode/decode round trips, NFSv2 file-handle size checks, 32-bit offset boundary tests, invalid enum/cookie fuzzing, and integration mounts that select NLM version 1 for NFSv2 and version 3/4 for later NFS clients.
