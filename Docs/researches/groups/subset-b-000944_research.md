# Research: subset-b-000944

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/twofish_common.c -->
# sources/distributed-fs/ceph-client/crypto/twofish_common.c

## Purpose
This file provides the shared Twofish key schedule used by both generic C and architecture-specific cipher implementations. It owns the precomputed q permutations, MDS tables, finite-field exponent tables, key-dependent S-box generation, whitening subkey generation, and round subkey generation. The exported entry points are `__twofish_setkey()` for direct context setup and `twofish_setkey()` for the legacy `crypto_tfm` cipher API.

## Important APIs, Types, And Functions
The important external type is `struct twofish_ctx` from `<crypto/twofish.h>`, with `s`, `w`, and `k` arrays populated by the key schedule. `__twofish_setkey()` validates only that `key_len` is a multiple of 8, then handles the 16, 24, and 32 byte Twofish key sizes through separate macro paths. `twofish_setkey()` is a thin adapter using `crypto_tfm_ctx()`. The `CALC_S`, `CALC_SB_*`, and `CALC_K*` macros encode most of the algorithm and are coupled tightly to the table layout.

## Control Flow
Setup computes RS-derived S-vector bytes from the raw key, conditionally extending them for 192-bit and 256-bit keys. It then fills all four key-dependent S-box tables for 256 entries and computes eight whitening words plus 32 round subkeys. The 128-, 192-, and 256-bit branches differ by q-table depth and by which key bytes feed the h-function.

## State, Dependencies, Integration, Risks, And Tests
The only persistent state is the caller-owned `twofish_ctx`; all other state is static read-only tables or stack temporaries. It integrates with the kernel CryptoAPI and is consumed by `twofish_generic.c` and accelerated Twofish implementations. The main risks are table/macro transcription errors, accepting unsupported 8-byte multiples if callers bypass CryptoAPI min/max key checks, and side-channel exposure from key-dependent table lookups. Test signals are CryptoAPI twofish known-answer tests for 128/192/256-bit keys, invalid key length tests, module load/unload, and cross-comparison with accelerated implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/twofish_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/twofish_generic.c -->
# sources/distributed-fs/ceph-client/crypto/twofish_generic.c

## Purpose
This file registers the generic C Twofish block cipher implementation with the kernel CryptoAPI. It supplies single-block encrypt and decrypt functions for the algorithm name `twofish` and driver name `twofish-generic`.

## Important APIs, Types, And Functions
The `crypto_alg alg` structure advertises block size `TF_BLOCK_SIZE`, context size `sizeof(struct twofish_ctx)`, key size bounds from `<crypto/twofish.h>`, `twofish_setkey()`, and local `twofish_encrypt()`/`twofish_decrypt()` callbacks. `G1`, `G2`, `ENCROUND`, `DECROUND`, `ENCCYCLE`, and `DECCYCLE` implement the round function over precomputed context tables. `INPACK` and `OUTUNPACK` combine little-endian unaligned word access with input/output whitening.

## Control Flow
Encryption reads four 32-bit words, applies whitening, executes eight cycles containing 16 Feistel rounds, then writes the swapped output words with output whitening. Decryption mirrors the process by reading the ciphertext in the post-encryption word order, running cycles 7 down to 0 with inverse rotations/subkey usage, and outputting the original word order.

## State, Dependencies, Integration, Risks, And Tests
State lives only in `struct twofish_ctx`, which is initialized by `twofish_common.c`. The module uses unaligned access helpers, bit rotations, and CryptoAPI registration. Risks include macro maintenance mistakes, endian regressions, and timing leakage from S-box table indexing. Test signals are CryptoAPI self-tests, encrypt/decrypt round-trip vectors, in-place operation checks, unaligned input/output checks, and module alias lookup for `twofish` and `twofish-generic`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/twofish_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/wp512.c -->
# sources/distributed-fs/ceph-client/crypto/wp512.c

## Purpose
This file implements Whirlpool hashing for the shash API and registers `wp512`, `wp384`, and `wp256`. The shorter variants reuse the full Whirlpool transform and truncate the 512-bit digest.

