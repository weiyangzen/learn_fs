# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_bulk.c

Purpose: applies GSS security services to PTLRPC bulk I/O descriptors. It signs, verifies, encrypts, decrypts, and prepares page vectors for bulk read/write paths on both client and server sides.

Important APIs/types/functions: client entry points are `gss_cli_ctx_wrap_bulk()`, `gss_cli_ctx_unwrap_bulk()`, and `gss_cli_prep_bulk()`. Server entry points are `gss_svc_prep_bulk()`, `gss_svc_unwrap_bulk()`, and `gss_svc_wrap_bulk()`. The helper `gss_prep_bulk()` allocates encryption pages with `obd_pool_get_desc_pages()` and calls `lgss_prep_bulk()`. Bulk security metadata is carried in `struct ptlrpc_bulk_sec_desc`.

Control flow: client wrap chooses the bulk security descriptor offset according to RPC service mode (`NULL`, `AUTH`, `INTG`, `PRIV`). For bulk reads with privacy it prepares receive pages; for bulk writes it either computes a MIC over `bd_vec` or allocates encrypted pages and calls `lgss_wrap_bulk()`. Client unwrap compares request and reply descriptors, handles server error flags, verifies bulk-read integrity, decrypts private bulk reads, and adjusts `bd_nob_transferred` to plaintext size. Server unwrap validates write data against the request descriptor, sets reply descriptor error flags on failures, verifies MICs or decrypts private writes. Server wrap signs or encrypts read replies and records ciphertext/plaintext sizes for the client.

State/persistence: mutates request buffers, clear buffers, reply buffers, bulk descriptor byte counts, vector lengths, encrypted vector allocation, and BSD error flags. No persistent storage.

Dependencies/integration: depends on PTLRPC flavor macros, Lustre message buffer layout, `gss_cli_ctx`, `gss_svc_reqctx`, `ptlrpc_bulk_desc`, OBD page pools, and mechanism dispatch functions in `gss_mech_switch.c`.

Risks/test signals: descriptor offsets vary by service mode, making layout regressions high risk. Integrity mode must trim final vector lengths before verification; privacy mode must preserve cleartext byte counts. Tests should cover client read/write and server read/write for null, integrity, and privacy bulk services; zero-vector bulk; server `BSD_FL_ERR`; mismatched descriptors; allocation failure; and mechanism MIC/encryption failure.
