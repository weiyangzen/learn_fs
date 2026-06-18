# subset-b-001223 grouped research

Work item: `subset-b-001223`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.c

Purpose: implements the CryptoCell AEAD algorithms exposed to the Linux crypto API. It handles authenticated encryption modes built from HMAC-SHA1/SHA256 or AES-XCBC with CBC/CTR ciphers, plus native CCM/GCM variants and IPsec RFC modes. The file translates `aead_request` operations into CryptoCell hardware descriptor sequences and registers matching `struct aead_alg` instances during driver initialization.

Important APIs, types, and functions: internal state is split between `struct cc_aead_handle`, which owns the AEAD algorithm list and SRAM workspace, `struct cc_aead_ctx`, which stores per-transform key material, auth mode, cipher mode, nonce, DMA addresses, and auth tag size, and `struct aead_req_ctx` from `cc_aead.h`, which stores per-request DMA and MLLI state. Public entry points are `cc_aead_alloc()` and `cc_aead_free()`. Crypto API callbacks include `cc_aead_init()`, `cc_aead_exit()`, `cc_aead_setkey()`, `cc_des3_aead_setkey()`, RFC-specific setkey functions, authsize validators, and encrypt/decrypt entry points. Descriptor builders include `hmac_setkey()`, `xcbc_setkey()`, `cc_hmac_authenc()`, `cc_xcbc_authenc()`, `cc_ccm()`, `cc_gcm()`, and lower-level helpers for association, cipher, digest, GHASH, GCTR, CCM, and IV setup.

Control flow: allocation reserves an AEAD SRAM workspace, filters `aead_algs[]` by hardware revision and standards body, creates `cc_crypto_alg` wrappers, and registers each `aead_alg`. A transform initialization copies template modes into `cc_aead_ctx`, sets DMA-aware request size, allocates coherent encryption-key storage, and allocates HMAC or XCBC helper buffers when needed. Setkey parses authenc keys or RFC nonces, validates cipher/auth key sizes, copies encryption keys into DMA memory, prepares HMAC padded keys or XCBC derived keys through synchronous hardware descriptor sequences, and stores reduced key length where RFC nonce bytes are stripped. Encrypt/decrypt callbacks zero the request context, save the original IV pointer, set request association length, perform RFC IV transformations when needed, then call `cc_proc_aead()`.

Request processing validates mode-specific data sizes and single-pass eligibility, prepares CTR/CCM/GCM IV and metadata buffers, calls `cc_map_aead_request()`, optionally copies MLLI tables into SRAM, emits descriptor sequences based on auth mode, and submits them with `cc_send_request()`. Completion calls `cc_unmap_aead_request()`, restores the original IV, compares computed and received MACs on decrypt, zeroes decrypted output on authentication failure, handles fragmented encryption ICV copy-back, and completes the original `aead_request`.

State and persistence behavior: transform state persists allocated DMA key buffers, HMAC/IPAD/OPAD buffers, XCBC keys, cipher/auth modes, nonce bytes, and selected auth size until `cc_aead_exit()`. Per-request state persists only until completion and includes DMA mappings for MAC, IV, CCM/GCM config, MLLI metadata, source/destination scatterlists, and tag backup. The hardware SRAM workspace is owned by the AEAD handle for the driver lifetime. No filesystem persistence is involved.

Dependencies and integration points: this file depends on Linux crypto AEAD/authenc/GCM helpers, DES/AES constants, `cc_buffer_mgr` for mapping and unmapping requests, `cc_request_mgr` for synchronous and asynchronous hardware submission, `cc_hash` for hash larval/digest SRAM addresses, `cc_sram_mgr` for workspace allocation, and `cc_driver` for `cc_drvdata`, hardware revision, descriptor flags, and device lookup. It integrates with `cc_driver.c` through `cc_aead_alloc()`/`cc_aead_free()` and with the request manager through `struct cc_crypto_req`.

Risks: AEAD correctness is highly sensitive to scatterlist offsets, fragmented ICV handling, and restore of the caller IV pointer after transformed RFC IVs. Decrypt must not reveal plaintext on tag failure; this code zeros the destination when CPU MAC comparison fails, but that depends on correct `icv_virt_addr` selection by the buffer manager. Single-pass versus double-pass decisions depend on alignment and plaintext-authenticate-only cases. Descriptor sequence length must remain below `MAX_AEAD_PROCESS_SEQ`; adding modes or descriptors without updating the cap risks stack overwrite. Key handling is security-sensitive because authenc parsing, nonce stripping, DES weak-key checks, and DMA synchronization must match crypto API expectations.

