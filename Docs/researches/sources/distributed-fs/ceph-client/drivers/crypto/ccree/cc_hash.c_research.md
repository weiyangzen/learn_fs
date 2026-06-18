# sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_hash.c

## Purpose

`cc_hash.c` implements the ARM CryptoCell asynchronous hash and MAC provider for the Linux crypto API. It registers software-facing `ahash` algorithms backed by CryptoCell descriptors: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SM3, HMAC variants, AES-XCBC, and AES-CMAC when the detected hardware revision and standard-body capability bits permit them.

The file also owns hash-specific SRAM constants. During allocation and resume it copies digest-length constants and larval digests into CryptoCell SRAM so later request descriptors can load hash initial state without embedding all constants in every request.

## Important APIs, Types, And Functions

Key private types are `struct cc_hash_handle`, which tracks SRAM offsets and registered algorithms; `struct cc_hash_alg`, the runtime wrapper around `struct ahash_alg`; `struct cc_hash_ctx`, the per-transform DMA-backed state for digest buffers, HMAC/IPAD/OPAD material, key parameters, hash mode, and hardware mode; and `struct hash_key_req_ctx`, temporary key state for `setkey`.

Main crypto API callbacks are `cc_hash_init`, `cc_hash_update`, `cc_hash_final`, `cc_hash_finup`, `cc_hash_digest`, `cc_hash_setkey`, `cc_hash_export`, and `cc_hash_import`. MAC-specific callbacks are `cc_mac_update`, `cc_mac_final`, `cc_mac_finup`, `cc_mac_digest`, `cc_xcbc_setkey`, and `cc_cmac_setkey`. Registration is driven by `driver_hash[]`, `cc_alloc_hash_alg()`, `cc_hash_alloc()`, and `cc_hash_free()`.

Descriptor helpers include `cc_restore_hash()`, `cc_fin_hmac()`, `cc_fin_result()`, `cc_set_desc()`, `cc_setup_xcbc()`, and `cc_setup_cmac()`. SRAM helpers exported to AEAD/hash code are `cc_init_hash_sram()`, `cc_larval_digest_addr()`, and `cc_digest_len_addr()`.

## Control Flow

On driver allocation, `cc_hash_alloc()` allocates the handle, computes SRAM space based on hardware revision, reserves it with `cc_sram_alloc()`, initializes the SRAM constants through `cc_init_hash_sram()`, then registers each eligible `ahash` algorithm. HMAC-capable templates register a keyed algorithm first, then a plain hash algorithm unless the template is XCBC/CMAC-only.

For normal hashing, `cc_hash_init()` seeds request state from HMAC precomputed state or from larval digests. `cc_hash_update()` maps only block-aligned processable data through `cc_map_hash_request_update()`, restores state into hardware, processes descriptors, and writes intermediate digest and byte-count state back. `cc_hash_final()` and `cc_hash_finup()` call `cc_do_finup()`, restore state, process final data with padding, optionally run the outer HMAC pass, and write the digest result. `cc_hash_digest()` performs one-shot initialization, data processing, optional HMAC finish, and result write in one descriptor sequence.

HMAC `setkey` hashes keys larger than the block size, zero-pads shorter keys, writes the normalized key to the OPAD/IPAD workspace, and then derives and stores the inner and outer starting states. XCBC `setkey` derives K1/K2/K3 by encrypting fixed constants with the AES key. CMAC `setkey` stores the AES key directly, with special 192-bit padding to the hardware's maximum key load size.

## State And Persistence Behavior

Per-transform state lives in `cc_hash_ctx` and is DMA-mapped for the transform lifetime by `cc_alloc_ctx()` and unmapped by `cc_free_ctx()`. Per-request state lives in `struct ahash_req_ctx`, including two partial-block buffers, digest snapshots, digest byte count, MLLI metadata, and DMA addresses. Export/import serializes a magic value, digest state, byte length, and buffered partial block so hash operations can be paused and restored by the crypto API.

No filesystem state is persisted. Hardware-visible persistent state is limited to SRAM constants and descriptor-programmed engine state. Runtime suspend loses device SRAM, so `cc_pm_resume()` calls `cc_init_hash_sram()` to re-stage the constants.

## Dependencies And Integration Points

The file depends on the crypto API, `cc_request_mgr` for descriptor submission, `cc_buffer_mgr` for scatterlist and MLLI mapping, `cc_sram_mgr` for constant storage, CryptoCell descriptor setters from `cc_hw_queue_defs.h`, and hardware mode enums from the ccree driver. AEAD code also uses `cc_larval_digest_addr()` and digest length helpers for authenticated encryption hash phases.

Integration with the Linux crypto API is through `crypto_register_ahash()` and asynchronous completion callbacks. Integration with runtime PM is indirect through `cc_send_request()` and `cc_send_sync_request()`, which hold device power while descriptors are outstanding.

## Risks And Edge Cases

Descriptor sequence length is bounded by `CC_MAX_HASH_SEQ_LEN`; adding operations to setkey/final paths must preserve this limit. DMA mappings are bidirectional and cacheline-aligned; missing syncs around precomputed HMAC buffers would create stale key state. SHA-384/SHA-512 larval values require hi/lo word ordering and a larger digest length constant. `cc_larval_digest_addr()` depends on the exact SRAM copy order and on whether SM3 support is present; mismatches corrupt every later hash. Zero-length hash, HMAC with zero-length key, and MAC finalization after a full block have explicit special paths that are easy to regress.

## Test Signals

Useful signals are crypto self-tests for all registered hashes and HMAC/MACs, `tcrypt`/AF_ALG one-shot and update/final coverage, export/import tests across partial blocks, suspend/resume tests that run hashing after resume, DMA API debugging, and stress with fragmented scatterlists that force both DLLI and MLLI descriptor paths.