## Important APIs, Types, And Functions
`struct wp512_ctx` stores a 256-bit bit-length counter and eight 64-bit chaining words. `wp512_process_buffer()` is the core 10-round Whirlpool block transform using the `C0` through `C7` T-tables and round constants. `wp512_init()`, `wp512_update()`, and `wp512_finup()` implement shash lifecycle; `wp384_finup()` and `wp256_finup()` truncate the full digest. The `wp_algs` array registers all three algorithms with `CRYPTO_AHASH_ALG_BLOCK_ONLY`.

## Control Flow
`update()` processes only whole 64-byte blocks and returns the remainder length to the block-only shash wrapper. `finup()` adds remaining bit length, pads with `0x80`, zero-fills to the 32-byte length trailer, processes the final block or blocks, clears the stack buffer, and emits big-endian digest words. The transform initializes round key and state from the current hash and block, iterates key schedule and cipher state rounds, then applies the Miyaguchi-Preneel feed-forward.

## State, Dependencies, Integration, Risks, And Tests
Digest state is per shash descriptor and not persisted outside the caller's context. The implementation depends on unaligned big-endian helpers, `crypto_register_shashes()`, and table correctness. `__no_kmsan_checks` marks the transform for sanitizer behavior. Risks include length accounting mistakes, truncation regressions, table corruption, and non-constant-time table lookups. Test signals are Whirlpool known-answer vectors for empty, partial, one-block, and multi-block messages; digest truncation vectors; shash finup/update equivalence; and module aliases `wp512`, `wp384`, and `wp256`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/wp512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xcbc.c -->
# sources/distributed-fs/ceph-client/crypto/xcbc.c

## Purpose
This file implements the `xcbc(...)` keyed-hash template for 16-byte block ciphers. It turns a child `crypto_cipher` into an XCBC-MAC shash instance.

## Important APIs, Types, And Functions
`struct xcbc_tfm_ctx` stores the spawned child cipher and two derived finalization constants. `crypto_xcbc_digest_setkey()` derives K1, K2, and K3 by encrypting fixed 0x01, 0x02, and 0x03 blocks, then rekeys the child with K1. `crypto_xcbc_digest_init()`, `crypto_xcbc_digest_update()`, and `crypto_xcbc_digest_finup()` implement CBC-MAC chaining and final block handling. `xcbc_create()` validates the shash template request and requires a 16-byte child block size.

## Control Flow
Initialization zeroes the previous-block state. Update XORs each full block into the state and encrypts it in place, returning any tail length to the block-only shash wrapper. Finalization XORs the supplied final bytes, applies `0x80` padding and K3 for a partial block or K2 for a full block, then encrypts once to produce the MAC.

## State, Dependencies, Integration, Risks, And Tests
Per-transform state is the child cipher and derived constants; per-request state is the previous block stored in `descsize`. It integrates through the CryptoAPI template registry and imports `CRYPTO_INTERNAL`. Risks include relying on block-only callers to avoid mid-stream partial updates, missing zeroization for derived stack key material, and incorrect child algorithms being rejected only by block size. Test signals include AES-XCBC known-answer vectors, exact-full-block versus partial-final tests, invalid child block size tests, and template lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xcbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xctr.c -->
# sources/distributed-fs/ceph-client/crypto/xctr.c

## Purpose
This file implements the `xctr(...)` skcipher template, a CTR-like XOR-counter mode used by HCTR2. It encrypts `IV XOR little-endian counter` rather than `IV + counter`.

## Important APIs, Types, And Functions
`crypto_xctr_crypt()` is both encrypt and decrypt because the mode is a stream cipher. `crypto_xctr_crypt_segment()` handles out-of-place full blocks, `crypto_xctr_crypt_inplace()` handles in-place full blocks with an aligned temporary keystream buffer, and `crypto_xctr_crypt_final()` handles the final partial block. `crypto_xctr_create()` builds the skcipher instance and restricts child ciphers to 16-byte blocks.