Test signals: useful tests include Linux crypto manager self-tests for all registered AEAD names, IPsec RFC4106/RFC4309/RFC4543 vectors, GCM/CCM tag sizes, decrypt authentication failure with output zeroing, in-place and non-in-place requests, fragmented tag scatterlists, unaligned AAD and CTR payload fallback to double-pass, zero-length payloads, and hardware-revision filtering of algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h

Purpose: declares the AEAD request contract and constants shared by AEAD processing and buffer mapping. It defines tag, CCM, and GCM layout constants and exposes driver-level AEAD allocation and teardown.

Important APIs, types, and functions: the central type is `struct aead_req_ctx`, the per-request private context allocated by `crypto_aead_set_reqsize_dma()`. It contains cacheline-aligned MAC, CTR IV, GCM IV variants, GHASH key, GCM length block, CCM configuration block, DMA addresses for those buffers, original IV backup, association length, source/destination MLLI state, scatterlist pointers, offsets, buffer type selections, auth size, cipher mode, and flags for fragmented ICV, single-pass flow, and RFC4543 plaintext-authenticate-only behavior. Externally visible functions are `cc_aead_alloc()` and `cc_aead_free()`.

Control flow: this header does not execute logic, but its layout drives `cc_aead.c` and `cc_buffer_mgr.c`. AEAD callbacks zero this structure at request start, fill mode-specific fields before mapping, let the buffer manager populate DMA/MLLI fields, and then consume those fields while building descriptors and completing requests.

State and persistence behavior: `struct aead_req_ctx` is transient per crypto request, but it holds pointers and DMA addresses that must be valid until request completion. Cacheline alignment on key buffers and MAC/config blocks is part of the DMA coherency contract. `backup_iv` preserves caller-visible request state across internal IV rewrites, and `backup_mac` temporarily preserves authentication tags where coherent in-place decrypt could overwrite source data.

Dependencies and integration points: the header depends on kernel crypto AEAD APIs, AES/CTR constants, `cc_driver.h` through downstream users, and `cc_buffer_mgr.h` types such as `cc_mlli`, `mlli_params`, and `cc_req_dma_buf_type`. It is included by both AEAD implementation and buffer manager, making it a shared ABI inside the driver.

Risks: field layout and alignment affect DMA safety. Adding per-request fields without updating request-size setup in `cc_aead_init()` would corrupt adjacent crypto API memory. Misinterpreting `assoclen`, `cryptlen`, `req_authsize`, or `is_icv_fragmented` can cause tag comparison against the wrong bytes. The enum `aead_ccm_header_size` uses sentinel `-1`; code must consistently distinguish no-CCM from zero-length CCM AAD header.

Test signals: tests should exercise all flags represented here: CCM with and without AAD, GCM and RFC GCM IV handling, fragmented ICV, in-place decrypt on coherent platforms, single-pass and double-pass flows, zero-length payload, and request-size sanity under KASAN or crypto self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.c

Purpose: centralizes DMA mapping, scatterlist analysis, MLLI table generation, and unmapping for skcipher, AEAD, and hash requests. It converts Linux scatterlists and request-local buffers into CryptoCell DLLI or MLLI descriptors and maintains enough metadata for the cipher, AEAD, and hash descriptor builders to address data correctly.

Important APIs, types, and functions: `struct buffer_array` is the internal staging model for one or more buffers that will become a shared MLLI table. Core helpers include `cc_get_sgl_nents()`, `cc_copy_sg_portion()`, `cc_render_buff_to_mlli()`, `cc_render_sg_to_mlli()`, `cc_generate_mlli()`, `cc_add_sg_entry()`, and `cc_map_sg()`. Exported mapping APIs are `cc_map_cipher_request()`, `cc_unmap_cipher_request()`, `cc_map_aead_request()`, `cc_unmap_aead_request()`, `cc_map_hash_request_final()`, `cc_map_hash_request_update()`, and `cc_unmap_hash_request()`. Initialization and teardown create/destroy the `mlli_buffs_pool`.

