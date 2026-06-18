# sources/distributed-fs/lustre-release/lustre/ptlrpc/layout.c

## Purpose
`layout.c` is the central PTLRPC request-layout registry. It defines the `RMF_*` request message fields, the `RQF_*` request formats that combine client and server field lists, and the `req_capsule` helpers that pack, size, grow, shrink, access, swab, and dump Lustre request/reply buffers. Almost every Lustre RPC path depends on these exported symbols to agree on wire field order, variable-length field sizing, byte swapping, and reply sizing.

## Important APIs, types, and data
The local `struct req_msg_field` records field name, flags, fixed or variable size, optional swabber, optional length-aware swabber, optional dumper, and a computed per-format/per-location offset table. `enum rmf_flags` distinguishes strings, no-size-check fields, structure arrays, and minimum-size/versioned fields. `struct req_format` names an RPC format and stores field arrays for `RCL_CLIENT` and `RCL_SERVER`.

The file exports many protocol descriptors: metadata fields such as `RMF_MDT_BODY`, `RMF_REC_REINT`, `RMF_MDT_MD`, security fields such as `RMF_SELINUX_POL`, OST fields such as `RMF_OST_BODY`, `RMF_OBD_IOOBJ`, `RMF_NIOBUF_REMOTE`, llog fields such as `RMF_LLOGD_BODY` and `RMF_LLOG_LOG_HDR`, HSM/LFSCK/batch-update fields, and optional server-only update fields under `CONFIG_LUSTRE_FS_SERVER`.

The `RQF_*` objects map operation families to field lists: MGS, FLD/SEQ, MDS get/reint/HSM/batch, LDLM lock/intent, OST object and BRW operations, llog-origin operations, LFSCK, and batch update. The top-level `req_formats[]` array is the authoritative registry used by `req_layout_init()`.

Key exported helpers include `req_layout_init()`, `req_capsule_init()`, `req_capsule_set()`, `req_capsule_server_pack()`, `req_capsule_client_pack()`, `req_capsule_client_get()`, `req_capsule_server_get()`, sized/swabbed variants, `req_capsule_set_size()`, `req_capsule_msg_size()`, `req_capsule_fmt_size()`, `req_capsule_extend()`, `req_capsule_shrink()`, `req_capsule_server_grow()`, `req_check_sepol()`, `req_capsule_subreq_init()`, and `req_capsule_set_replen()`.

## Control flow
Initialization walks every registered `RQF`, assigns `rf_idx`, validates limits and array element sizing, and fills each field's offset table with one-based offsets so zero means "not present". Request construction initializes a capsule, assigns a format, sets explicit sizes for variable fields, fills missing fixed sizes with `req_capsule_filled_sizes()`, then packs either a normal PTLRPC request/reply through `lustre_pack_request()`/`lustre_pack_reply()` or a batch sub-request through `lustre_init_msg_v2()`.

Field access flows through `__req_capsule_get()`: it validates the format, resolves the field offset from the precomputed table, chooses `lustre_msg_string()` for string fields or `lustre_msg_buf()` for other fields, computes the expected length from flags and `rc_area`, validates structure-array and minimum-size constraints, then calls `swabber_dumper_helper()`. The swabber helper handles whole fields, structure arrays, and length-aware versioned fields, marks each field swabbed once, and optionally emits protocol dumps.

Format mutation is deliberately narrow. `req_capsule_set()` allows only setting the same format once initialized; `req_capsule_extend()` permits changing to a super-format after checking that existing fields are preserved or are explicitly opaque. `req_capsule_shrink()` reduces an already packed buffer and updates reply lengths. `req_capsule_server_grow()` is the complex path: it may grow in place if the reply-state buffer has enough room, or repack into a larger reply state, copy previous buffers, grow the target field, transfer "difficult reply" lock accounting, and release the old reply state. Batch sub-request growth uses the parent `RMF_BUT_REPLY` field and enforces `BUT_MAXREPSIZE`.

`req_check_sepol()` is compiled for server builds and compares an optional client `RMF_SELINUX_POL` string with the export's nodemap policy, returning `-EACCES` on mismatch. `req_capsule_set_replen()` computes the expected reply size for full requests or stores the sub-request reply size in `lm_repsize`.

## State and persistence behavior
This file does not persist data directly. Its state is process-global protocol metadata: exported `RMF_*`/`RQF_*` objects and the offset tables populated by `req_layout_init()`. Per-request state lives in `struct req_capsule` (`rc_fmt`, `rc_area`, request/reply message pointers, and location) and in associated `ptlrpc_request` fields such as `rq_reqlen`, `rq_replen`, and `rq_reply_state`. Since field offsets and formats define the on-wire protocol, changes here are compatibility-sensitive even though no on-disk store is touched.

## Dependencies and integration points
The code depends on Lustre message packing (`lustre_pack_request`, `lustre_pack_reply`, `lustre_msg_*`), byte-swapping and dumping helpers from `lustre_swab.h` and `llog_swab.h`, PTLRPC request structures from `lustre_req_layout.h`, nodemap exports for SELinux policy checks, and batch update constants like `BUT_MAXREPSIZE`. It is consumed by client/server handlers throughout MDS, MDT, OST, LDLM, LLOG, LFSCK, OSP, and batch RPC paths. `llog_client.c` and `llog_server.c` in this subset directly depend on the llog `RQF_*`/`RMF_*` definitions.

## Risks and edge cases
The main risk is wire compatibility: field order, fixed sizes, flags, swabbers, and version guards must match peers. Variable-sized fields require callers to set sizes before packing; missing `req_capsule_set_size()` on server variable replies trips assertions or yields wrong reply lengths. `RMF_F_NO_SIZE_CHECK` is necessary for interoperability in several places but weakens validation. Structure-array fields can fail if buffer lengths are not exact multiples of element sizes. `req_capsule_server_grow()` is high risk because it reallocates reply state while preserving difficult-reply locks and batch sub-request offsets. The FLD_READ comment documents an intentional little-endian/flexible-array interoperability compromise. `req_check_sepol()` depends on correct nodemap lifetime and only runs for non-subrequests.

## Test signals
Useful validation includes layout initialization assertions, build coverage for both server and non-server configs, mixed-version protocol tests around `RMF_SWAP_LAYOUTS` and guarded MGS fields, RPC pack/unpack tests for every `RQF_*` family, big-endian or forced-swab tests for fixed, array, and length-aware fields, batch RPC tests that force `RMF_BUT_REPLY` growth and `BUT_MAXREPSIZE`, MDT paths that grow `RMF_MDT_MD`, `RMF_ACL`, or `RMF_NIOBUF_INLINE`, and nodemap SELinux policy tests covering missing, matching, and mismatching policies.
