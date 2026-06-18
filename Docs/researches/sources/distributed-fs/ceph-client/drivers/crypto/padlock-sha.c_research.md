<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c

Purpose: provides VIA PadLock SHA1/SHA256 shash acceleration, including older one-shot/fallback-assisted flow and Nano multi-part hardware update variants.

Important APIs and functions: `padlock_sha1_init()` and `padlock_sha256_init()` seed aligned state. `padlock_sha_update()` processes full blocks through an ahash fallback using imported/exported core state and returns remaining bytes to the shash core. `padlock_sha1_finup()` and `padlock_sha256_finup()` issue `rep xsha1`/`rep xsha256` and byte-swap the digest output; they fall back when the total byte count exceeds the instruction argument range. Nano-specific update functions issue hardware block updates directly. Import/export copy aligned core state and sanitize count alignment.

Control flow: init checks `X86_FEATURE_PHE` and `PHE_EN`, skips Zhaoxin/newer family `>= 0x07` because self-tests fail, selects Nano algorithms for model `>= 0x0f`, and registers SHA1 and SHA256. Non-Nano variants allocate fallback ahash transforms in `init_tfm`; Nano variants avoid fallback for updates.

State and persistence: per-transform context stores fallback ahash for non-Nano algorithms. Per-request state is an aligned shash descriptor buffer large enough for PadLock microcode. No device-global mutable state beyond registered algorithms.

Dependencies and integration: x86 CPU feature matching, PadLock alignment, SHA core state layouts, crypto shash/ahash import/export core helpers, and inline instruction opcodes.

Risks and test signals: hardware requires 128-byte, 16-byte-aligned state; descriptor size and import sanitization prevent faults. Direct digest writes are avoided because output may be unaligned. Test SHA1/SHA256 vectors, multi-update streaming, import/export, unaligned result buffers, large message fallback, Nano and non-Nano paths, and disabled/skipped CPU-family behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c -->
