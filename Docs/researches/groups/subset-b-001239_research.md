# Research: subset-b-001239

Grouped source research for the subset B crypto-driver work item. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/mxs-dcp.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/mxs-dcp.c

Purpose: implements the Freescale/NXP i.MX23/i.MX28 DCP crypto accelerator as Linux Crypto API algorithms for AES-128 ECB/CBC, internal protected-key AES variants, SHA1, and SHA256. The driver owns one global DCP instance and multiplexes crypto API requests onto DCP hardware channels using per-channel queues and kernel threads.

Important types and APIs: `struct dcp` stores MMIO base, coherent bounce area, completions, queues, per-channel locks, worker threads, and capabilities. `struct dcp_async_ctx` is the transform context shared by AES and SHA paths, including channel selection, SHA algorithm state, software fallback pointer, key bytes, and protected-key state. `struct dcp_dma_desc` mirrors the hardware descriptor format. AES entry points are `mxs_dcp_aes_*_{encrypt,decrypt,setkey}` and SHA entry points are `dcp_sha_{init,update,final,finup,digest,import,export}`.

Control flow: probe maps registers, enables the optional DCP clock, resets the block, allocates aligned coherent buffers, starts one SHA thread and one AES thread, reads hardware capability bits, and registers only supported algorithms. AES requests enqueue through `mxs_dcp_aes_enqueue`, are dequeued by `dcp_chan_thread_aes`, copied into the shared page-sized input buffer, submitted by `mxs_dcp_run_aes`, copied back into destination scatterlists, and completed asynchronously. SHA requests enqueue similarly; `dcp_sha_req_to_buf` batches scatterlist bytes into the SHA buffer, submits full chunks, and finalizes with `HASH_TERM`.

State and persistence: no on-disk state exists. Runtime state is the global `global_sdcp`, per-channel crypto queues, DCP register state, request contexts, and transform contexts. SHA streaming state is persisted across update/final via `dcp_async_ctx.fill`, `hot`, and exported/imported using `struct dcp_export_state`. AES CBC IV is updated from the last ciphertext block on encrypt or last input block on decrypt.

Dependencies and integration points: integrates with platform devices matching `fsl,imx23-dcp` and `fsl,imx28-dcp`, `stmp_reset_block`, optional clock framework, DMA mapping APIs, the async skcipher/ahash crypto APIs, and the SoC protected-key constants from `soc/fsl/dcp.h`. It falls back to generic software skcipher for AES key sizes the DCP cannot process directly.

Risks: the single coherent buffer per channel means the worker-thread serialization is essential; bypassing it would corrupt in-flight operations. `mxs_dcp_start_dma` returns before unmapping the descriptor on timeout/error, which should be scrutinized for DMA lifetime regressions. Hardware only supports AES-128, so fallback flag propagation and key-size handling are security-sensitive. SHA result byte reversal and hard-coded null hashes are hardware-compatibility quirks that need vector coverage. Request length handling must keep AES block alignment and buffer flush points correct across scatterlist boundaries.

Test signals: boot/probe tests should verify algorithm registration follows capability bits and that duplicate devices are rejected. Crypto selftests should cover AES ECB/CBC 128-bit hardware paths, 192/256-bit fallback paths, protected-key key-slot validation, CBC IV chaining, SHA1/SHA256 streaming/export/import, zero-length hashes, DMA timeout/error handling, and module remove cleanup of algorithms and worker threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/mxs-dcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/Kconfig

Purpose: defines configuration gates for IBM Power NX crypto and 842 compression acceleration. It separates symmetric/hash acceleration on pSeries from compression core support and platform-specific compression backends.

Important symbols: `CRYPTO_DEV_NX_ENCRYPT` builds `nx_crypto` for pSeries encryption/hash acceleration and depends on `PPC_PSERIES`, `IBMVIO`, and big-endian CPU support. It selects AES and CCM helpers. `CRYPTO_DEV_NX_COMPRESS` enables the shared 842 crypto API layer and selects the compression algorithm API plus software 842 decompression. `CRYPTO_DEV_NX_COMPRESS_PSERIES` and `CRYPTO_DEV_NX_COMPRESS_POWERNV` build the corresponding platform submit drivers, both gated by Power platform and `PPC_VAS` requirements.

Control flow and integration: this file does not execute code, but it controls which object groups the Makefile can build. Compression support is a two-level gate: the shared `nx-842.c` layer is selected by `CRYPTO_DEV_NX_COMPRESS`, while hardware access is supplied by exactly the platform modules that match the machine.

State and persistence: Kconfig choices persist in the kernel build configuration only. There is no runtime state here.

Dependencies: depends on PowerPC platform features, IBM VIO, VAS, the crypto API, AES/CCM helpers, and software 842 decompression support.

Risks: defaults are `y`, so unsupported or lightly tested platforms can compile these drivers unless dependency expressions are accurate. The encryption option explicitly excludes little-endian CPUs, while compression does not; this asymmetry is intentional only if the compression code handles endianness through BE conversions and platform APIs. Incorrect dependency changes can produce modules with unresolved symbols or runtime probe failures.

Test signals: build matrix should cover pSeries, PowerNV, big-endian and little-endian configurations, built-in and module forms, and combinations where compression core is enabled without one or both platform backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/Makefile -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/Makefile

Purpose: maps the NX Kconfig symbols to kernel objects and groups the encryption, compression core, and platform-specific compression modules.

Important build objects: `nx-crypto.o` includes `nx.o`, AES ECB/CBC/GCM/CCM/CTR/XCBC wrappers, SHA256, and SHA512. `nx_debugfs.o` is conditionally appended under `CONFIG_DEBUG_FS`. `nx-compress.o` contains the shared `nx-842.o` crypto API shim. `nx-compress-pseries.o` and `nx-compress-powernv.o` each contain their platform backend.