## Control Flow
The skcipher walk is configured with `chunksize` equal to the child block size so partial blocks appear only at the end. For each block, the code XORs the low 32 bits of the IV with a little-endian block counter, encrypts the modified IV, XORs the keystream with input, restores the IV by XORing the same counter again, and increments the counter. The byte counter tracks continuity across walk segments.

## State, Dependencies, Integration, Risks, And Tests
The request IV is mutated temporarily but restored after each block, so no persistent counter state remains after completion. Dependencies are skcipher template helpers, simple cipher spawns, and CryptoAPI walk helpers. Risks include 32-bit block counter wrap for very large requests, IV restoration bugs across partial/error paths, and the hard-coded 16-byte limitation. Test signals are HCTR2/XCTR vectors, segmented scatterlist tests, in-place/out-of-place parity, partial-tail tests, and invalid child blocksize tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xts.c -->
# sources/distributed-fs/ceph-client/crypto/xts.c

## Purpose
This file implements the `xts(...)` skcipher template for IEEE 1619 XTS mode. It composes an ECB-capable data cipher with a raw block cipher for tweak generation.

## Important APIs, Types, And Functions
`struct xts_tfm_ctx` stores the child skcipher and tweak cipher. `xts_setkey()` verifies and splits the key into data and tweak halves. `xts_xor_tweak_pre()` and `xts_xor_tweak_post()` apply GF(2^128) tweak masks before and after child encryption/decryption. `xts_cts_final()` handles ciphertext stealing for non-block-multiple lengths. `xts_create()` handles template instantiation, including legacy `ecb(...)` name mangling and tweak cipher lookup.

## Control Flow
Each request encrypts the IV with the tweak key to get `T`, XORs each block with successive `T` values, runs the ECB child over all full blocks, then XORs tweaks again. If there is a partial final block, the code stops near the last two blocks and performs ciphertext stealing through a temporary two-block scatterlist view and a subrequest. Async child completions resume in `xts_encrypt_done()` or `xts_decrypt_done()`.

## State, Dependencies, Integration, Risks, And Tests
Persistent transform state is two spawned cipher handles; per-request state includes the current tweak, tail scatterlist, and embedded subrequest. Dependencies include `xts_verify_key()`, GF128 helpers, scatterwalk, DRM-independent CryptoAPI skcipher infrastructure, and the `ecb` template soft dependency. Risks include CTS corner cases, async completion ordering, key-half validation, alignment requirements, and name-mangling behavior. Test signals are XTS-AES known-answer vectors, partial-sector ciphertext-stealing vectors, async child tests, minimum-length rejection, and same-key-half rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xxhash_generic.c -->
# sources/distributed-fs/ceph-client/crypto/xxhash_generic.c

## Purpose
This file exposes the kernel `lib/xxhash.c` 64-bit non-cryptographic hash through the shash API as `xxhash64` and `xxhash64-generic`.

## Important APIs, Types, And Functions
`struct xxhash64_tfm_ctx` stores the optional 64-bit seed. `struct xxhash64_desc_ctx` stores streaming `xxh64_state`. `xxhash64_setkey()` accepts exactly eight little-endian seed bytes. `xxhash64_init()`, `xxhash64_update()`, and `xxhash64_final()` implement streaming shash operation, while `xxhash64_digest()` uses the one-shot `xxh64()` helper.

## Control Flow
Setkey initializes the transform seed when provided. Streaming users reset descriptor state from that seed, feed arbitrary byte ranges through `xxh64_update()`, and emit the digest as little-endian. One-shot users bypass descriptor accumulation and hash the full input directly with the transform seed.

## State, Dependencies, Integration, Risks, And Tests
State is split between per-transform seed and per-request streaming state. The algorithm is marked `CRYPTO_ALG_OPTIONAL_KEY`, so the default zero seed is valid. Dependencies are `<linux/xxhash.h>`, shash registration, and unaligned little-endian helpers. Risks are misuse as a cryptographic hash, seed-endian mismatch, and divergence between streaming and one-shot paths. Test signals are xxHash64 reference vectors, optional-key behavior, invalid key length, and streaming versus digest equivalence over split inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/xxhash_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/zstd.c -->
# sources/distributed-fs/ceph-client/crypto/zstd.c