Control flow: skcipher mapping starts with IV DMA mapping, maps source and optionally destination scatterlists, chooses DLLI for single mapped entries or MLLI for multi-entry data, builds MLLI tables when needed, and records input/output MLLI counts. AEAD mapping first backs up in-place decrypt MACs on coherent platforms, calculates crypt length excluding decrypt tags, maps internal MAC and CCM/GCM buffers, maps the source scatterlist, then chains association data, IV, and payload in different orders for single-pass and double-pass flows. `cc_aead_chain_data()` finds the scatterlist entry where payload starts after AAD, maps destination if needed, chooses DLLI versus MLLI, and prepares ICV address/backup state. Hash mapping handles current-buffer residue, update block alignment, final-update composition, and optional MLLI table generation.

State and persistence behavior: DMA mappings persist from map until the matching unmap call in request completion or error cleanup. MLLI tables are allocated from `drvdata->mlli_buffs_pool`, copied later into CryptoCell SRAM by descriptor sequences, and freed in unmap paths. Request contexts hold mapped entry counts, offsets, DMA addresses, and buffer-type enums. Hash contexts also persist residue buffers across update/final calls through alternating buffer indexes.

Dependencies and integration points: depends on Linux DMA, scatterlist, scatterwalk, dmapool, and crypto request APIs. It includes `cc_cipher.h`, `cc_hash.h`, and `cc_aead.h` to populate their request contexts. It integrates with `cc_driver` through `cc_drvdata`, device lookup, coherent-DMA flag, and MLLI SRAM base address. The descriptor builders in `cc_cipher.c`, `cc_aead.c`, and `cc_hash.c` consume the selected DLLI/MLLI metadata.

Risks: this file is a high-risk boundary because off-by-one scatterlist lengths, wrong DMA direction, stale mapped counts, or incorrect tag offsets can cause data corruption, authentication bypass/failure, or DMA API misuse. `cc_copy_sg_portion()` uses `end - to_skip + 1`; callers must supply compatible inclusive offsets. AEAD in-place decrypt with coherent DMA has special MAC backup/copy-back behavior that can regress silently. Error paths must not unmap buffers that were never mapped, and MLLI generation must respect `MAX_NUM_OF_TOTAL_MLLI_ENTRIES`.

Test signals: run crypto tests with multi-fragment scatterlists, AAD split across SG entries, payload start in a later SG entry, fragmented and contiguous ICV, in-place and out-of-place AEAD, hash updates with sub-block residues, zero-length cipher/hash/AEAD data, forced DMA mapping failures if available, and DMA API debug enabled to detect unbalanced maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h

Purpose: declares the buffer-manager interface used by the CryptoCell cipher, AEAD, and hash front ends. It provides common enum/type definitions for DLLI/MLLI selection and scatterlist copy direction.

Important APIs, types, and functions: `enum cc_req_dma_buf_type` distinguishes no buffer, direct-linked DMA (`CC_DMA_BUF_DLLI`), and MLLI table (`CC_DMA_BUF_MLLI`). `enum cc_sg_cpy_direct` controls copy direction for `cc_copy_sg_portion()`. `struct cc_mlli` stores SRAM address, mapped scatterlist counts, original SG entries, and MLLI entries. `struct mlli_params` stores the DMA pool, virtual address, DMA address, and byte length of an allocated MLLI table. Declared APIs cover initialization, cipher map/unmap, AEAD map/unmap, hash update/final map/unmap, and scatterlist portion copying.

Control flow: consumers call the map function before emitting hardware descriptors, inspect request-context fields populated by the implementation, submit descriptors, and then call the matching unmap from completion/error paths. The init function must run before algorithm registration can process requests because cipher/AEAD/hash mapping can allocate from `drvdata->mlli_buffs_pool`.

State and persistence behavior: the header describes transient per-request state rather than persistent storage. `mlli_params` values are valid only while a request mapping is live; `cc_mlli.sram_addr` points to driver SRAM assigned elsewhere and is meaningful after the MLLI table has been copied to SRAM.

Dependencies and integration points: includes Linux crypto alg APIs and `cc_driver.h`. It is used by `cc_cipher.c`, `cc_aead.c`, `cc_hash.c`, and any future request type that needs common DMA/MLLI handling.

