## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ccm.c

Purpose: implements `ccm(aes)` and `rfc4309(ccm(aes))` AEAD algorithms using NX AES CCM plus AES CCA helper operations for associated-data authentication.

Important APIs and helpers: `ccm_aes_nx_set_key`, `ccm4309_aes_nx_set_key`, authsize validators, `set_msg_len`, `crypto_ccm_check_iv`, `generate_b0`, `generate_pat`, `ccm_nx_encrypt`, `ccm_nx_decrypt`, and exported descriptors `nx_ccm_aes_alg` and `nx_ccm4309_aes_alg`.

Control flow: setkey supports only AES-128 and initializes both the main CCM CPB and secondary CCA CPB. RFC4309 setkey splits a trailing 3-byte nonce from the key. `generate_pat` builds B0/B1 formatting, handles short AAD inline and long AAD through one or more CCA hcalls, and copies the resulting authentication state into the CCM CPB. Encrypt/decrypt then loop over payload chunks, maintain intermediate/continuation flags, build scatterlists after the AAD region, call hardware, carry forward output counter/MAC/S0 state, and either write the tag or compare it with constant-time `crypto_memneq`.

State and persistence: per-transform state includes key, RFC4309 nonce, temporary auth tags, and two CPBs. Per-request state includes a synthetic IV in `struct nx_ccm_rctx`. No durable state exists.

Dependencies: depends on NX core AEAD context allocation, `nx_build_sg_lists`, `nx_walk_and_build`, scatterlist copy helpers, AES/AEAD crypto APIs, and CCM/RFC4309 formatting rules.

Risks: AAD length encoding and `assoclen - 8` for RFC4309 are easy underflow points if checks regress. Only AES-128 is supported despite the generic CCM name. Long AAD chunking updates stats with `assoclen` each loop, which may overcount. Tag compare and authsize validation are security-critical. The secondary CPB and shared scatterlist area are reused under one spinlock.

Test signals: CCM and RFC4309 known-answer vectors, all accepted auth sizes, rejected auth sizes, invalid IV `L'`, zero AAD, short AAD <=14, medium and large AAD paths, encrypt/decrypt tag mismatch, chunked payloads, and underflow tests for RFC4309 associated data length.