## Purpose
This file registers Zstandard compression as a CryptoAPI acomp algorithm named `zstd` and `zstd-generic`. It wraps kernel zstd compression/decompression streams and scatterlist walking.

## Important APIs, Types, And Functions
`struct zstd_ctx` owns a compression context pointer, decompression context pointer, zstd parameters, and a flexible workspace. `zstd_alloc_stream()` sizes a shared workspace for both cstream and dstream use at default level 3 and max window log 18. `zstd_compress()` and `zstd_decompress()` implement scatterwalk streaming, with `zstd_compress_one()` and `zstd_decompress_one()` fast paths for fully contiguous buffers.

## Control Flow
Algorithm initialization lazily allocates shared acomp streams under `zstd_stream_lock`. Each request locks a stream in bottom-half-safe context, initializes the appropriate zstd stream in the workspace, walks source and destination segments, updates `req->dlen` to total output on success, and resets it to zero on error. Compression flushes after each source segment and ends the stream after input exhaustion; decompression loops until all source data is consumed.

## State, Dependencies, Integration, Risks, And Tests
Persistent state is held in the global stream pool, while each stream context owns reusable workspace allocated with `kvmalloc_flex()`. Dependencies include kernel zstd APIs, acomp internals, scatterwalk, vmalloc, and the CryptoAPI virtual-buffer request flag. Risks include destination exhaustion, workspace sizing drift with zstd API changes, noncoherent streaming assumptions, and serialized throughput due to limited stream pool availability. Test signals are acomp compression/decompression round trips, fragmented scatterlists, too-small destination buffers, corrupt input, large-window boundary inputs, and module unload freeing streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/zstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/Kconfig

## Purpose
This file is the top-level Linux kernel `Device Drivers` Kconfig menu for the source tree. It orders and includes subsystem-specific Kconfig files, including the acceleration framework.

## Important APIs, Types, And Functions
There are no C APIs. The important constructs are `menu "Device Drivers"`, `source` statements, and `config PC104`. The acceleration integration point is `source "drivers/accel/Kconfig"`, placed after video/media and before sound/HID/USB-related subsystems.

## Control Flow
Kconfig evaluation enters the Device Drivers menu, presents `PC104` when applicable, and recursively includes driver subsystem menus in the order listed. The file acts as a dependency graph root rather than executable code.

## State, Dependencies, Integration, Risks, And Tests
State is Kconfig selection state persisted in generated `.config` files. Dependencies are textual paths relative to the kernel source root. Integration risk is mostly ordering and missing-source breakage: moving or deleting a sourced file breaks menu construction, and subsystem order can affect symbol visibility/readability. Test signals are `make olddefconfig`, `make menuconfig`, `scripts/kconfig/conf`, and ensuring `CONFIG_DRM_ACCEL` appears when `DRM` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/Makefile

## Purpose
This is the top-level kernel drivers build Makefile. It maps Kconfig symbols to driver subdirectories and defines the broad build order for built-in and modular driver objects.

## Important APIs, Types, And Functions
There are no runtime APIs. The core interface is kbuild syntax: `obj-y` for always-descended directories and `obj-$(CONFIG_...)` for conditional descent. The acceleration integration point is `obj-$(CONFIG_DRM_ACCEL) += accel/`. The file also includes subsystem ordering comments for dependencies like GPIO after pinctrl, DMA early, and GPU after char/IOMMU.

## Control Flow
During kbuild, the top-level build system expands enabled `obj-*` entries and descends into selected directories. Built-in order matters for initcall/link ordering and for availability of infrastructure expected by later subsystems.