Control flow and integration: the object grouping establishes link-time visibility among wrapper files. The AES/SHA wrapper files export algorithm descriptors consumed by `nx.o`, and `nx.o` supplies shared context allocation, scatterlist construction, OF capability parsing, and registration. For compression, platform modules depend on exported symbols from `nx-842.c` for context allocation and crypto API compress/decompress entry points.

State and persistence: build-only metadata; no runtime state.

Dependencies: depends on Kbuild, `CONFIG_CRYPTO_DEV_NX_ENCRYPT`, `CONFIG_CRYPTO_DEV_NX_COMPRESS_PSERIES`, `CONFIG_CRYPTO_DEV_NX_COMPRESS_POWERNV`, and `CONFIG_DEBUG_FS`.

Risks: because platform compression modules and shared compression core are linked as separate objects, symbol exports from `nx-842.c` must remain aligned with platform users. Adding a new AES/SHA wrapper requires updating both this Makefile and `nx.h`/`nx.o` registration tables. Debugfs inclusion must not make core registration depend on debugfs symbols when disabled.

Test signals: compile tests should verify all Kconfig combinations, especially debugfs on/off and platform modules as loadable modules. Link checks should catch missing exported algorithm descriptors or compression symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.c

Purpose: provides the shared Crypto API `scomp` implementation for IBM NX 842 hardware compression. It adapts arbitrary caller buffers to hardware-specific alignment, size, and multiplicity constraints supplied by a platform `struct nx842_driver`, adds a private header when needed, splits oversized inputs into groups, and falls back to software 842 only for decompression.

Important types and functions: `struct nx842_crypto_ctx` owns per-stream work memory, source/destination bounce buffers, a cached header, and the selected platform driver. `struct nx842_crypto_param` tracks input/output cursors. `nx842_crypto_alloc_ctx` and `nx842_crypto_free_ctx` are exported to platform drivers. Public crypto operations are `nx842_crypto_compress` and `nx842_crypto_decompress`. Internal helpers include `compress`, `decompress`, `update_param`, `check_constraints`, and `nx842_crypto_add_header`.

Control flow: compression copies platform constraints, limits maximum to the bounce buffer size, decides whether a header is needed based on input/output alignment, size, and maximum constraints, then repeatedly calls `compress` for up to `NX842_CRYPTO_GROUP_MAX` groups. `compress` may bounce source or destination, reserves header/padding space, retries hardware `-EBUSY` until `COMP_BUSY_TIMEOUT`, records group metadata, and advances cursors. Decompression parses the private magic header if present, otherwise treats input as raw 842. Each group is normalized and sent to hardware; hardware failures or unsupported constraints branch to `sw842_decompress`.

State and persistence: state is per allocated compression stream and protected by `spin_lock_bh`. The private on-buffer header is an interoperability contract: compressed outputs may include `NX842_CRYPTO_MAGIC`, ignore byte count, group count, and group descriptors. There is no persistent kernel state beyond allocated contexts.

Dependencies and integration: platform backends provide `compress`, `decompress`, `constraints`, and `workmem_size`. The file depends on `linux/sw842.h` for software fallback, `crypto_scomp` call conventions, vmalloc/physical address helpers via headers, and the header layout from `nx-842.h`.

Risks: header parsing is security-sensitive because decompression consumes untrusted compressed buffers; group count, header length, padding, compressed length, and ignore handling must reject overflows. Compression never falls back to software, so callers must handle hardware failure. Bounce buffer and maximum clamping are central to avoiding overrun. The distinction between raw software 842 and private-header NX output must remain stable.

Test signals: test raw 842 decompression, private-header round trips, multi-group compression, misaligned buffers, too-small outputs, non-multiple lengths, padded final groups, busy retry behavior, software fallback on hardware decompression rejection, and malformed headers with zero groups, excessive groups, truncated header, oversized padding, and invalid lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.h

Purpose: declares shared constants, data structures, and exported entry points for the NX 842 compression stack used by both pSeries and PowerNV backends.

Important types and definitions: hardware DDE/DDL constraints include `DDE_BUFFER_ALIGN`, `DDE_BUFFER_SIZE_MULT`, `DDE_BUFFER_LAST_MULT`, and `DDL_LEN_MAX`. CCW masks and function codes define compress/decompress with and without CRC. CSB completion-code aliases cover 842-specific errors, duplicated translation/protection codes, and hypervisor/hardware failures. `struct nx842_constraints` describes buffer alignment, length multiple, minimum, and maximum requirements. `struct nx842_driver` is the platform backend contract. Header types `struct nx842_crypto_header` and `struct nx842_crypto_header_group` define the private grouped compression framing. `struct nx842_crypto_ctx` defines shared stream state.

Control flow and integration: platform drivers allocate stream contexts through `nx842_crypto_alloc_ctx(&driver)` and register `nx842_crypto_compress`/`nx842_crypto_decompress` as `scomp` callbacks. The shared layer invokes the function pointers in `struct nx842_driver` after normalizing buffers to the advertised constraints. `nx842_get_pa` abstracts physical address lookup for linear and vmalloc addresses.

State and persistence: header structures can be embedded in compressed output and therefore form persistent data within a compressed buffer. Context fields such as bounce buffers, header cache, and work memory are runtime-only.

Dependencies: includes kernel/module/OF/slab/io/mm helpers and relies on PowerPC physical address translation conventions. It forward-declares `crypto_scomp`.

Risks: the private header ABI is packed and bounded by `NX842_CRYPTO_GROUP_MAX`; any layout change can break decompression of existing NX-framed buffers. `nx842_get_pa` assumes page-backed vmalloc memory and direct physical addressing acceptable to the platform backend. Constraint semantics must stay consistent between platform code and the shared normalizer.