Risks: the buffer-type enum is part of an implicit contract with descriptor builders; if a builder assumes DLLI while the mapper produced MLLI, hardware reads the wrong address form. `cc_mlli` has both mapped and logical counts, and mixing them can cause invalid DMA unmaps or descriptor lengths. API callers must pair every successful map with the exact matching unmap.

Test signals: compile coverage for all users, DMA API debug, request paths that exercise each enum value, and failure-injection around MLLI pool allocation and scatterlist mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_buffer_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.c

Purpose: implements CryptoCell skcipher algorithms for AES, DES/3DES, SM4, XTS, ESSIV, protected AES/SM4 keys, and policy-protected CPP keys. It registers Linux crypto `skcipher_alg` instances and turns `skcipher_request` operations into hardware descriptor sequences.

Important APIs, types, and functions: internal transform state lives in `struct cc_cipher_ctx`, which stores mode, flow mode, key type, user-key DMA buffer, protected-key slot metadata, ESSIV hash and fallback transforms, and fallback status. Key token support uses `struct cc_hkey_info` from the header plus private `cc_hw_key_info` and `cc_cpp_key_info`. Public driver entry points are `cc_cipher_alloc()` and `cc_cipher_free()`. Crypto API callbacks are `cc_cipher_init()`, `cc_cipher_exit()`, `cc_cipher_setkey()`, `cc_cipher_sethkey()`, `cc_cipher_encrypt()`, and `cc_cipher_decrypt()`. Descriptor helpers include `cc_setup_state_desc()`, `cc_setup_key_desc()`, `cc_setup_xex_state_desc()`, `cc_setup_flow_desc()`, `cc_setup_readiv_desc()`, and `cc_setup_mlli_desc()`.

Control flow: allocation filters `skcipher_algs[]` by hardware revision, standards body, and security-disabled state, creates wrappers, and registers each algorithm. Transform init copies mode metadata from the wrapper, allocates ESSIV software hash and fallback when applicable, sets request size, allocates a key buffer, and maps it for DMA. Setkey validates key size and mode constraints, handles DES weak-key and XTS key validation, hashes ESSIV secondary keys in software, and syncs user-key DMA memory for hardware. Protected-key setkey parses `cc_hkey_info`, validates HW or CPP slot ranges, enforces protected-key mode restrictions, and records key type/slot instead of copying raw keys.

Request flow starts in encrypt/decrypt, which zeroes `struct cipher_req_ctx` and calls `cc_cipher_process()`. Processing validates data size and zero-length requests, delegates to fallback for unsupported ESSIV key sizes, copies the IV into DMAable memory, fills CPP metadata when needed, maps IV/data through the buffer manager, emits state, MLLI-copy, key, XEX, data-flow, and read-IV descriptors, then submits asynchronously. Completion unmaps DMA, copies the updated IV back to the request IV, frees the copied IV, and completes the skcipher request.

State and persistence behavior: per-transform key state persists until `cc_cipher_exit()`, including mapped key DMA memory, protected-key slot metadata, ESSIV hash/fallback transforms, and mode selection. Per-request state persists mapped IV/data and MLLI table pointers until completion. CPP requests carry slot/algorithm metadata in `struct cc_crypto_req` for request-manager handling. No persistent storage is written.

Dependencies and integration points: depends on Linux crypto skcipher/DES/XTS/SM4/shash helpers, `cc_buffer_mgr` for DMA mapping, `cc_request_mgr` for hardware submission, and `cc_driver` for hardware flags and algorithm priority. It integrates with `cc_driver.c` through allocation/free and shares `cc_crypto_alg`/`cc_alg_template` with AEAD registration patterns.

Risks: key-size validation is mode-specific and protects against hardware misuse; changes must preserve XTS/ESSIV double-key rules and protected-key restrictions. ESSIV fallback behavior depends on request-size layout and copying the request object into request context. IV handling is sensitive because hardware writes next IV into the DMA copy and completion copies it back. MLLI output offsets must match buffer-manager counts. Security-disabled filtering must prevent protected-key algorithms from registering when unavailable.

Test signals: crypto manager skcipher tests for each registered algorithm, XTS and ESSIV vectors, DES weak-key rejection, SM4 OSCCA-only filtering, protected-key token validation, CPP CBC/CTR behavior on 713 hardware, fallback ESSIV non-256-bit keys, in-place and out-of-place scatterlists, MLLI multi-fragment data, zero-length requests, and IV update semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h