## State, Dependencies, Integration, Risks, And Tests
State is build graph state derived from `.config`. Dependencies are directory names and Kconfig symbols. Risks include incorrect conditional symbols preventing driver compilation, ordering regressions, and typoed directories. Test signals are `make drivers/`, allmodconfig/allnoconfig coverage, and confirming `drivers/accel/` is built only with `CONFIG_DRM_ACCEL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/accel/Kconfig

## Purpose
This file defines the compute acceleration driver menu under DRM. It introduces `CONFIG_DRM_ACCEL`, the framework gate for accelerator devices exposed separately from GPUs.

## Important APIs, Types, And Functions
The key symbol is `menuconfig DRM_ACCEL`, a boolean visible only within `if DRM`. Its help text explains `/dev/accel/accel*` device exposure and shared DRM infrastructure. It sources vendor/device submenus including AMD XDNA, Ethos-U, habanalabs, IVPU, QAIC, and Rocket.

## Control Flow
If `CONFIG_DRM` is enabled, users can enable the compute acceleration framework and then select individual accelerator drivers from the sourced submenus. If DRM is disabled, this entire menu is omitted.

## State, Dependencies, Integration, Risks, And Tests
State is Kconfig selection propagated to `drivers/accel/Makefile`. Dependencies include DRM and all sourced vendor Kconfig paths. Risks are hiding accelerator drivers unintentionally behind DRM, missing sourced files, or help text drifting from device-node behavior. Test signals include menu visibility with DRM on/off and build coverage for each sourced driver symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/Makefile

## Purpose
This kbuild file maps accelerator driver Kconfig symbols to vendor subdirectories.

## Important APIs, Types, And Functions
The key entries are `obj-$(CONFIG_DRM_ACCEL_AMDXDNA) += amdxdna/` plus corresponding entries for Arm Ethos-U, habanalabs, IVPU, QAIC, and Rocket. There is no runtime code.

## Control Flow
kbuild descends only into directories whose config symbols are enabled. The parent `drivers/Makefile` includes this directory when `CONFIG_DRM_ACCEL` is enabled.

## State, Dependencies, Integration, Risks, And Tests
State is the build graph derived from `.config`. Integration risk is direct: a wrong symbol or path silently excludes an accelerator driver from builds. Test signals are allmodconfig coverage, per-driver `M=drivers/accel/<driver>` builds, and checking that `CONFIG_DRM_ACCEL_AMDXDNA=m` produces `amdxdna.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Kconfig

## Purpose
This file defines the AMD XDNA accelerator driver option for AMD AI Engine NPUs integrated into client CPUs.

## Important APIs, Types, And Functions
The key symbol is `CONFIG_DRM_ACCEL_AMDXDNA`, a tristate named "AMD AI Engine". It depends on `AMD_IOMMU`, `DRM_ACCEL`, `PCI`, `HAS_IOMEM`, and `X86_64`, and selects `DRM_SCHED`, `DRM_GEM_SHMEM_HELPER`, `FW_LOADER`, and `HMM_MIRROR`.

## Control Flow
When dependencies are met, the user can build the driver built-in or as module `amdxdna`. Selected helper symbols ensure scheduler, GEM shared-memory, firmware loading, and HMM mirror support are available.

## State, Dependencies, Integration, Risks, And Tests
State is Kconfig selection. Runtime integration depends on PCI discovery, AMD IOMMU/PASID/IOMMU paths, firmware loading, DRM scheduler, and HMM invalidation support. Risks include under-specified dependencies causing compile failures on unsupported architectures and over-strict dependencies hiding valid hardware. Test signals include Kconfig dependency matrix builds and verifying module build/load on supported AMD Ryzen AI platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Makefile

## Purpose
This Makefile defines the object list for the AMD XDNA driver module.

## Important APIs, Types, And Functions
`amdxdna-y` lists the compilation units linked into `amdxdna.o`, including AIE2 context, error, message, PCI, PM, PSP, SMU, solver, GEM, IOMMU, mailbox, sysfs, user-buffer, and NPU register files. `obj-$(CONFIG_DRM_ACCEL_AMDXDNA) = amdxdna.o` connects the object to the Kconfig symbol.

## Control Flow
kbuild compiles each listed `.o` and links them into a single built-in or module object depending on `CONFIG_DRM_ACCEL_AMDXDNA`.