Test signals: compile checks should catch structure layout changes, including the static assertion around `__struct_group`. Runtime tests should validate context allocation/free under both backends, header compatibility, vmalloc and linear buffer handling, and all CCW/CSB error code mappings used by backend validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-842.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-cbc.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-cbc.c

Purpose: registers and implements `cbc(aes)` using IBM Power NX symmetric encryption hardware through the shared NX crypto context.

Important APIs: `cbc_aes_nx_set_key` initializes the CPB for AES CBC, records the key size property slot, and copies the key. `cbc_aes_nx_crypt` performs encrypt/decrypt loops. `nx_cbc_aes_alg` is the exported `skcipher_alg` descriptor consumed by `nx.o`.

Control flow: setkey calls `nx_ctx_init`, maps key lengths to NX key-size fields, selects `nx_ctx->ap`, sets CPB mode `NX_MODE_AES_CBC`, and stores the key. Encryption/decryption acquire `nx_ctx->lock`, set or clear `NX_FDM_ENDE_ENCRYPT`, repeatedly build NX scatterlists from the request at the current offset, reject empty in/out lists, issue `nx_hcall_sync`, copy the chaining value back to `req->iv`, update stats, and continue until the request length is processed.

State and persistence: per-transform state is the aligned CPB, key material, selected OF algorithm properties, and shared stats pointer. Per-request mutable state is the IV, which is updated for CBC chaining. No persistent storage exists.

Dependencies: depends on `nx_build_sg_lists`, `nx_hcall_sync`, CPB definitions from `nx_csbcpb.h`, AES key constants, and registration in `nx.o`.

Risks: CBC requires block-aligned request lengths, so caller-side crypto API validation and scatterlist trimming matter. Incorrect IV update breaks multi-call chaining. The CPB is reused across requests, making the spinlock mandatory. Stats use the CSB processed-byte count and depend on successful hardware completion.

Test signals: AES-CBC encrypt/decrypt vectors for 128/192/256-bit keys, multi-page scatterlists, partial processing bounded by OF `databytelen`, IV mutation checks, busy/error hcall paths, and concurrent request serialization on one transform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-cbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ccm.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ccm.c

Purpose: implements `ccm(aes)` and `rfc4309(ccm(aes))` AEAD algorithms using NX AES CCM plus AES CCA helper operations for associated-data authentication.

Important APIs and helpers: `ccm_aes_nx_set_key`, `ccm4309_aes_nx_set_key`, authsize validators, `set_msg_len`, `crypto_ccm_check_iv`, `generate_b0`, `generate_pat`, `ccm_nx_encrypt`, `ccm_nx_decrypt`, and exported descriptors `nx_ccm_aes_alg` and `nx_ccm4309_aes_alg`.

Control flow: setkey supports only AES-128 and initializes both the main CCM CPB and secondary CCA CPB. RFC4309 setkey splits a trailing 3-byte nonce from the key. `generate_pat` builds B0/B1 formatting, handles short AAD inline and long AAD through one or more CCA hcalls, and copies the resulting authentication state into the CCM CPB. Encrypt/decrypt then loop over payload chunks, maintain intermediate/continuation flags, build scatterlists after the AAD region, call hardware, carry forward output counter/MAC/S0 state, and either write the tag or compare it with constant-time `crypto_memneq`.

State and persistence: per-transform state includes key, RFC4309 nonce, temporary auth tags, and two CPBs. Per-request state includes a synthetic IV in `struct nx_ccm_rctx`. No durable state exists.

Dependencies: depends on NX core AEAD context allocation, `nx_build_sg_lists`, `nx_walk_and_build`, scatterlist copy helpers, AES/AEAD crypto APIs, and CCM/RFC4309 formatting rules.

Risks: AAD length encoding and `assoclen - 8` for RFC4309 are easy underflow points if checks regress. Only AES-128 is supported despite the generic CCM name. Long AAD chunking updates stats with `assoclen` each loop, which may overcount. Tag compare and authsize validation are security-critical. The secondary CPB and shared scatterlist area are reused under one spinlock.

Test signals: CCM and RFC4309 known-answer vectors, all accepted auth sizes, rejected auth sizes, invalid IV `L'`, zero AAD, short AAD <=14, medium and large AAD paths, encrypt/decrypt tag mismatch, chunked payloads, and underflow tests for RFC4309 associated data length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ccm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ctr.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ctr.c

Purpose: implements the RFC3686 variant of AES-CTR using NX hardware.

Important APIs: `ctr_aes_nx_set_key` prepares the AES CTR CPB, `ctr3686_aes_nx_set_key` extracts the trailing nonce from the key, `ctr_aes_nx_crypt` performs the shared encrypt/decrypt operation, `ctr3686_aes_nx_crypt` constructs the RFC3686 IV, and `nx_ctr3686_aes_alg` exports `rfc3686(ctr(aes))`.

Control flow: base setkey initializes the context for AES, selects the correct key property slot for 128/192/256-bit keys, sets `NX_MODE_AES_CTR`, and copies the key. RFC3686 setkey requires a key longer than the nonce, stores the 4-byte nonce in context, and delegates to base setkey. Crypt builds a 16-byte counter block from nonce, request IV, and initial counter 1, loops through scatterlist chunks with `nx_build_sg_lists`, calls `nx_hcall_sync`, copies the output counter for continuation, and updates AES stats.

State and persistence: the transform stores the RFC3686 nonce and key in CPB memory. A local IV/counter is used per request; the caller's request IV is not mutated by the RFC3686 wrapper.

Dependencies: AES and CTR crypto helpers, CPB constants, NX core scatterlist and hcall functions, and OF-provided algorithm properties.

