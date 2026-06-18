# sources/distributed-fs/ceph-client/include/crypto/aes.h

Purpose: common AES constants, key schedule structures, generic key preparation APIs, and architecture-specific AES entry points.

Important APIs/types/functions: AES size constants, `struct p8_aes_key`, `union aes_enckey_arch`, `union aes_invkey_arch`, `struct aes_enckey`, `struct aes_key`, legacy `struct crypto_aes_ctx`, `aes_check_keylen`, `aes_expandkey`, `aes_preparekey`, `aes_prepareenckey`, `aes_encrypt`, `aes_decrypt`, exported tables, CFB helpers, and many ARM64/PPC/SPARC64 assembly function declarations.

Control flow: callers validate or pass key length to prepare functions, which expand raw keys into encryption-only or encryption/decryption key structures. Block/mode implementations then use prepared keys for per-block or multi-block operations, optionally through arch optimized entry points.

State and persistence: prepared key structures persist round keys or arch-specific raw/optimized formats. Raw keys are caller-owned and must be zeroized by callers when sensitive.

Dependencies and integration points: depends on core crypto types and architecture Kconfig. Used by AES modes, MACs, GCM, CCM, CFB, XTS, and arch crypto implementations.

Risks: architecture-specific union layouts must remain ABI-compatible with assembly code. Encryption-only keys reduce memory/time but cannot support decryption modes. Key length validation failures must be propagated.

Test signals: AES KATs for 128/192/256-bit keys, arch/generic fallback comparison, mode tests using prepared keys, alignment tests, and key zeroization audits.
