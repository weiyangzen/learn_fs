# sources/distributed-fs/ceph-client/drivers/net/ppp/ppp_mppe.c

Purpose: Implements Microsoft Point-to-Point Encryption as a PPP CCP compressor-style module for PPTP/MPPE links. It encrypts/decrypts PPP frames and expands them rather than compressing them.

Important APIs, types, and functions: `struct ppp_mppe_state` stores ARC4 context, SHA1 digest, master/session keys, key length, MPPE bits, coherency count, stateful/stateless flags, discard/sanity state, unit/debug values, and stats. `get_new_key_from_sha()` and `mppe_rekey()` implement RFC key derivation. `mppe_alloc()`, `mppe_free()`, `mppe_init()`, `mppe_compress()`, `mppe_decompress()`, `mppe_incomp()`, and reset/stat functions implement the compressor API. Module init registers `ppp_mppe`.

Control flow: Allocation validates MPPE option/key material and rejects FIPS mode. Init parses 40/128-bit and stateful/stateless options, creates the initial session key, and initializes coherency count. TX encrypts protocols `0x0021..0x00fa`, writes PPP_COMP and MPPE overhead, rekeys every stateless packet or selected stateful packets/reset events, and returns expanded length. RX validates encrypted/flushed bits, coherency count, output size, loss state, and then decrypts with protocol-field reconstruction. Recoverable errors request CCP recovery; repeated malformed traffic can return fatal errors.

State and persistence behavior: Key material, ARC4 state, coherency count, discard mode, sanity counter, and stats persist per CCP direction. Sensitive memory is freed with `kfree_sensitive()`. State is not durable after session close or module unload.

Dependencies and integration points: Depends on crypto ARC4/SHA1 libraries, FIPS state, PPP comp/defs headers, unaligned helpers, `ppp_mppe.h`, and generic PPP compressor registration. `comp_extra = MPPE_PAD` tells generic PPP to reserve expansion space. Module alias supports `ppp-compress-CI_MPPE`.

Risks and test signals: MPPE uses legacy ARC4/SHA1 and is disabled in FIPS. Debug logs can expose keys. Generic PPP must drop frames when MPPE returns negative to avoid plaintext leakage. Stateful recovery depends on peer CCP reset behavior. Test FIPS rejection, 40/128-bit modes, stateless/stateful rekey, coherency wrap, late/lost packets, flushed recovery, too-small buffers, malformed MPPE bits, PFC and non-PFC encrypted frames, reset behavior, sensitive free, and PPTP/pppd interop.