Risks: CTR permits byte-granular blocksize but the NX chunk builder may trim to AES block boundaries when limited; short or non-multiple lengths need vector coverage. The code copies `aes_cbc.cv` while operating in CTR CPB union storage; this relies on union layout equivalence and should be watched during structure changes. Counter continuation must be correct across hardware chunks.

Test signals: RFC3686 test vectors for all AES key sizes, non-block-multiple lengths, multi-chunk large requests, scatterlist offsets, nonce extraction failure for too-short keys, and encrypt/decrypt equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ecb.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ecb.c

Purpose: implements `ecb(aes)` through NX hardware.

Important APIs: `ecb_aes_nx_set_key` initializes key size, algorithm properties, CPB mode, and key bytes. `ecb_aes_nx_crypt` performs encrypt/decrypt hardware calls. `nx_ecb_aes_alg` exports the skcipher descriptor.

Control flow: setkey calls `nx_ctx_init`, maps AES key lengths to NX key size constants and property slots, sets `NX_MODE_AES_ECB`, and copies key bytes. Crypt takes the context lock, sets encrypt/decrypt direction in CPB flags, loops over request chunks bounded by OF limits and scatterlist capacity, issues synchronous hcalls, updates AES operation/byte counters, and releases the lock.

State and persistence: per-transform state is the CPB, key, selected algorithm properties, and stats pointer. ECB has no IV or request-persistent state.

Dependencies: uses NX core context initialization, scatterlist building, hcall submission, and crypto API registration performed in `nx.o`.

Risks: ECB is block-oriented and structurally simple, but it still depends on accurate scatterlist length trimming and nonzero hcall input/output lengths. The reused CPB must not be accessed concurrently without the spinlock. ECB mode has no semantic IV protection; it should be exposed only as the standard crypto API primitive.

Test signals: AES-ECB known-answer vectors for 128/192/256-bit keys, invalid key size rejection, large multi-page scatterlists, chunking at `databytelen`, hcall error propagation, and concurrent transform use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ecb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-gcm.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-gcm.c

Purpose: implements `gcm(aes)` and `rfc4106(gcm(aes))` AEAD algorithms using NX AES-GCM hardware plus AES-GCA/GMAC helper paths for associated data and empty payloads.

Important APIs and helpers: `gcm_aes_nx_set_key`, `gcm4106_aes_nx_set_key`, `gcm4106_aes_nx_setauthsize`, `nx_gca`, `gmac`, `gcm_empty`, `gcm_aes_nx_crypt`, RFC4106 wrappers, and exported descriptors `nx_gcm_aes_alg` and `nx_gcm4106_aes_alg`.

Control flow: setkey initializes main GCM and secondary GCA CPBs for all AES key sizes; RFC4106 stores a trailing 4-byte nonce. Requests synthesize the 16-byte GCM IV, initialize counter word 1, process empty-message cases through `gcm_empty` or `gmac`, process AAD through `nx_gca`, then loop over payload chunks with `nx_build_sg_lists` and `nx_hcall_sync`. Each chunk carries forward counter, GHASH pattern, and S0 state. Encrypt writes the tag to destination; decrypt reads the input tag and compares it with `crypto_memneq`.

State and persistence: per-transform state includes key, RFC4106 nonce, secondary CPB, and temporary tag storage. Per-request state is `struct nx_gcm_rctx` with the mutable IV/counter. No persistent storage exists.

Dependencies: AES/GCM crypto helpers, scatterwalk copy helpers, NX core hcall and scatterlist functions, CPB mode definitions, and algorithm registration in `nx.o`.

Risks: RFC4106 requires at least 8 bytes of associated data; the wrapper checks this before subtracting. Empty payload handling temporarily switches CPB mode to ECB/GMAC and must restore it and scrub the ECB key overlay. AAD chunk stats appear to add the full assoclen per chunk, which can overcount. Tag handling, IV construction, authsize constraints, and state carry-forward across chunks are security-sensitive.

Test signals: GCM/RFC4106 known-answer vectors for all AES key sizes, auth sizes 8/12/16 for RFC4106, zero payload with and without AAD, long AAD chunking, tag mismatch, nonce extraction, invalid short RFC4106 AAD, scatterlist offsets, and multi-chunk counter continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-gcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-xcbc.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-xcbc.c

Purpose: implements the `xcbc(aes)` shash algorithm using NX AES-XCBC-MAC hardware, including a software-assisted hardware ECB sequence for the zero-length message case.

Important types and APIs: `struct xcbc_state` stores the current MAC state. `nx_xcbc_set_key`, `nx_xcbc_init`, `nx_xcbc_update`, `nx_xcbc_finup`, `nx_xcbc_empty`, and `nx_crypto_ctx_aes_xcbc_init2` implement the shash lifecycle. `nx_shash_aes_xcbc_alg` exports the algorithm descriptor.

Control flow: transform init allocates the shared NX SHA/AES context, calls `nx_ctx_init`, sets AES-128 key size, and selects `NX_MODE_AES_XCBC_MAC`. Setkey accepts only AES-128. Update copies previous state into the CPB, marks intermediate/continuation, builds input and output scatterlists for block-aligned data, invokes hardware, and returns leftover bytes to the shash core. Final processes the final nonzero block with intermediate cleared; zero-length final calls `nx_xcbc_empty`, which temporarily switches to ECB mode to derive K1/K3 and calculate the RFC3566 tag.

State and persistence: the descriptor state holds the running MAC. The transform CPB stores key and temporary CV/MAC fields. No durable storage exists.

Dependencies: NX core hcall/scatterlist helpers, AES constants, CPB mode definitions, shash block-only semantics, and algorithm registration in `nx.o`.

