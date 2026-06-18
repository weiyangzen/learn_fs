<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fcrypt.c -->
# sources/distributed-fs/ceph-client/crypto/fcrypt.c

Purpose: Implements the generic `fcrypt` 64-bit block cipher used by the kernel crypto API. It is a legacy DES-like 16-round Feistel cipher with 8-byte keys where each input key byte has one parity bit ignored, leaving 56 effective bits.

Important APIs/types/functions: `struct fcrypt_ctx` stores 16 big-endian round schedules. `fcrypt_setkey()` discards parity bits and rotates the 56-bit key material by 11 bits per round. `F_ENCRYPT()` applies the round function through four fixed S-box tables. `fcrypt_encrypt()` and `fcrypt_decrypt()` unroll all rounds in opposite orders. `fcrypt_alg` registers the cipher under `fcrypt`/`fcrypt-generic` with 8-byte block and key sizes.

Control flow: Module init calls `crypto_register_alg()`. Setkey expands the caller key into `ctx->sched[]`, using a 64-bit path on 64-bit builds and a split high/low 56-bit path otherwise. Encryption copies an 8-byte block into left/right big-endian halves, alternates the Feistel macro for 16 schedules, and writes the resulting block. Decryption uses the same macro with schedules reversed.

State and persistence behavior: Persistent transform state is only the per-tfm schedule array. The S-boxes and registration object are static read-only module data. No IV, request state, filesystem state, or durable storage is involved.

Dependencies and integration points: Depends on `<crypto/algapi.h>` and the classic `crypto_alg` cipher frontend. Consumers obtain it by name through the kernel crypto API, including any filesystem or network code that still needs rxkad/AFS-compatible FCrypt behavior.

Risks: This is legacy crypto with a small block and effective 56-bit key, so new protocols should avoid it. Correctness depends on endian handling, parity-bit removal, and schedule rotation matching historical implementations. The table-driven S-box path is not constant-time with respect to secret-dependent table indices on all hardware.

Test signals: Kernel crypto manager known-answer tests for `fcrypt`, encrypt/decrypt round trips, module load/unload registration, and compatibility vectors from AFS/rxkad are the main signals. Cross-architecture tests should cover both 64-bit and non-64-bit key schedule paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/fcrypt.c -->
