# sources/distributed-fs/lustre-release/lustre/ptlrpc/pack_server.c

Purpose: contains server-side byte-swapping helpers for object update request/reply formats and OUT update buffer headers.

Important APIs/types/functions: `lustre_swab_object_update()` swaps a single `object_update` and its variable parameter array. `lustre_swab_object_update_request()` swaps an `object_update_request`, optionally validates a supplied buffer length, and swaps each embedded update. `lustre_swab_object_update_reply()` swaps reply metadata, per-result lens, and fixed result fields. `lustre_swab_out_update_header()` and `lustre_swab_out_update_buffer()` are exported for OUT update transport structures.

Control flow: request swabbing first converts magic/count fields, then computes a conservative minimum size from the update count and parameter count when `len > 0`; overflow or malformed embedded update lookup returns an error before continuing. Reply swabbing computes the expected header/lens/result footprint, validates it against `len`, then iterates results and swabs each result header.

State/persistence: no retained state or persistence. The functions mutate caller-owned network buffers in place after receive or before local interpretation.

Dependencies/integration: depends on Lustre update helpers such as `object_update_request_get()`, `object_update_result_get()`, `object_update_param_size()`, LU FID swabbing, and the server-side update protocol used by target/OUT code.

Risks/test signals: size validation is intentionally minimal for variable-length parameters and must remain consistent with object update layout helpers. Tests should cover zero-length validation bypass, overflow detection, malformed update/result lookup returning `-EPROTO`, multi-update requests, multi-result replies, and exported OUT header/buffer swab behavior.
