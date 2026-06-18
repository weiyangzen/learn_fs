# sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.h

## Purpose

This header defines the shared constants, algorithm descriptors, per-transform contexts, per-request contexts, hardware callback table, and global device-private structure for the Broadcom SPU crypto driver. `cipher.c` uses these declarations to register algorithms, construct mailbox messages, track request progress, and call SPU-M/SPU2-specific helper code.

## Important APIs, Types, and Functions

- Constants such as `MAX_SPUS`, `MAX_KEY_SIZE`, `MAX_IV_SIZE`, `MAX_DIGEST_SIZE`, `MAX_ASSOC_SIZE`, `SPU_MSG_ALIGN`, and `SPU_MB_RETRY_MAX` bound hardware instances, key/IV/digest storage, AEAD AAD size, alignment, and mailbox retry behavior.
- `enum op_type`, `enum spu_spu_type`, and `enum spu_spu_subtype` classify operation statistics and hardware generations.
- `struct iproc_alg_s` wraps a `skcipher_alg`, `ahash_alg`, or `aead_alg` with SPU cipher/auth metadata, auth ordering, and a `registered` flag.
- `struct spu_msg_buf` groups all per-request DMA/message fragments: request headers, IV/counter, digest, request padding, TX/RX status, skcipher XTS update/tweak, and AEAD GCM/AAD scratch buffers.
- `struct iproc_ctx_s` is the per-tfm state: encryption/auth keys, salt placement, IV, digest size, algorithm pointer, cipher/auth parameters, max payload, fallback AEAD, HMAC pads, cached request header, response header length, shash fallback, and RFC4543 flag.
- `struct spu_hash_export_s` is the compact exported hash state used by ahash export/import.
- `struct iproc_reqctx_s` tracks one crypto request across async mailbox callbacks, including parent request, selected context and channel, byte counters, source/destination SG cursors, AEAD assoc pointer, mailbox message, IV/counter, hash carry, incremental digest, and embedded AEAD fallback request.
- `struct spu_hw` is the hardware abstraction table. Its function pointers cover message dumping, max payload calculation, response length parsing, padding calculation, AEAD IV handling, hash type/digest sizing, request creation, cipher header init/finish, status processing, CCM IV update, and word alignment.
- `struct bcm_device_private` is the global platform state exported as `iproc_priv`.

## Control Flow

The header itself has no executable control flow, but it defines the data model used by `cipher.c`. Probe fills `bcm_device_private.spu` and mailbox fields. Crypto tfm init fills `iproc_ctx_s` from an `iproc_alg_s` entry. Request enqueue initializes `iproc_reqctx_s` cursors and counters. Hardware-specific functions in `spu_hw` are selected once based on device tree subtype and are then used by all request-building and response-parsing paths.

## State and Persistence Behavior

All structures are runtime-only. Transform state persists while a kernel crypto tfm exists and may contain key material, fallback handles, HMAC pads, salts, and cached SPU headers. Request state persists until the async mailbox operation completes. Exported hash state is intentionally small and excludes transient message buffers. Global counters and mailbox channel arrays persist for the platform device lifetime.

## Dependencies and Integration Points

The header includes Linux atomics, mailbox client and Broadcom message definitions, crypto AES/ARC4/GCM/SHA headers, internal hash/skcipher APIs, AEAD APIs, and SPU generation headers `spu.h`, `spum.h`, and `spu2.h`. It is the contract between `cipher.c`, utility code, and hardware-specific SPU message implementations.

## Risks and Edge Cases

- Fixed-size buffers must remain large enough for every algorithm registered in `cipher.c`; adding algorithms with larger keys, IVs, digests, or AAD requirements requires revisiting constants.
- `MAX_ASSOC_SIZE` caps AEAD associated data at 512 bytes in the hardware path.
- `struct spu_msg_buf` can contain sensitive material and is embedded in request contexts; debug dumps or use-after-free bugs would be security-sensitive.
- `struct spu_hw` callbacks must all be populated consistently for each hardware generation before requests can run.
- The global `extern struct bcm_device_private iproc_priv` couples all code to a single device instance.
- Hash export state size is constrained by crypto API expectations, so adding fields to `spu_hash_export_s` needs care.

## Test Signals

Compile coverage should catch missing callback declarations and structure size issues across SPU-M and SPU2 builds. Runtime tests should verify that request sizes fit buffers, AEAD AAD over 512 bytes is rejected, hash export/import restores counters and carry data, per-generation callback tables are fully populated, and debug/stat counters in `bcm_device_private` update as operations complete.
