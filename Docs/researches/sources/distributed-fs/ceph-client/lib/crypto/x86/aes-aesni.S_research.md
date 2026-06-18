# sources/distributed-fs/ceph-client/lib/crypto/x86/aes-aesni.S

Purpose: x86 AES-NI assembly primitives for AES-128/AES-256 key expansion and AES block encryption/decryption.

Important APIs/types/functions: exports `aes128_expandkey_aesni()`, `aes256_expandkey_aesni()`, `aes_encrypt_aesni()`, and `aes_decrypt_aesni()`. Internal macros `_prefix_sum`, `_gen_round_key`, `_aes_expandkey_aesni`, and `_aes_crypt_aesni` implement the shared logic.

Control flow: key expansion copies the raw initial round key(s), generates remaining round keys using AES-NI SubBytes via `aesenclast` plus round constants, and optionally emits equivalent inverse-cipher round keys by reversing the schedule and applying `aesimc` to interior rounds. Encryption/decryption load a block, XOR the initial key, iterate normal AES rounds with `aesenc` or `aesdec`, then apply the last-round instruction and store the block.

State and persistence: writes only caller-provided round-key and output buffers. It uses XMM registers and has i386/x86_64 calling convention branches; no global state.

Dependencies: AES-NI/SSE4.1-era instructions, `linux/linkage.h`, ABI assumptions (`-mregparm=3` on i386), and caller-side FPU context bracketing.

Integration points: called by `x86/aes.h` when CPU feature gates and FPU usability allow it; generic AES is the fallback.

Risks: assembly must match generic expanded-key layout exactly. Inverse-key pointer may be NULL and is checked. AES-192 is deliberately unsupported in the accelerated expander. Wrong round count or key schedule offsets would break all users.

Test signals: expected to be covered by AES crypto library tests and any mode tests exercising encryption/decryption; no local KUnit file in this subset.