Risks: only AES-128 keys are valid. The algorithm declares `CRYPTO_AHASH_ALG_BLOCK_ONLY` and `FINAL_NONZERO`, so update/final contracts depend on the shash core supplying appropriate lengths. The zero-length special path changes CPB mode/key and must restore both. Nested calls under the same spinlock are notable because `nx_xcbc_finup` calls `nx_xcbc_empty` while already locked.

Test signals: RFC3566 vectors, zero-length vector, invalid key sizes, update/finup splits, block-only behavior, leftover return values, CPB mode restoration after empty digest, and concurrent transform serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-xcbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-powernv.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-powernv.c

Purpose: provides the PowerNV hardware backend for NX 842 compression. It discovers NX coprocessors from the device tree, chooses either legacy ICSWX submission or Power9+ VAS copy/paste submission, registers the `842` scomp algorithm, and supplies the shared `nx-842.c` layer with hardware constraints and function pointers.

Important types and functions: `struct nx842_workmem` contains aligned CRB and DDLs. `struct nx_coproc` tracks chip, coprocessor type/instance, and VAS receive window. Submission helpers include `setup_direct_dde`, `setup_indirect_dde`, `setup_ddl`, `nx842_config_crb`, `nx842_exec_icswx`, `nx842_exec_vas`, and `wait_for_csb`. Discovery/setup includes `nx_powernv_probe_vas`, `nx842_powernv_probe`, `nx_open_percpu_txwins`, `vas_cfg_coproc_info`, and `nx_coproc_init`.

Control flow: module init verifies alignment assumptions, scans `ibm,power9-nx` nodes for VAS FIFOs, initializes coprocessors through OPAL, registers a VAS userspace API for GZIP, and opens per-CPU TX windows for 842. If no VAS coprocessors are found, it scans legacy `ibm,power-nx` nodes and uses ICSWX. Compression/decompression wrappers pass CRC function codes into the selected exec function. Each exec builds DDE/DDL descriptors, submits the CRB, waits for CSB validity, maps completion codes to Linux errors, and returns processed length.

State and persistence: runtime state is global `nx_coprocs`, per-CPU `cpu_txwin`, `nx842_ct`, the selected `nx842_powernv_exec` function pointer, and registered scomp algorithm state. No persistent storage exists.

Dependencies: PowerNV OF nodes, OPAL NX initialization, VAS APIs, ICSWX, PowerPC physical address helpers, CSB/CRB definitions, crypto scomp API, and shared `nx-842.c` exports.

Risks: per-CPU VAS windows assume each CPU maps to a chip with a high-priority 842 FIFO. DDE setup enforces alignment and length constraints; relaxing constraints risks hardware checkstops or protocol errors. `wait_for_csb` busy-waits up to 5 seconds, so hung hardware impacts CPU time. VAS retry handling and preemption disabling are sensitive. Init cleanup must close RX/TX windows on every failure path.

Test signals: boot tests on Power8 ICSWX and Power9+ VAS systems, DT missing-property failures, OPAL failure handling, per-CPU TX window setup, malformed CSB code mapping, compression/decompression scomp vectors, busy/timeout paths, module unload window cleanup, and fallback to legacy path when VAS nodes are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-powernv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-pseries.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-pseries.c

Purpose: provides the pSeries VIO backend for NX 842 compression. It submits 842 operations through `vio_h_cop_sync`, manages OF-derived constraints and live property updates, registers sysfs counters, exposes optional NX-GZIP capability data, and registers the `842` scomp algorithm through the shared `nx-842.c` layer.

Important types and functions: `struct nx842_devdata` stores the VIO device, counters, and OF limits. `struct nx842_workmem` contains pHyp scatterlists and `nx_csbcpb`. `nx842_pseries_compress` and `nx842_pseries_decompress` are backend function pointers. OF helpers include `nx842_OF_set_defaults`, `nx842_OF_upd_status`, `nx842_OF_upd_maxsglen`, `nx842_OF_upd_maxsyncop`, `nx842_OF_upd`, and `nx842_OF_notifier`. Probe/remove are `nx842_probe` and `nx842_remove`.

Control flow: init confirms an `ibm,compression` node, initializes RCU `devdata`, queries VAS/NX-GZIP capabilities, registers the VIO driver, and registers a pSeries VAS userspace API. Probe allocates devdata/counters, publishes them with RCU, registers the OF reconfig notifier, validates current OF properties, registers the scomp algorithm, and creates sysfs groups. Each compression operation checks alignment/length constraints, builds direct or indirect pHyp scatterlists, fills a `vio_pfo_op`, calls `vio_h_cop_sync`, validates CSB status, updates counters/histograms, and returns processed output length.

State and persistence: runtime state is global RCU-protected `devdata`, constraints maximum updated from OF, atomic counters and latency histograms, sysfs attributes, VAS capability globals, and the registered scomp algorithm. OF reconfiguration can replace devdata live; there is no on-disk state.

Dependencies: IBM VIO, hypervisor calls, OF reconfiguration notifier, VAS capability query APIs, sysfs, RCU, atomic counters, shared NX CSB/CPB structs, and `nx-842.c` exported context/operation functions.

Risks: `nx842_OF_upd` uses a property-name filter with ORed `strncmp` conditions that appears likely to treat most updates as uninteresting only if all names match, which warrants review. Probe error paths after crypto/sysfs registration must avoid leaked registration. Exit unregisters the scomp algorithm even though remove also does, so double-unregister ordering should be tested. RCU replacement must preserve counter ownership and not race with active operations. Hardware constraints are mutable and feed the shared compressor.

Test signals: VIO probe/remove, OF property update/reconfig tests for status/max-sg/max-sync, scomp vectors, sysfs counter and histogram reads, invalid alignment/length rejection, pHyp hcall error mapping, CSB error-code mapping, RCU race tests under concurrent compression, and init/exit with VAS capability present/absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-common-pseries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha256.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha256.c

