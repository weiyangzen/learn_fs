## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-gcm.c

Purpose: implements `gcm(aes)` and `rfc4106(gcm(aes))` AEAD algorithms using NX AES-GCM hardware plus AES-GCA/GMAC helper paths for associated data and empty payloads.

Important APIs and helpers: `gcm_aes_nx_set_key`, `gcm4106_aes_nx_set_key`, `gcm4106_aes_nx_setauthsize`, `nx_gca`, `gmac`, `gcm_empty`, `gcm_aes_nx_crypt`, RFC4106 wrappers, and exported descriptors `nx_gcm_aes_alg` and `nx_gcm4106_aes_alg`.

Control flow: setkey initializes main GCM and secondary GCA CPBs for all AES key sizes; RFC4106 stores a trailing 4-byte nonce. Requests synthesize the 16-byte GCM IV, initialize counter word 1, process empty-message cases through `gcm_empty` or `gmac`, process AAD through `nx_gca`, then loop over payload chunks with `nx_build_sg_lists` and `nx_hcall_sync`. Each chunk carries forward counter, GHASH pattern, and S0 state. Encrypt writes the tag to destination; decrypt reads the input tag and compares it with `crypto_memneq`.

State and persistence: per-transform state includes key, RFC4106 nonce, secondary CPB, and temporary tag storage. Per-request state is `struct nx_gcm_rctx` with the mutable IV/counter. No persistent storage exists.

Dependencies: AES/GCM crypto helpers, scatterwalk copy helpers, NX core hcall and scatterlist functions, CPB mode definitions, and algorithm registration in `nx.o`.

Risks: RFC4106 requires at least 8 bytes of associated data; the wrapper checks this before subtracting. Empty payload handling temporarily switches CPB mode to ECB/GMAC and must restore it and scrub the ECB key overlay. AAD chunk stats appear to add the full assoclen per chunk, which can overcount. Tag handling, IV construction, authsize constraints, and state carry-forward across chunks are security-sensitive.

Test signals: GCM/RFC4106 known-answer vectors for all AES key sizes, auth sizes 8/12/16 for RFC4106, zero payload with and without AAD, long AAD chunking, tag mismatch, nonce extraction, invalid short RFC4106 AAD, scatterlist offsets, and multi-chunk counter continuation.
