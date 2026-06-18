<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c

Purpose: contains shared QCE register access and setup for ahash, skcipher, and AEAD requests, plus status/version helpers.

Important APIs and functions: `qce_start()` dispatches by crypto algorithm type. `qce_setup_config()` resets status and writes CE config for pipe pair, burst size, interrupt masks, and endian mode. `qce_auth_cfg()` and `qce_encr_cfg()` translate abstract QCE flags into authentication/encryption segment config bits. `qce_setup_regs_ahash()`, `qce_setup_regs_skcipher()`, and `qce_setup_regs_aead()` program keys, IVs, byte counts, sizes, starts, segment configs, and GO. `qce_check_status()` returns `-ENXIO` on hardware/error/incomplete and `-EBADMSG` on MAC failure. `qce_get_version()` decodes the hardware revision.

Control flow: each setup path first writes base config/status, writes algorithm-specific key/IV/auth state, sets segment sizes and starts, switches to little-endian BAM/result mode, and triggers GO with optional result dump. SHA preserves first/last block state and byte counts; skcipher handles XTS IV/key special layout; AEAD handles HMAC defaults, CCM nonce, tag position, and CCM counter setup.

State and persistence: no private module state; it mutates hardware registers. Request and transform context objects supply the durable software state.

Dependencies and integration: `regs-v5.h` bit definitions, QCE DMA result buffer format, SHA/skcipher/AEAD context headers, Linux crypto constants, and QCE core version/pipe selection.

Risks and test signals: endian conversions differ between SHA/skcipher and AEAD helper paths. AES-192 is accepted by some setkey code but not encoded as a hardware key size, so fallback decisions must be correct. Test register setup indirectly with vectors for every mode, XTS sector and IV behavior, SHA update/final block boundaries, AEAD tag verification, and unsupported v5.0 rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c -->