Purpose: implements the `sha256` shash algorithm using NX SHA hardware.

Important types and APIs: `struct sha256_state_be` stores the big-endian hardware digest words and byte count. `nx_crypto_ctx_sha256_init`, `nx_sha256_init`, `nx_sha256_update`, `nx_sha256_finup`, `nx_sha256_export`, and `nx_sha256_import` implement the shash lifecycle. `nx_shash_sha256_alg` exports the descriptor.

Control flow: transform init allocates a SHA context through `nx_crypto_ctx_sha_init`, initializes HCOP SHA state, selects the SHA256 property slot, and sets digest size in CPB. Descriptor init seeds SHA256 initial constants in big-endian form. Update locks the context, copies current digest into the CPB, marks intermediate/continuation, builds output scatterlist to descriptor state, repeatedly processes full SHA256 blocks through hardware, updates count, stores the new digest, and returns leftover bytes. Finup copies partial digest, clears intermediate, sets total bit length, builds input/output lists, calls hardware, updates stats, and copies final digest.

State and persistence: descriptor state persists digest and byte count across shash updates and can be exported/imported in CPU-endian format. Transform state is runtime CPB/scatterlist memory.

Dependencies: NX core context/hcall/scatterlist helpers, SHA2 constants, unaligned access helpers, CPB SHA definitions, and registration in `nx.o`.

Risks: update returns leftover length and relies on the shash core to retain unprocessed bytes. Endianness conversion in import/export is critical. The message bit length is a 64-bit `sctx->count * 8`; overflow behavior should match shash expectations. Zero-length final and partial-block handling need vector coverage.

Test signals: SHA256 known-answer vectors, streaming split at every byte around block boundaries, export/import round trips, zero-length digest, large updates bounded by OF limits, hcall failure propagation, and stats increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha512.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha512.c

Purpose: implements the `sha512` shash algorithm using NX SHA hardware.

Important types and APIs: `struct sha512_state_be` stores big-endian SHA512 state and a two-word byte count. Lifecycle functions are `nx_crypto_ctx_sha512_init`, `nx_sha512_init`, `nx_sha512_update`, `nx_sha512_finup`, `nx_sha512_export`, and `nx_sha512_import`. `nx_shash_sha512_alg` is the exported descriptor.

Control flow: transform init selects SHA function/mode, property slot `NX_PROPS_SHA512`, and digest size `NX_DS_SHA512`. Init seeds SHA512 constants. Update locks the context, copies current digest into the CPB, marks intermediate/continuation, builds output scatterlist to descriptor state, processes full SHA512 blocks, increments a two-word byte counter on wrap, stores hardware digest output, and returns leftover bytes. Finup computes high/low bit length from the two-word count plus final bytes, builds input/output scatterlists, calls hardware, updates stats, and copies final digest.

State and persistence: descriptor state persists digest and 128-bit-ish byte count across updates and can be exported/imported with endian conversion. Transform CPB and scatterlists are runtime-only.

Dependencies: NX core helpers, SHA512 constants, unaligned access helpers, CPB SHA512 fields, and algorithm registration in `nx.o`.

Risks: high-count arithmetic is subtle; `count1` is incremented on update wrap and then shifted into bit length in final. Export/import must preserve both count words. As with SHA256, leftover return semantics and OF-limited chunking must match shash core behavior. The final path does not explicitly verify `len == SHA512_DIGEST_SIZE` after building the output SG, unlike SHA256.

Test signals: SHA512 known-answer vectors, split-update fuzzing around 128-byte block boundaries, very large simulated count/import cases, export/import round trips, zero-length digest, hcall error propagation, and output scatterlist length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.c

Purpose: is the shared core for the pSeries NX symmetric/hash crypto driver. It parses VIO/OpenFirmware capabilities, registers supported algorithms, allocates aligned per-transform workspaces, builds NX scatterlists, submits synchronous hypervisor coprocessor calls, records debug stats, and owns the VIO driver lifecycle.

Important APIs and types: `nx_hcall_sync`, `nx_build_sg_list`, `nx_walk_and_build`, `nx_build_sg_lists`, `nx_ctx_init`, `nx_crypto_ctx_*_init`, and `nx_crypto_ctx_*_exit` are shared by algorithm wrappers. OF parsing is handled by `nx_of_update_status`, `nx_of_update_sglen`, `nx_of_update_msc`, and `nx_of_init`. Registration helpers gate algorithms on parsed properties. `struct nx_crypto_driver nx_driver` is the global driver state.

Control flow: module init registers a VIO driver for `ibm,sym-encryption`. Probe rejects multiple devices, records the VIO device, parses OF properties, and calls `nx_register_algs`. Registration validates status/max-sg/max-sync-cop, initializes stats/debugfs, sets status OK, then registers ECB, CBC, CTR, GCM, RFC4106 GCM, CCM, RFC4309 CCM, SHA256, SHA512, and XCBC in order with unwind paths. Each transform init allocates a 4K-aligned CPB plus input/output SG pages, optionally a secondary AEAD CPB, copies OF properties into the context, and attaches stats.

State and persistence: global state is `nx_driver` with OF properties, stats, debugfs root, and VIO device. Per-transform state is allocated `kmem`, aligned CPBs, SG pages, property slots, private nonce/tag state, and stats pointer. No persistent storage exists.

Dependencies: IBM VIO hcalls, OF properties `status`, `ibm,max-sg-len`, `ibm,max-sync-cop`, Linux crypto APIs, debugfs, PowerPC physical address helpers, and algorithm descriptors declared in `nx.h`.

