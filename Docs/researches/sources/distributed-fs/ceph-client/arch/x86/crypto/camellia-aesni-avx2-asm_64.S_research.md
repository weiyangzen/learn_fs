# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia-aesni-avx2-asm_64.S

Purpose: Implements 32-block parallel Camellia ECB encryption/decryption and CBC decryption using AVX2 and AES-NI.

Important APIs/functions: exports `camellia_ecb_enc_32way`, `camellia_ecb_dec_32way`, and `camellia_cbc_dec_32way`. Internal functions `__camellia_enc_blk32` and `__camellia_dec_blk32` hold the core round flow. Macros provide 32-way byteslicing, AES-assisted S-box transforms, FL layers, round scheduling, and writeback.

Control flow: public functions call `vzeroupper`, load and byte-swap 32 input blocks into YMM registers, select encryption or decryption key start, use destination or stack as scratch depending on overlap, and call the core crypt helper. The helper runs base round groups, inserts FL layers, branches on `key_length` to process the larger-key rounds, unpacks lanes, and returns for writeback. CBC decrypt XORs decrypted output with previous ciphertext blocks after preserving the first decrypted block as needed.

State and persistence: uses only caller-owned `struct camellia_ctx`, destination memory, and stack scratch. No global mutable state. The use of `vzeroupper` manages architectural vector state hygiene rather than persistent data.

Dependencies and integration points: called by `camellia_aesni_avx2_glue.c`, which gates AVX2/AES-NI/OSXSAVE support and falls back to 16-way/scalar tails. Depends on exact key table offsets and on helper C key schedule behavior.

Risks: AVX2 lane ordering and output transposition are fragile. CBC decrypt has special in-place handling with a 512-byte stack allocation. Missing `vzeroupper` or incorrect FPU wrapping in callers can cause performance or state issues.

Test signals: run Camellia ECB/CBC vectors for all key sizes, exactly 32-block CBC decrypt, in-place and out-of-place decrypt, 32+16+2+1 fallback mixes, and module tests on CPUs with AVX but no AVX2.