Purpose: declares skcipher request state, allocation APIs, and protected-key token layout for the CryptoCell cipher front end.

Important APIs, types, and functions: `struct cipher_req_ctx` stores per-request generic async context, selected DMA buffer type, input/output SG and MLLI counts, copied IV pointer, and MLLI allocation parameters. `struct cc_hkey_info` is the packed protected-key token passed through setkey, carrying real key length and two hardware key slots. `CC_HW_KEY_SIZE` exposes the token length for algorithm templates. Public functions are `cc_cipher_alloc()` and `cc_cipher_free()`.

Control flow: `cc_cipher.c` declares `sizeof(struct cipher_req_ctx)` as the base request size and appends fallback request space for ESSIV where needed. The buffer manager fills DMA and MLLI fields after mapping, descriptor builders consume them, and completion frees any live request resources.

State and persistence behavior: `cipher_req_ctx` is transient for one request. Its `iv` pointer references a DMAable copy of caller IV, not caller memory. `mlli_params` is live only between mapping and unmapping. `cc_hkey_info` is caller-provided key metadata and is copied into private context by protected-key setkey.

Dependencies and integration points: includes `cc_driver.h` and `cc_buffer_mgr.h`, binding cipher request state to common async context and buffer mapping types. Used by `cc_cipher.c` and `cc_buffer_mgr.c`.

Risks: packed key token layout is externally visible to users of protected-key algorithms; changing it would break setkey callers. Request-size accounting must include this structure or buffer-manager writes will corrupt memory. Input/output nent fields are easy to confuse with MLLI nents and mapped nents.

Test signals: compile-time structure use, protected-key setkey with valid/invalid token lengths, MLLI and DLLI skcipher requests, ESSIV fallback request-size tests, and DMA debug for map/unmap balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h

Purpose: provides shared CryptoCell algorithm constants and enum values for block sizes, key sizes, digest sizes, engine identifiers, crypto algorithms, directions, cipher modes, and hash modes. It is the common vocabulary used by descriptor builders and request contexts.

Important APIs, types, and functions: defines DES/AES key and IV sizes, SHA/MD5 digest and block sizes, maximum hash/HMAC buffer sizes, CPP slot/algorithm constants, `enum drv_engine_type`, `enum drv_crypto_alg`, `enum drv_crypto_direction`, `enum drv_cipher_mode`, `enum drv_hash_mode`, and `enum drv_hash_hw_mode`. There are no functions.

Control flow: this header has no runtime flow, but its enum values are passed into descriptor macros such as `set_cipher_mode()`, `set_cipher_config0()`, and flow setup throughout AEAD, cipher, and hash code. It also informs request validation such as block alignment and key size checks.

State and persistence behavior: no mutable state. The constants define compile-time sizes for DMA buffers and runtime comparisons. Changing values affects hardware programming semantics across the driver.

Dependencies and integration points: includes Linux integer types. Used by `cc_driver.h`, AEAD/cipher/hash implementations, debugfs, and hardware descriptor definitions. It bridges Linux crypto API concepts to CryptoCell hardware mode encodings.

Risks: enum numeric values must match CryptoCell hardware expectations. Reordering or renumbering modes would silently program descriptors incorrectly. Maximum-size constants determine allocated DMA buffer sizes; undersizing can corrupt memory, while oversizing may mismatch hardware transfer lengths.

Test signals: broad crypto self-tests across all algorithms, descriptor dump inspection for mode values, compile coverage for new algorithms, and hardware bring-up tests on 630/710/712/713 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_crypto_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c

Purpose: exposes selected CryptoCell registers and the DMA coherency flag through debugfs for diagnostics. It creates a global `ccree` debugfs directory and per-device subdirectories.

Important APIs, types, and functions: `CC_DEBUG_REG()` maps register names to offsets. Static register sets include `ver_sig_regs`, `pid_cid_regs`, and `debug_regs`. Public functions are `cc_debugfs_global_init()`, `cc_debugfs_global_fini()`, `cc_debugfs_init()`, and `cc_debugfs_fini()`.