Risks: scatterlist trimming is complex and uses negative lengths to signal SG lists to pHyp; arithmetic mistakes can underprocess data or violate block alignment. Remove unregisters SHA256/SHA512 with swapped property-slot constants, which should be reviewed. `nx_crypto_ctx_aead_exit` frees memory but does not null pointers like the generic exit. OF parsing must reject malformed variable-length `max-sync-cop` properties without reading past the property.

Test signals: VIO probe/remove, OF property parser fuzzing, registration unwind on each algorithm failure, algorithm selftests, debugfs stat visibility, SG building for vmalloc and highmem-like page boundaries, hcall busy retry behavior, and module unload with active transforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.h

Purpose: declares the shared interface and state model for the NX symmetric/hash crypto driver.

Important types: `struct nx_sg` is the packed scatterlist format expected by pHyp. `enum nx_status`, `struct msc_triplet`, `struct max_sync_cop`, `struct alg_props`, and `struct nx_of` represent parsed OpenFirmware capabilities. `struct nx_stats` stores operation, byte, sync-call, and error counters. `struct nx_crypto_driver` is the module-level VIO/debugfs state. AEAD and mode-specific private structs store GCM/CCM request IVs, nonces, tags, XCBC key, and CTR nonce. `struct nx_crypto_ctx` is the per-transform workspace with aligned CPBs, VIO operation structs, NX SG pages, properties, stats, and private mode state.

Control flow and integration: algorithm wrappers include this header to call context initializers, `nx_ctx_init`, `nx_hcall_sync`, and scatterlist builders. `nx.o` includes it to define the global `nx_driver` and register external algorithm descriptors. Debugfs init/fini macros compile to no-ops without `CONFIG_DEBUG_FS`.

State and persistence: structures describe runtime-only module, transform, request, and stats state. There is no persistent storage. Some fields hold key material and must be freed with sensitive cleanup by exit paths.

Dependencies: crypto internal AEAD/hash/skcipher APIs, CTR helper constants, Power VIO definitions, and CPB constants from `nx_csbcpb.h` via implementation files.

Risks: this header is the ABI between many NX files; changing `struct nx_crypto_ctx` layout affects every algorithm descriptor's `cra_ctxsize`. `NX_MAX_SG_ENTRIES` assumes a 4K page for SG pages. Private union fields must not overlap in ways that wrappers misuse across modes. Debugfs macros must match function declarations.

Test signals: compile all NX algorithms with debugfs on/off, validate `cra_ctxsize` users after structure changes, run all AES/SHA/AEAD vectors, and use KASAN/KMSAN-style tests for context allocation/free and key cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_csbcpb.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_csbcpb.h

Purpose: defines the packed NX coprocessor status block and coprocessor parameter block layouts for AES, AEAD, XCBC, SHA256, and SHA512 operations, plus mode/function constants used by the NX crypto wrappers.

Important structures and macros: `struct cop_symcpb_*` variants model per-mode CPB payloads. `struct cop_symcpb_header`, `struct cop_parameter_block`, `struct cop_status_block`, and `struct nx_csbcpb` define the complete hardware page layout. Macros such as `NX_CPB_FDM`, `NX_CPB_SET_KEY_SIZE`, `NX_CPB_SET_DIGEST_SIZE`, `NX_CSB_VALID_BIT`, mode constants, FDM continuation/intermediate/encrypt flags, function codes, key sizes, digest sizes, and property indices are used throughout the NX driver.

Control flow and integration: wrappers fill the CPB header/mode/key/IV/state fields before calling `nx_hcall_sync`. The hypervisor/hardware writes the CSB and output CPB fields such as chaining values, message digests, counters, MACs, and processed-byte counts. `nx_ctx_init` sets the CSB valid bit and physical addresses for hcalls.

State and persistence: CPBs are per-transform runtime memory, but they contain sensitive key material and intermediate authentication/hash state. No fields are persisted outside kernel memory unless algorithm wrappers explicitly copy IVs/tags/digests to caller buffers.

Dependencies: exact packed layout expected by IBM NX hardware and pHyp. Includes no external headers beyond basic types through includers.

Risks: any structure padding, field size, or constant change can break hardware protocol. Union overlays mean wrappers must reference the correct member for the active mode. Key/digest size macros OR bits into `ks_ds`; callers must initialize/clear CPBs before reuse. Endianness of multi-byte CSB fields is hardware-defined and must be converted at use sites.

Test signals: build-time layout checks would be valuable, plus algorithm known-answer tests for every mode, hcall CSB processed-byte validation, key-size/digest-size selection tests, and static analysis for sensitive data lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_csbcpb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_debugfs.c

Purpose: exposes NX crypto driver counters through debugfs when `CONFIG_DEBUG_FS` is enabled.

Important APIs: `nx_debugfs_init` creates the `nx-crypto` directory and read-only files for AES/SHA operation and byte counters, total errors, last hypervisor error, and last error PID. `nx_debugfs_fini` removes the tree.

Control flow: `nx_register_algs` calls `NX_DEBUGFS_INIT` before algorithm registration after stats are zeroed and OF state is ready. `nx_remove` calls `NX_DEBUGFS_FINI` before unregistering algorithms. The file is compiled only when the Makefile appends it under debugfs.

State and persistence: debugfs entries point directly at atomic counter storage in `struct nx_stats`. The entries are runtime-only and removed on device removal/module exit.

Dependencies: Linux debugfs, VIO/device headers, crypto headers for shared declarations, and `nx.h` macros that compile calls away when debugfs is disabled.

Risks: debugfs exposes diagnostic counters but not key material. The code does not check `debugfs_create_dir` or file creation errors, which is conventional but means missing debugfs entries do not block operation. Directly exposing atomic counter internals relies on stable atomic field layout expected by debugfs helpers.

Test signals: mount debugfs and verify all files appear after successful probe, counters increment after AES/SHA operations, error fields update on injected hcall failures, and the directory disappears after remove. Also build with `CONFIG_DEBUG_FS=n` to verify no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/nx/nx_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes-gcm.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/omap-aes-gcm.c