## State, Dependencies, Integration, Risks, And Tests
Build state is the object list. Risks include missing new source files, stale deleted file references, and link-order issues for init/exit or exported helper dependencies. Test signals are `make M=drivers/accel/amdxdna`, modpost symbol checks, and verifying that all expected feature files are included in `amdxdna.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_ctx.c

## Purpose
This file manages AMD XDNA AIE2 hardware contexts, DRM scheduler jobs, command submission, resource allocation, firmware context restart, debug-buffer commands, and HMM invalidation recovery.

## Important APIs, Types, And Functions
Public entry points include `aie2_hwctx_init()`, `aie2_hwctx_fini()`, `aie2_hwctx_suspend()`, `aie2_hwctx_resume()`, `aie2_hwctx_config()`, `aie2_hwctx_sync_debug_bo()`, `aie2_cmd_submit()`, and `aie2_hmm_invalidate()`. `struct aie2_ctx_health` packages timeout health for userspace command errors. The scheduler backend uses `aie2_sched_job_run()`, `aie2_sched_job_free()`, and `aie2_sched_job_timedout()`.

## Control Flow
Context initialization pins the client heap, allocates command-list BOs, initializes DRM scheduler/entity state, computes candidate column starts, resumes the device, allocates AIE resources or temporal-only firmware context, maps host heap to firmware, creates a syncobj, and releases PM usage. Command submission obtains a job semaphore, initializes a DRM sched job, locks BO reservations, repopulates invalid HMM mappings if needed, arms the scheduler job, adds reservation fences, assigns a sequence number, pushes the job, and appends the output fence to the context syncobj. Job execution sends driver commands, chain commands, forced command-list single commands, or legacy execbuf messages. Timeout handling queries app health when supported, stops/destroys the firmware context, restarts it, and marks command health.

## State, Dependencies, Integration, Risks, And Tests
Persistent state includes `hwctx->priv`, pinned heap BO, command BO ring, mailbox channel, syncobj, column list, CU config copy, sequence counters, job semaphores, and submitted/free counters. Dependencies include DRM scheduler/syncobj/GEM reservations, dma fences, XRS resource solver, AMD XDNA GEM and mailbox helpers, PM locks, HMM/MMU interval notifiers, and AIE2 firmware message functions. Risks are deadlocks around `dev_lock`, `io_lock`, reservation locks, and notifier locks; lost semaphore/fence references on error paths; restart failure after timeout; HMM retry loops; and stale debug BO ownership. Test signals include context create/destroy under stress, suspend/resume with pending jobs, timeout recovery with app health, HMM invalidation during submit, syncobj sequence waits, command-list and legacy execution paths, and debug BO attach/sync/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_error.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_error.c

## Purpose
This file handles asynchronous AIE2 firmware error events. It allocates DMA-visible event buffers, registers them with firmware, decodes AIE event payloads into AMD XDNA error categories, stores the latest error, and exposes it to userspace.

## Important APIs, Types, And Functions
`struct async_events` owns an ordered workqueue, a DMA buffer, and one `struct async_event` per AIE column. `struct aie_error` and `struct aie_err_info` describe firmware error payloads. `aie_get_error_category()` maps module/row/event IDs through lookup tables. Public functions are `aie2_error_async_events_alloc()`, `aie2_error_async_events_free()`, and `aie2_get_array_async_error()`.

## Control Flow
Allocation creates the event container, allocates one large message buffer sized as `ASYNC_BUF_SIZE * total_col`, creates an ordered workqueue, initializes per-column event structures, and registers each buffer with firmware. Firmware callbacks read status/type from BAR data, use a write memory barrier so status is observed last, and queue worker processing. The worker validates error counts, logs payloads, builds an error-column bitmap, updates `ndev->last_async_err`, and re-registers the event buffer for future firmware notifications.

## State, Dependencies, Integration, Risks, And Tests
Persistent state is `ndev->async_events` and `ndev->last_async_err`. Dependencies include message buffer allocation/free from `aie2_message.c`, mailbox async registration, DMA cache flushing, DRM logging, workqueues, `dev_lock`, and userspace copy helpers. Risks include firmware-provided count overflow, assuming fewer than 32 columns for bitmaps, races during free versus queued work, noncoherent DMA cache handling, and unknown event IDs reducing diagnostic quality. Test signals are synthetic async event injection, oversized `err_cnt` validation, module/row mapping checks, free during active events, userspace query of last error, and repeated event re-registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_message.c -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_message.c

## Purpose
This file is the AIE2 firmware mailbox marshalling layer. It sends management messages, creates and destroys firmware contexts and mailbox channels, queries metadata/telemetry/status, configures CUs and debug buffers, and converts userspace command buffers into firmware execute messages.

## Important APIs, Types, And Functions
Management APIs include `aie2_suspend_fw()`, `aie2_resume_fw()`, runtime config get/set, PASID assignment, metadata/version queries, context create/destroy, host-buffer mapping, status/telemetry queries, async-event registration, and app-health query. Execution APIs include `aie2_execbuf()`, `aie2_cmdlist_multi_execbuf()`, `aie2_cmdlist_single_execbuf()`, `aie2_sync_bo()`, and `aie2_config_debug_bo()`. `aie2_msg_init()` selects legacy or NPU command-list operation tables based on firmware feature bits.

## Control Flow
Synchronous management commands use `aie2_send_mgmt_msg_wait()`, which tears down the management channel on timeout and maps non-success firmware status to `-EINVAL`. Context creation sends `CREATE_CONTEXT`, builds x2i/i2x mailbox resource descriptors from firmware queue addresses, maps an MSI-X vector, starts a mailbox channel, and rolls back by destroying the firmware context on failure. Command execution either sends a direct CU/DPU request or fills a reusable device command buffer with one or more command-list slots, flushes it for device access, builds a chain request, and sends it asynchronously through the context channel.

## State, Dependencies, Integration, Risks, And Tests
State touched here includes management/context mailbox channels, firmware context IDs, hardware context counts, selected exec message ops, command-list BO contents, and temporary DMA buffers used for queries. Dependencies include mailbox helpers, PCI IRQ mapping, GEM lookup/vmap/device addresses, DMA/IOMMU message allocation, DRM cache flushing, userspace copy, bitfield packing, and protocol structs from `aie2_msg_priv.h`. Risks include command payload size validation, leaked GEM references or vmaps on early returns, firmware protocol drift, noncoherent DMA synchronization, channel teardown during concurrent use, and inconsistent legacy versus NPU command formats. Test signals include protocol version/metadata queries, context create rollback failures, CU config validation, multi-command chain error indices, NPU preempt/ELF feature gating, telemetry/status buffer sizing, app health on timeout, and management timeout recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_msg_priv.h -->
# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_msg_priv.h

## Purpose
This private header defines the AIE2 firmware mailbox protocol used by the AMD XDNA driver. It centralizes opcodes, status values, packed request/response layouts, command-list slot formats, telemetry/error structures, and app-health reports.

## Important APIs, Types, And Functions
`enum aie2_msg_opcode` covers XRT-style execution commands, driver management commands, async event registration, app health, and protocol versioning. `enum aie2_msg_status` partitions AIE, management ERT, app ERT, and NPU RTOS status codes. Important structs include context create/destroy, queue pair descriptions, telemetry/status queries, execute-buffer and DPU requests, CU config, sync BO, debug BO config, async event messages, command-chain slots, and `struct app_health_report`.

## Control Flow
The header has no executable flow, but its packed layouts determine how `aie2_message.c`, `aie2_ctx.c`, and `aie2_error.c` communicate with firmware. Flexible-array command slots carry variable argument counts, while wrapper requests pass device addresses and sizes for firmware-readable buffers.

## State, Dependencies, Integration, Risks, And Tests
The protocol describes persistent firmware-side state such as context IDs, queue pairs, CUs, debug BO registrations, async event buffers, and app health. It depends on fixed-width UAPI-style integer sizes, `__packed`, `GENMASK`, and size constants such as `SZ_4K` and `SZ_8K`. Risks include ABI drift with firmware, alignment/packing mismatches, endianness assumptions, flexible-array size miscalculation, and insufficient reserved-field validation. Test signals include compile-time struct-size checks against firmware specs, mailbox round-trip tests for every opcode, command slot boundary tests, and compatibility tests across firmware versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_msg_priv.h -->