Control flow: module init calls global init to create `/sys/kernel/debug/ccree`. Device initialization calls `cc_debugfs_init()`, which allocates debugfs regset structures with devm memory, creates a per-platform-device directory, exposes a `regs` regset and `coherent` bool, then exposes either legacy signature/version registers or PID/CID registers depending on hardware revision. Teardown removes the per-device directory recursively, and module exit removes the global directory.

State and persistence behavior: `cc_debugfs_dir` is a global dentry pointer for module lifetime. Each `cc_drvdata` stores its per-device debugfs directory in `drvdata->dir`. Files are runtime-only debugfs entries and do not persist across unload or reboot.

Dependencies and integration points: depends on Linux debugfs, register-offset macros from `cc_host_regs` via `cc_driver.h`, and hardware revision/offset fields initialized in `cc_driver.c`. `cc_driver.c` owns call ordering around probe/remove and module init/exit.

Risks: debugfs register exposure is read-only but can still leak hardware state useful for diagnostics or attackers with debugfs access. The global `ver_sig_regs` offsets are mutable and shared, so multiple devices with different revisions could conflict. Failure to allocate the version regset is intentionally non-fatal, so missing debugfs version data should not be treated as probe failure.

Test signals: mount debugfs and verify per-device `regs`, `version`, and `coherent` files appear; test both <=712 and >712 register layouts; unload/reload the module and check cleanup; boot with `CONFIG_DEBUG_FS=n` to verify stub behavior from the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h

Purpose: provides the debugfs interface contract with compile-time stubs when debugfs is disabled.

Important APIs, types, and functions: declares `cc_debugfs_global_init()`, `cc_debugfs_global_fini()`, `cc_debugfs_init()`, and `cc_debugfs_fini()` under `CONFIG_DEBUG_FS`. The non-debugfs path provides no-op inline functions and a successful `cc_debugfs_init()` stub.

Control flow: driver module init/remove can call these functions unconditionally. If debugfs is disabled, calls compile to no-ops and device probe continues normally.

State and persistence behavior: no state in this header. Runtime state is owned by `cc_debugfs.c` only when debugfs is compiled in.

Dependencies and integration points: relies on forward visibility of `struct cc_drvdata` from includers, and is included by `cc_driver.c`. It isolates the platform driver from `#ifdef CONFIG_DEBUG_FS` call-site clutter.

Risks: stubs make debugfs absence silent, so tests that depend on debugfs must check kernel config. Header guard comment names `__CC_SYSFS_H__`, which is cosmetic but can confuse maintainers.

Test signals: build with `CONFIG_DEBUG_FS=y` and `n`, verify probe succeeds in both cases, and confirm debugfs cleanup paths are not referenced when compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.c

Purpose: is the platform-driver core for ARM CryptoCell REE hardware. It matches device-tree compatibles, maps registers, initializes clocks, PM, interrupts, hardware configuration, SRAM/request/buffer managers, crypto algorithms, debugfs, and FIPS integration, then tears those resources down on remove.

Important APIs, types, and functions: hardware identity is described by `struct cc_hw_data` and `arm_ccree_dev_of_match[]`. Module parameters are `dump_desc`, `dump_bytes`, and `sec_disable`. Key functions are `init_cc_cache_params()`, `cc_read_idr()`, `__dump_byte_array()`, `cc_isr()`, `cc_wait_for_reset_completion()`, `init_cc_regs()`, `init_cc_resources()`, `fini_cc_regs()`, `cleanup_cc_resources()`, `cc_get_default_hash_len()`, `ccree_probe()`, `ccree_remove()`, `ccree_init()`, and `ccree_exit()`.

Control flow: module init creates the global debugfs root and registers the platform driver. Probe calls `init_cc_resources()`, which allocates `cc_drvdata`, records matched hardware revision and standards body, maps MMIO, gets IRQ and optional clock, sets DMA mask, enables runtime PM and clock, validates hardware signature/PID/CID, checks 703 slim mode and security-disabled state, requests the ISR, computes cache/ACE parameters, initializes registers, debugfs, FIPS, SRAM, MLLI SRAM, request manager, buffer manager, hash algorithms, skcipher algorithms, and AEAD algorithms. On successful initialization it reports REE FIPS OK and drops runtime PM usage. Error labels unwind in reverse order. Remove frees AEAD, cipher, hash, buffer manager, request manager, FIPS, debugfs, registers, runtime PM, and clock.