Purpose: implements OMAP AES GCM AEAD request handling for `gcm(aes)` and `rfc4106(gcm(aes))`, sharing device selection, DMA, register programming, and engine integration with `omap-aes.c`.

Important APIs: queue and completion helpers are `omap_aes_gcm_handle_queue`, `omap_aes_gcm_crypt_req`, `omap_aes_gcm_finish_req`, `omap_aes_gcm_dma_out_callback`, and `omap_aes_gcm_done_task`. Request setup is `omap_aes_gcm_copy_buffers` and `omap_aes_gcm_prepare_req`. Public crypto callbacks include encrypt/decrypt wrappers, RFC4106 wrappers, setkey/authsize functions, and `omap_aes_gcm_cra_init`.

Control flow: encrypt/decrypt wrappers synthesize IVs, precompute E(K, J0) into `rctx->auth_tag`, validate RFC4106 AAD length, and enqueue via the shared crypto engine. The engine calls `omap_aes_gcm_prepare_req`, which aligns/copies AAD and payload into DMA-friendly SG lists, assigns device state, and writes AES control registers. DMA completion reads hardware tag registers, XORs with the precomputed tag and input tag for decrypt, cleans temporary SG buffers, copies auth tags on encrypt, checks decrypt tag mismatch, finalizes the AEAD request, and autosuspends the device.

State and persistence: per-request `omap_aes_reqctx` stores mode flags, synthetic IV, and auth tag scratch. Device state stores `aead_req`, SG pointers, total payload length, associated-data length, auth size, and flags. No persistent state exists beyond transform key/nonce in `omap_aes_gcm_ctx`.

Dependencies: `omap-aes.c` exports `omap_aes_find_dev`, `omap_aes_write_ctrl`, DMA start/stop, and GCM DMA callback hookup. Uses OMAP crypto SG alignment helpers, AES software key schedule for J0 encryption, crypto IPsec/GCM authsize validators, DMA engine APIs, runtime PM, and scatterwalk copy helpers.

Risks: RFC4106 subtracts 8 from assoclen in multiple paths, so validation order is critical. Zero-length AAD+payload returns a tag without hardware DMA and must be correct. Decrypt tag verification checks whether XOR result bytes are nonzero; it should remain constant-time enough for kernel AEAD expectations. SG cleanup must mirror all copy paths to avoid leaks or data corruption. `sg_arr` stack reuse around `scatterwalk_ffwd` is delicate.

Test signals: GCM and RFC4106 AEAD vectors, empty payload/AAD case, AAD-only and payload-only cases, authsize validation, decrypt bad-tag rejection, in-place and out-of-place SGs, unaligned SGs requiring copies, DMA and PIO-not-used interactions through shared driver, and runtime PM completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes-gcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.c

Purpose: implements the TI OMAP AES platform driver and Crypto API engine integration for AES ECB/CBC/CTR skciphers and, on OMAP4-class pdata, GCM AEAD algorithms implemented in `omap-aes-gcm.c`.

Important types and APIs: global `dev_list` provides round-robin device selection through `omap_aes_find_dev`. Core hardware helpers include `omap_aes_hw_init`, `omap_aes_write_ctrl`, DMA trigger/stop functions, `omap_aes_crypt_dma_start`, `omap_aes_crypt_dma`, and the PIO IRQ handler. Skcipher lifecycle functions include `omap_aes_prepare_req`, `omap_aes_crypt_req`, `omap_aes_crypt`, setkey/init/exit, and mode wrappers. Probe/remove register engine algorithms based on per-SoC `struct omap_aes_pdata`.

Control flow: probe obtains OF or platform resources, maps registers, enables runtime PM, reads hardware revision, initializes DMA or PIO fallback IRQ mode, adds the device to the global list, starts a crypto engine, and registers skcipher and optional AEAD engine algorithms. A skcipher request below `aes_fallback_sz` uses software fallback. Larger requests select a device, transfer to the crypto engine, align/copy input/output SGs as needed, write key/IV/control registers, map DMA SGs, submit DMA in/out descriptors, and trigger hardware. Completion work unmaps DMA, stops hardware DMA, cleans copy buffers, updates IV for CBC/CTR, finalizes the request, and autosuspends.

State and persistence: runtime state includes device list, per-device engine queue, DMA channels, SG pointers, mode flags, copy flags, fallback threshold, queue length sysfs setting, and runtime PM status. Transform state stores key material and fallback cipher. Sysfs attributes `fallback` and `queue_len` persist only until reboot/module unload.

Dependencies: platform/OF matching for `ti,omap2-aes`, `ti,omap3-aes`, `ti,omap4-aes`; DMA engine, runtime PM, crypto engine, OMAP crypto alignment helpers, `omap-aes.h` register/pdata definitions, and `omap-aes-gcm.c` AEAD callbacks.

Risks: `omap_aes_remove` assumes `aead_algs_info` is non-null, which is risky for OMAP2/3 pdata without AEAD algorithms. `omap_aes_setkey` ignores fallback setkey failure and returns success, which could mask unusable fallback state. DMA/PIO paths share device fields and must be serialized by the crypto engine. Sysfs queue length updates all devices under locks but affect active admission behavior. Runtime PM get/put balance must hold across all error paths.

Test signals: skcipher vectors for ECB/CBC/CTR, small-request fallback threshold behavior, invalid block sizes, key sizes 128/192/256, DMA and PIO modes, SG alignment/copy cleanup, IV update for CBC/CTR, sysfs fallback and queue_len changes, probe/remove on OMAP2/3/4 pdata including no-AEAD remove, runtime suspend/resume, and AEAD registration through OMAP4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.c -->