Interrupt flow: `cc_isr()` ignores interrupts while runtime-suspended, reads/clears HOST_IRR, stores interrupt bits in `drvdata->irq`, masks completion interrupts and calls `complete_request()`, masks/schedules FIPS handling for GPR0 when enabled, logs AXI errors, and rate-limits unknown bits. `init_cc_regs()` clears pending interrupts, unmasks completion/AXI/FIPS causes, and writes cache/ACE settings.

State and persistence behavior: `cc_drvdata` is the persistent per-device state for mapped registers, IRQ source, completion, platform device, MLLI SRAM address, DMA pool, registered algorithms, subsystem handles, SRAM cursor, debugfs dentry, clock, coherency flag, hardware revision/name, offsets, standards body, security-disabled state, completion mask, and cache parameters. State lasts from probe to remove. Module parameters persist while loaded and affect debug dumping and secure-function registration.

Dependencies and integration points: depends on platform device, OF matching, runtime PM, clk, IRQ, DMA, debugfs, FIPS, SRAM manager, request manager, buffer manager, hash, cipher, AEAD, and PM callbacks. It is the integration root for the files in this work item and for adjacent `cc_hash`, `cc_request_mgr`, `cc_sram_mgr`, and `cc_pm`.

Risks: resource unwinding must stay exactly reverse-ordered; incorrect labels can leak IRQ/clock/PM state or leave registered crypto algorithms after partial failure. Hardware ID checks gate access to register layouts; mistakes can write wrong offsets. Security-disabled and slim-mode handling controls whether protected algorithms register. Interrupt masking/unmasking interacts with request completion and FIPS tasklets, so missed unmasking can stall the queue. Runtime PM suspended checks can hide shared IRQ events.

Test signals: platform probe/remove on all supported compatibles, invalid signature/PID/CID failure paths, runtime suspend/resume with active crypto, IRQ completion and AXI error handling, `sec_disable=1` filtering, 703 slim mode algorithm set, debugfs creation, FIPS enabled and disabled boots, and fault injection at each init step to verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h

Purpose: defines the main CryptoCell driver interface, hardware revision constants, interrupt masks, algorithm wrapper types, per-device state, generic request metadata, and register/DMA helper functions shared across the driver.

Important APIs, types, and functions: defines `DRV_MODULE_VERSION`, `enum cc_hw_rev`, `enum cc_std_body`, DMA and interrupt masks, register macro `CC_REG()`, queue sizing constants, `struct cc_cpp_req`, `struct cc_crypto_req`, `struct cc_drvdata`, `struct cc_crypto_alg`, `struct cc_alg_template`, and `struct async_gen_req_ctx`. Helpers include `drvdata_to_dev()`, `dump_byte_array()`, `cc_iowrite()`, `cc_ioread()`, `cc_gfp_flags()`, and `set_queue_last_ind()`. Declared driver functions include reset wait, register init/fini, byte dumping, and default hash-length query.

Control flow: this header has no top-level runtime flow, but it shapes every request path. Algorithm registration wraps Linux crypto algorithms in `cc_crypto_alg`; request paths fill `cc_crypto_req` before calling the request manager; DMA code uses `cc_gfp_flags()` to match request sleepability; descriptor builders call `set_queue_last_ind()` conditionally for newer hardware.

State and persistence behavior: `cc_drvdata` is persistent from probe to remove and is the owner/locator for all subsystem handles. `cc_crypto_req` is transient per request and carries callback, callback argument, optional synchronous completion, and CPP metadata. `async_gen_req_ctx` is embedded in cipher/AEAD/hash request contexts to retain IV DMA and operation direction.

Dependencies and integration points: includes Linux interrupt/workqueue, DMA, platform device, clock, crypto API headers, register definitions, crypto constants, hardware queue descriptor definitions, and SRAM manager declarations. It is included by nearly every C file in the ccree driver.

Risks: constants in this header control hardware programming and queue limits. Changing `MAX_MLLI_BUFF_SIZE`, interrupt masks, or DMA mask can break multiple subsystems. `struct cc_drvdata` field lifetime assumptions are shared widely; adding fields requires careful probe/remove initialization. `set_queue_last_ind()` is revision-gated and descriptor completion behavior may change if used incorrectly.

Test signals: full driver build, probe/remove, algorithm registration, DMA mask validation, descriptor completion on 630/710/712/713 hardware, and request paths using sleepable and atomic crypto requests to check `cc_gfp_flags()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c

Purpose: coordinates FIPS status between the REE driver and TEE firmware on CryptoCell hardware that supports GPR0 FIPS synchronization. It reports REE self-test failures to TEE and handles TEE-reported cryptographic failures.

Important APIs, types, and functions: private `struct cc_fips_handle` stores a tasklet, notifier block, and driver pointer. Public functions are `cc_fips_init()`, `cc_fips_fini()`, `fips_handler()`, `cc_set_ree_fips_status()`, and `cc_tee_handle_fips_error()`. Private helpers are `cc_get_tee_fips_status()`, `cc_ree_fips_failure()`, `tee_fips_error()`, and `fips_dsr()`.

Control flow: initialization is a no-op before hardware revision 712. Otherwise it allocates a handle, initializes a tasklet, registers a notifier on `fips_fail_notif_chain`, and immediately checks whether TEE already reported an error. When Linux FIPS infrastructure reports REE failure, `cc_ree_fips_failure()` writes an error status to HOST_GPR0. When the platform ISR sees the GPR0 interrupt, it masks the interrupt and calls `fips_handler()`, which schedules the tasklet. The tasklet checks the stored IRQ bits, calls `cc_tee_handle_fips_error()`, and attempts to unmask the interrupt. Teardown unregisters the notifier, kills the tasklet, and clears the handle.

State and persistence behavior: `drvdata->fips_handle` persists while the device is active. TEE/REE status is exchanged through hardware GPR registers rather than files. The driver may panic if TEE reports failure while the kernel is in FIPS mode; otherwise it logs an error.

Dependencies and integration points: depends on Linux FIPS notifier infrastructure, tasklets, and register access helpers from `cc_driver.h`. `cc_driver.c` initializes FIPS before algorithm allocation completes, calls `cc_set_ree_fips_status(true)` after successful crypto registration, and dispatches GPR0 IRQs into `fips_handler()`.

Risks: FIPS behavior is high impact: a TEE error can intentionally panic the system when `fips_enabled` is true. The tasklet unmask calculation uses register constants and IRQ bits, so it should be reviewed carefully against the intended HOST_IMR read-modify-write behavior. Missing notifier unregister or tasklet kill can race during driver remove. Hardware revision gating must match GPR register availability.

Test signals: boot with `CONFIG_CRYPTO_FIPS=y` and FIPS mode enabled/disabled, inject REE notifier failures, simulate TEE status OK/error bits, verify HOST_GPR0 writes, verify GPR0 interrupt mask/unmask behavior, and remove the device while no tasklet remains scheduled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h

Purpose: declares the CryptoCell FIPS synchronization interface and provides no-op stubs when kernel FIPS crypto support is disabled.

Important APIs, types, and functions: under `CONFIG_CRYPTO_FIPS`, `enum cc_fips_status` defines the bit values exchanged with TEE through GPR registers: module OK, module error, REE status present, and TEE status present. It declares `cc_fips_init()`, `cc_fips_fini()`, `fips_handler()`, `cc_set_ree_fips_status()`, and `cc_tee_handle_fips_error()`. Without FIPS support, all functions inline to no-ops or success.

Control flow: `cc_driver.c` can call FIPS hooks unconditionally. With FIPS disabled, initialization cannot fail and IRQ/status hooks are inert. With FIPS enabled, the C implementation owns notifier registration, tasklet dispatch, and TEE/REE status writes.

State and persistence behavior: no state in the header. The enum values are part of the hardware/software synchronization contract and must remain stable.

Dependencies and integration points: used by the platform driver and ISR path. It relies on `struct cc_drvdata` visibility from includers and hardware register macros in the implementation.

Risks: stubbed success means non-FIPS builds do not exercise real synchronization paths. Enum values must match firmware expectations; changes can invert OK/error reporting. Call sites must still guard hardware IRQ handling through `CONFIG_CRYPTO_FIPS` where the ISR references FIPS-specific masks.

Test signals: build with `CONFIG_CRYPTO_FIPS=y` and `n`, verify probe succeeds in both modes, and for FIPS builds validate status bit definitions against firmware tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_fips.h -->
