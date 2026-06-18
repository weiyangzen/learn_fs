# subset-b-001228 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.c

## Purpose
This file registers HiSilicon SEC v2/v3 hardware acceleration with the Linux Crypto API for asynchronous skcipher and AEAD transforms. It bridges `crypto_skcipher` and `crypto_aead` requests into SEC queue-manager SQEs, handles DMA mapping of scatterlists or small packet buffers, validates hardware result descriptors, and falls back to software transforms when a request is unsupported, too large, or cannot safely be submitted to hardware.

## Important APIs, Types, And Functions
The exported entry points are `sec_register_to_crypto(struct hisi_qm *qm)` and `sec_unregister_from_crypto(struct hisi_qm *qm)`, called by `sec_main.c` through `hisi_qm_alg_register()` and `hisi_qm_alg_unregister()`. Registration is guarded by `sec_algs_lock` and `sec_available_devs`, so Crypto API algorithms are registered only once while multiple SEC devices may exist.

Core local types include `struct sec_skcipher` and `struct sec_aead`, wrappers around Crypto API algorithm descriptors plus hardware capability masks. `struct sec_req`, `struct sec_ctx`, `struct sec_qp_ctx`, and resource types are defined in `sec.h` and are used here to store per-request SQEs, DMA resources, queue IDs, fallback transforms, and algorithm state.

The key setup path is `sec_skcipher_setkey()` for AES, SM4, 3DES, CTR/CBC/ECB/XTS modes, and `sec_aead_setkey()` for CCM/GCM plus authenc HMAC-SHA CBC modes. `sec_skcipher_soft_crypto()` and `sec_aead_soft_crypto()` are software fallback paths. Descriptor builders are split by algorithm and hardware generation: `sec_skcipher_bd_fill()` and `sec_aead_bd_fill()` build type2 descriptors; `sec_skcipher_bd_fill_v3()` and `sec_aead_bd_fill_v3()` build type3 descriptors. `sec_process()` is the common submit path.

## Control Flow
Crypto API init allocates queue pairs through `sec_create_qps()`, creates per-queue request/resource pools, allocates DMA key/IV/MAC buffers, and chooses type2 or type3 `sec_req_op` callbacks from the QM hardware version. Request submission validates lengths and modes, decides whether pbuffer optimization is usable, assigns a request ID, maps buffers, copies IV state, fills an SQE, and sends it with `hisi_qp_send()`.

Completion flows through `sec_req_cb()` for type2 or `sec_req_cb3()` for type3. Type2 completions recover the request from the SQ message ring/tag index, while type3 completions carry a request pointer in the descriptor tag. Both parse done/ICV/flag/error fields, unmap buffers, update debug counters, and call the skcipher or AEAD callback. Backlogged requests are drained after each completion.

## State And Persistence
State is in memory only. Per-transform state includes keys in coherent DMA buffers, fallback tfms, algorithm mode, request operation table, queue contexts, and preallocated pbuffer/IV/MAC/SGL resources sized by queue depth. Request IDs are tracked by per-QP IDR and freed on completion or fallback cleanup. Global registration state is the `sec_available_devs` counter. Sensitive key buffers are cleared with `memzero_explicit()` before DMA free.

## Dependencies And Integration Points
The file depends on the Linux Crypto API, DMA mapping, IDR, scatterlist helpers, and HiSilicon QM APIs. It uses the shared HiSilicon SGL pool exported from `hisi_acc_sg_buf_map_to_hw_sgl()`. It integrates with `sec_main.c` through algorithm capability bitmaps from `sec_get_alg_bitmap()` and queue allocation from `sec_create_qps()`.

## Risks
The main risks are DMA lifetime errors, request ID leaks on rare failure paths, invalid descriptor bit programming, and fallback behavior mismatch. AEAD has extra risk around CCM IV dimension validation, GCM minimum tag size, MAC extraction/copyback, and decrypt ICV handling. Small-packet pbuffer mode shares one DMA buffer for input/output, so copy sizing must stay consistent with authsize and associated data. Type2/type3 split raises compatibility risk when capability probing or QM version checks are wrong.

## Test Signals
Useful signals are Crypto API self-tests for `ecb/cbc/ctr/xts(aes)`, `cbc/ctr/xts(sm4)`, `ecb/cbc(des3_ede)`, `ccm/gcm(aes)`, `ccm/gcm(sm4)`, and authenc HMAC-SHA CBC algorithms. Exercise zero length, non-block-size CBC, XTS minimum length, oversized input fallback, small pbuffer requests, in-place and out-of-place scatterlists, backlog under full SQ, ICV failure on AEAD decrypt, and hardware v2/v3 descriptor paths. Runtime debug counters `send_cnt`, `recv_cnt`, and `done_flag_cnt` should move consistently with completed requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.h

## Purpose
This header defines the SEC hardware-facing crypto descriptor contract used by `sec_crypto.c`. It contains algorithm, mode, key-size, address-type, and descriptor-type enums plus packed descriptor layouts for type2 and type3 SEC SQEs. It is the bitfield map that lets the Crypto API driver encode skcipher and AEAD operations for different hardware generations.

## Important APIs, Types, And Functions
The externally visible declarations are `sec_register_to_crypto()` and `sec_unregister_from_crypto()`. Core enums include `enum sec_calg` for 3DES/AES/SM4, `enum sec_hash_alg` for HMAC-SHA variants, `enum sec_cmode` for ECB/CBC/CTR/CCM/GCM/XTS, `enum sec_ckey_type`, `enum sec_bd_type`, `enum sec_auth`, `enum sec_cipher_dir`, and `enum sec_addr_type`.

`struct sec_sqe_type2` and `struct sec_sqe` describe the older type2 format nested inside the base SQE. `struct sec_sqe3` describes the newer type3 format with wider tags and rearranged fields. `struct bd_status` is an internal normalized completion view used by `sec_crypto.c` after parsing either descriptor format. Helper structs such as `bd3_auth_ivin`, `bd3_skip_data`, `bd3_stream_scene`, `bd3_no_scene`, `bd3_check_sum`, and `bd3_tls_type_back` model type3 union payloads.

## Control Flow
The header has no executable control flow, but it directly shapes runtime flow because descriptor fill functions in `sec_crypto.c` write these fields, and completion callbacks parse their status fields. Type2 descriptors use the nested `type2` fields under `struct sec_sqe`; type3 descriptors use `struct sec_sqe3` and carry the request pointer in `tag`.

## State And Persistence
There is no runtime state in this header. All state represented by these structs is transient descriptor state in DMA-visible command/completion memory. The layout uses little-endian integer types and packed/aligned attributes where required for hardware ABI stability.

## Dependencies And Integration Points
The header is included by `sec_crypto.c` and relies on kernel integer/endian types. It depends on `struct hisi_qm` being visible to compilation units through included SEC/QM headers. It is tightly coupled to SEC hardware manuals and to the field offsets in `sec_crypto.c`.

## Risks
Descriptor ABI drift is the primary risk. Incorrect bit comments, enum values, packing, or alignment would produce hardware-visible corruption. The two descriptor generations are similar enough that accidental cross-use is plausible, especially for address type, cipher/auth ordering, MAC length, and tag fields.

## Test Signals
Tests should cover both type2 and type3 devices or emulation. Descriptor dumps through QM debugfs, Crypto API known-answer tests, and negative AEAD ICV tests validate that bitfield packing matches hardware expectations. Sparse/endian builds are useful because the header uses explicit little-endian fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_main.c

## Purpose
This file is the PCI and device-management layer for the HiSilicon SEC accelerator. It initializes the QM instance, capabilities, memory, user-domain/SMMU settings, clock gating, RAS/error recovery, debugfs, SR-IOV, runtime PM, and Crypto API registration for PF/VF SEC devices.

## Important APIs, Types, And Functions
Exported helpers include `sec_create_qps()`, `sec_destroy_qps()`, `sec_get_alg_bitmap()`, and `hisi_sec_get_pf_driver()`. Module parameters are `pf_q_num`, `ctx_q_num`, `vfs_num`, and `uacce_mode`; setters validate PF queue count, even context queue count, SR-IOV count, and UACCE mode.

Device initialization is centered on `sec_probe()`, `sec_qm_init()`, `sec_probe_init()`, `sec_pf_probe_init()`, and `sec_set_user_domain_and_cache()`. Hardware bring-up is in `sec_engine_init()`, which disables clock gating before memory init, waits for SEC memory initialization, enables TRNG, configures SVA/prefetch, opens SEC cores from capability bitmaps, enables v2 descriptor checks, sets endian, and re-enables clock gating on newer hardware.

RAS and reset integration are implemented through `sec_err_ini`, with callbacks such as `sec_hw_error_enable()`, `sec_hw_error_disable()`, `sec_get_err_result()`, `sec_dev_is_abnormal()`, `sec_disable_axi_error()`, and `sec_enable_axi_error()`. Debugfs support is created by `sec_debugfs_init()`, `sec_core_debug_init()`, and the `clear_enable`, DFX counter, register dump, diff-reg, and capability-reg files.

## Control Flow
Module init initializes the QM device list, creates the root debugfs directory, and registers a PCI driver. Probe allocates `struct sec_dev`, initializes QM fields based on PF/VF identity, stores capability registers, maps algorithm names, checks whether an IOMMU paging domain is active, performs PF-only hardware init, starts QM, initializes debugfs, adds the device to the QM list, registers algorithms through `sec_crypto.c`, optionally registers UACCE, optionally enables SR-IOV VFs, and initializes PM.

Remove reverses that sequence: PM uninit, wait for tasks, unregister algorithms, remove from list, disable SR-IOV, remove debugfs, stop QM, undo PF resources, and uninit QM. PCI error handlers delegate reset and recovery to common HiSilicon QM handlers with SEC-specific `sec_err_ini` callbacks.

## State And Persistence
Persistent runtime state is device memory only: `struct sec_dev`, embedded `struct hisi_qm`, cached capability tables, debug counters, last DFX register snapshots, `ctx_q_num`, `iommu_used`, and debugfs files. Hardware state includes SEC memory init, SAA/core enable bits, endian mode, SVA prefetch mode, RAS masks, and OOO shutdown settings. No on-disk persistence exists.

## Dependencies And Integration Points
This file depends on PCI, debugfs, IOMMU, PM runtime, UACCE, SR-IOV, and the HiSilicon QM common layer. It integrates with `sec_crypto.c` through `sec_devices.register_to_crypto` and queue allocation. It shares capability and error semantics with other HiSilicon accelerator drivers.

## Risks
Risks include incorrect capability defaults across hardware versions, queue-count module parameters that overcommit hardware, SVA prefetch close/open timeout behavior, RAS masking that suppresses recoverable errors, and cleanup ordering around algorithm unregister versus in-flight queue tasks. PF/VF v1 special casing is fragile because VF queue layout is hard-coded.

## Test Signals
Probe/remove smoke tests should cover PF and VF IDs, v1/v2/v3 capability variants, module parameters, UACCE on/off, SR-IOV enable/disable, runtime suspend/resume, and PCI error injection. Debugfs `cap_regs`, `diff_regs`, and DFX counters should appear for PFs and be cleaned on remove. Crypto API algorithms should register only after QM start and vanish after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sgl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sgl.c

## Purpose
This file provides a shared HiSilicon accelerator helper for converting Linux scatterlists into hardware SGL descriptors stored in preallocated coherent DMA pools. SEC and ZIP use it to avoid allocating descriptor memory per request and to hand hardware a compact DMA address for a list of source or destination buffers.

## Important APIs, Types, And Functions
Exported APIs are `hisi_acc_create_sgl_pool()`, `hisi_acc_free_sgl_pool()`, `hisi_acc_sg_buf_map_to_hw_sgl()`, and `hisi_acc_sg_buf_unmap()`. The hardware layout is `struct hisi_acc_hw_sgl`, with header fields for next pointer and entry counts followed by flexible `struct acc_hw_sge` entries. `struct hisi_acc_sgl_pool` stores up to five coherent memory blocks, count, SGE capacity, and descriptor size.

## Control Flow
Pool creation validates device, count, and SGE count, computes an aligned descriptor size, chooses block sizes up to `PAGE_SIZE << MAX_PAGE_ORDER` capped at 2^31, allocates full blocks plus a remainder block, and stores pool geometry. Mapping first DMA maps the Linux scatterlist, rejects inputs with more mapped entries than the pool SGE count, obtains the indexed hardware SGL from the pool, fills SGE DMA addresses/lengths/page controls, and returns both virtual and DMA addresses. Unmap reverses the scatterlist DMA mapping and clears descriptor fields.

## State And Persistence
State is coherent DMA memory owned by the pool and reused by callers according to a caller-provided index. The helper itself does not track allocations or concurrency; it assumes the caller assigns unique indices and releases mappings. Descriptor contents are cleared on unmap but pool memory persists until `hisi_acc_free_sgl_pool()`.

## Dependencies And Integration Points
The file depends on DMA mapping, scatterlist APIs, and `linux/hisi_acc_qm.h` for public declarations. SEC uses one input and one output pool per QP. ZIP uses a pool sized at twice the queue depth so each request gets separate source and destination hardware SGLs.

## Risks
Because the pool does not internally lock or allocate entries, callers must not reuse the same index concurrently. `entry_sum_in_chain` is set to the pool capacity rather than actual mapped entries, matching hardware expectations but easy to misinterpret. Failure during remainder allocation frees only previously allocated full blocks; this is correct for the current loop but sensitive to future changes. `page_ctrl` stores `sg_virt()` and must not be consumed by hardware as a DMA pointer.

## Test Signals
Exercise pool creation for min/max SGE counts, boundary block counts, invalid counts, scatterlists with too many mapped entries, in-place/unmap paths in SEC and ZIP, and repeated reuse of the same index. DMA debug and KASAN can catch stale mapping and descriptor overrun bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sgl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/Makefile

## Purpose
This Makefile wires the HiSilicon TRNG v2 driver into the kernel build. When `CONFIG_CRYPTO_DEV_HISI_TRNG` is enabled, it builds the module/object named `hisi-trng-v2` from `trng.o`.

## Important APIs, Types, And Functions
There are no C APIs here. The important build variables are `obj-$(CONFIG_CRYPTO_DEV_HISI_TRNG)` and `hisi-trng-v2-objs`.

## Control Flow
Kbuild includes `hisi-trng-v2.o` only when the config symbol is enabled. The composite object consists solely of `trng.o`.

## State And Persistence
No runtime state exists. The file affects build artifacts and module composition only.

## Dependencies And Integration Points
It depends on the enclosing crypto driver Kbuild and the Kconfig symbol for HiSilicon TRNG. It integrates `trng.c` as the implementation unit.

## Risks
The risk is low. A mismatch between object name and module metadata would prevent the driver from building or loading under the expected module name.

## Test Signals
Build with `CONFIG_CRYPTO_DEV_HISI_TRNG=y` and `=m`, and verify that `hisi-trng-v2` is linked and contains `trng.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/trng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/trng.c

## Purpose
This file implements the HiSilicon true random number generator v2 platform driver. It exposes hardware random data through the hwrng framework and, on non-v1 hardware, exposes a Crypto API `stdrng` implementation backed by a hardware/software DRBG register interface.

## Important APIs, Types, And Functions
Key types are `struct hisi_trng`, representing one mapped TRNG device; `struct hisi_trng_list`, the global load-balancing list of devices; and `struct hisi_trng_ctx`, a Crypto API context holding the selected device. The hwrng path uses `hisi_trng_read()`. The Crypto API RNG path uses `hisi_trng_alg` with `hisi_trng_init()`, `hisi_trng_exit()`, `hisi_trng_seed()`, and `hisi_trng_generate()`.

Register helpers include `hisi_trng_set_seed()` to program 48 bytes of seed into 12 seed registers and initialize the DRBG, `hisi_trng_reseed()` to reseed from raw TRNG data after bytes have been generated, and `hisi_trng_get_bytes()` to poll DRBG status, read four 32-bit data registers, copy up to 16 bytes per round, and trigger the next generation.

## Control Flow
Probe allocates `struct hisi_trng`, maps MMIO, initializes locks and version, initializes the global list once, adds the device, optionally registers the Crypto API RNG once using `trng_active_devs`, then registers an hwrng with quality 512. Crypto RNG init chooses the currently least-used TRNG by `ctx_num`, increments its context count, and generation takes the per-device mutex while producing data in chunks up to `SW_MAX_RANDOM_BYTES`. Remove waits until no Crypto API contexts reference the device, then unregisters the Crypto RNG when the last non-v1 device is removed.

## State And Persistence
Runtime state includes the global TRNG device list, active non-v1 device count, per-device context count, MMIO base, hardware version, RNG registration, and `random_bytes` since last seed. There is no persistent storage. Seed material is stack/local data and device registers; the code does not explicitly scrub the temporary reseed buffer.

## Dependencies And Integration Points
The driver depends on ACPI platform enumeration (`HISI02B3`), hwrng, Crypto API RNG internals, MMIO polling, and kernel random headers. It integrates with users through `/dev/hwrng`/hwrng consumers and Crypto API consumers of `stdrng`/`hisi_stdrng`.

## Risks
`hisi_trng_remove()` busy-waits while contexts exist, which can stall module removal. `hisi_trng_init()` assumes the global list is non-empty; a race with remove is mitigated by list locking but depends on registration lifetime. Reseed behavior uses raw TRNG output only after prior generation, so initial `random_bytes = SW_MAX_RANDOM_BYTES` forces first generation through reseed. Poll timeouts return partial hwrng data on raw reads but `-EIO` on DRBG paths.

## Test Signals
Test hwrng reads, Crypto API RNG seed/generate, short seed rejection, large generate split at `SW_MAX_RANDOM_BYTES`, probe/remove with multiple devices, v1 behavior without Crypto API RNG registration, and timeout/error paths via fault injection. Lockdep is useful around list and per-device mutex use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/Makefile

## Purpose
This Makefile builds the HiSilicon ZIP accelerator driver when `CONFIG_CRYPTO_DEV_HISI_ZIP` is enabled. The composite object `hisi_zip.o` contains ZIP device management, Crypto API compression, and DAE support.

## Important APIs, Types, And Functions
There are no runtime APIs in this file. The key Kbuild lines are `obj-$(CONFIG_CRYPTO_DEV_HISI_ZIP) += hisi_zip.o` and `hisi_zip-objs = zip_main.o zip_crypto.o dae_main.o`.

## Control Flow
Kbuild links `zip_main.o`, `zip_crypto.o`, and `dae_main.o` into the single `hisi_zip` driver object when the config symbol is active.

## State And Persistence
No runtime state exists. This file only controls module/object composition.

## Dependencies And Integration Points
The composition means `zip_main.c` can call DAE helpers and register Crypto API operations from `zip_crypto.c` in one module.

## Risks
The risk is mostly build integration. Omitting `dae_main.o` would leave unresolved DAE symbols used by `zip_main.c`; omitting `zip_crypto.o` would remove Crypto API registration callbacks.

## Test Signals
Build as built-in and module with `CONFIG_CRYPTO_DEV_HISI_ZIP`, confirm `hisi_zip.o` links all three objects, and check for unresolved symbols in modpost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/dae_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/dae_main.c

## Purpose
This file adds Data Analytics Engine support to the HiSilicon ZIP driver for hardware that advertises `QM_SUPPORT_DAE`. It initializes DAE memory, appends DAE algorithm names to the UACCE capability string, controls DAE out-of-order AXI shutdown behavior, and folds DAE RAS/error state into ZIP device recovery.

## Important APIs, Types, And Functions
Public functions declared in `zip.h` include `hisi_dae_set_user_domain()`, `hisi_dae_set_alg()`, `hisi_dae_hw_error_enable()`, `hisi_dae_hw_error_disable()`, `hisi_dae_get_err_result()`, `hisi_dae_dev_is_abnormal()`, `hisi_dae_close_axi_master_ooo()`, and `hisi_dae_open_axi_master_ooo()`. `dae_is_support()` gates every operation on the QM capability bit.

`struct hisi_dae_hw_error` and `dae_hw_error[]` map interrupt bits to log messages. Algorithm exposure differs by hardware generation: v5 and later advertise `hashagg`, `udma`, `hashjoin`, and `gather`; earlier supported DAE devices advertise `hashagg`.

## Control Flow
ZIP PF initialization calls `hisi_dae_set_user_domain()` after ZIP cache/user-domain setup. It starts DAE memory initialization and polls a done register. ZIP QM initialization calls `hisi_dae_set_alg()` after setting ZIP algorithms so UACCE users see DAE operations in the same accelerator device. ZIP error callbacks call DAE enable/disable, status, abnormality, and OOO helpers alongside ZIP equivalents.

## State And Persistence
The file stores no private runtime state. It manipulates DAE MMIO registers and appends to `qm->uacce->algs`. Error state lives in hardware status/mask registers and in the common QM error flow.

## Dependencies And Integration Points
It depends on the HiSilicon QM capability model, UACCE algorithm string storage, MMIO polling, and the ZIP module. It is not separately registered; it is linked into `hisi_zip.o`.

## Risks
Risk centers on capability gating and UACCE string length. `hisi_dae_set_alg()` mutates `qm->uacce->algs` using `strcat()` after checking length, so callers must ensure the string is initialized and bounded by `QM_DEV_ALG_MAX_LEN`. DAE error reset decisions can force whole ZIP device recovery when NFE bits are set.

## Test Signals
Test ZIP probe on hardware with and without `QM_SUPPORT_DAE`, UACCE algorithm string contents for pre-v5 and v5, DAE memory-init timeout handling, DAE CE/NFE logging, combined ZIP/DAE recovery result selection, and OOO close/open register polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/dae_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip.h

## Purpose
This header is the shared contract between HiSilicon ZIP device management, Crypto API compression, and DAE support. It defines common driver structures, the ZIP SQE layout, capability table indexes, and cross-file function prototypes.

## Important APIs, Types, And Functions
`struct hisi_zip` embeds `struct hisi_qm`, a PF-only control pointer, and ZIP DFX counters. `struct hisi_zip_dfx` provides `send_cnt`, `recv_cnt`, `send_busy_cnt`, and `err_bd_cnt`. `struct hisi_zip_sqe` maps the 128-byte hardware SQE used by `zip_crypto.c`, including consumed/produced lengths, status, request type, buffer type, source/destination addresses, and tag fields. `enum zip_cap_table_type` indexes stored capability records.

Declared functions connect the module pieces: queue allocation (`zip_create_qps()`), Crypto API registration (`hisi_zip_register_to_crypto()`, `hisi_zip_unregister_from_crypto()`), algorithm capability checking (`hisi_zip_alg_support()`), and DAE helpers.

## Control Flow
The header has no execution, but its declarations define the module graph: `zip_main.c` owns PCI/QM lifecycle and calls into `zip_crypto.c` and `dae_main.c`; `zip_crypto.c` uses `struct hisi_zip_sqe` to submit compression requests; DAE callbacks are invoked from ZIP error and initialization paths.

## State And Persistence
No state is allocated in the header. The structs describe in-memory per-device state and transient hardware SQEs. The DFX counters are atomic runtime state exposed by debugfs.

## Dependencies And Integration Points
It depends on `linux/hisi_acc_qm.h` for QM types and error-result enums. The header is private to the HiSilicon ZIP directory and coordinates all three object files in the composite module.

## Risks
The SQE layout is hardware ABI. Field order and comments must stay aligned with descriptor fill/parsing in `zip_crypto.c`. Capability enum order must match capability table initialization in `zip_main.c`; any drift would cause wrong algorithm registration or debug reporting.

## Test Signals
Build tests catch prototype drift. Runtime tests should verify SQE submission/completion for deflate/lz4, DFX counter exposure, and algorithm filtering from capability table indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_crypto.c

## Purpose
This file registers HiSilicon ZIP hardware as asynchronous compression algorithms for the Crypto API. It supports hardware deflate compression/decompression and lz4 compression, with software fallback for initialization failures and lz4 decompression.

## Important APIs, Types, And Functions
Exported-to-module functions are `hisi_zip_register_to_crypto()` and `hisi_zip_unregister_from_crypto()`. The async compression algorithms are `hisi_zip_acomp_deflate` and `hisi_zip_acomp_lz4`. Internal request state is split across `struct hisi_zip_ctx`, two `struct hisi_zip_qp_ctx` entries for compression and decompression queues, per-queue `struct hisi_zip_req_q` arrays plus bitmaps, and per-request `struct hisi_zip_req`.

Descriptor operations are abstracted by `struct hisi_zip_sqe_ops`, currently implemented by `hisi_zip_ops` for SQE type 3. `hisi_zip_fill_sqe()` writes source/destination addresses, input/output lengths, SGL buffer type, request type, 16K window size, request pointer tag, and SQE type. Completion uses `GET_REQ_FROM_SQE()` to recover the request pointer.

## Control Flow
Algorithm init creates two QPs using `zip_create_qps()`, initializes request queues, creates SGL pools sized at `q_depth << 1`, and sets QP completion callbacks. A compression request allocates a free request ID from the bitmap, maps source and destination scatterlists into hardware SGLs using the shared HiSilicon SGL helper, fills an SQE, and submits it with `hisi_qp_send()`. Completion checks status, unmaps both SGLs, updates `acomp_req->dlen` from produced length, completes the request, and frees the request ID.

If QP creation or resource setup fails in init, the context sets `fallback = true` and init still succeeds. Fallback requests use `ACOMP_FBREQ_ON_STACK()` and call the software Crypto API algorithm. LZ4 decompression always falls back through `hisi_zip_decompress()`.

## State And Persistence
Global algorithm registration is tracked by `zip_algs_lock` and `zip_available_devs`. Per-transform state owns QPs, bitmaps, request arrays, SGL pools, and the fallback flag. Per-device DFX counters count sends, receives, send-busy events, and bad descriptors. No state persists across module unload.

## Dependencies And Integration Points
The file depends on Crypto API `acompress`, HiSilicon QM queue submission, HiSilicon SGL pool helpers, DMA mapping through those helpers, and ZIP capability checks in `zip_main.c`. It registers algorithms only if `hisi_zip_alg_support()` finds the relevant hardware bits.

## Risks
Request pointer tags are split into two 32-bit SQE fields; this assumes pointer round-trip is valid for the target architecture. Request queue exhaustion returns `-EAGAIN`. Hardware status `HZIP_NC_ERR` is treated as non-fatal, so callers must interpret produced data correctly. The fallback path uses stack fallback requests and copies only `dlen`; callback semantics must match the async caller expectation. Resource cleanup must match init failure stages to avoid leaking QPs, bitmaps, or SGL pools.

## Test Signals
Run Crypto API acomp tests for deflate compress/decompress and lz4 compress; check lz4 decompression fallback. Exercise zero or missing src/dst/slen/dlen rejection, request bitmap exhaustion, too many SGL entries via `sgl_sge_nr`, hardware nonzero status, `HZIP_NC_ERR`, and init fallback when QP allocation fails. Debugfs DFX counters should reflect send/receive/busy/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_main.c

## Purpose
This file is the PCI/QM lifecycle, capability, debugfs, RAS, UACCE, SR-IOV, and PM layer for the HiSilicon ZIP accelerator. It initializes compression/decompression hardware cores, exposes capabilities to QM/UACCE, registers Crypto API algorithms through `zip_crypto.c`, and incorporates DAE support from `dae_main.c`.

## Important APIs, Types, And Functions
Public functions are `zip_create_qps()`, `hisi_zip_alg_support()`, and `hisi_zip_get_pf_driver()`. Module parameters include `perf_mode`, `uacce_mode`, `pf_q_num`, and `vfs_num`. Major lifecycle functions are `hisi_zip_probe()`, `hisi_zip_qm_init()`, `hisi_zip_probe_init()`, `hisi_zip_pf_probe_init()`, `hisi_zip_set_user_domain_and_cache()`, and `hisi_zip_remove()`.

Capabilities are described by `zip_basic_cap_info[]` and `zip_cap_query_info[]`; algorithm strings are mapped by `zip_dev_algs[]`. Error handling is supplied through `hisi_zip_err_ini`, including ZIP and DAE error enable/disable, abnormality checks, reset decisions, SVA prefetch open/close, AXI error gating, and last DFX register dumps. Debugfs setup creates control files, per-core register directories, DFX counters, diff-reg dumps, and capability dumps.

## Control Flow
Module init initializes the ZIP QM list, creates a root debugfs directory, and registers a PCI driver. Probe allocates `struct hisi_zip`, initializes QM identity and PF/VF queue fields, caches capability tables, sets supported algorithm strings, appends DAE algorithms when supported, performs PF-only user-domain/cache/core/SVA/DAE init, starts QM, initializes debugfs, adds the device to the QM list, registers Crypto API algorithms with two queue contexts, optionally registers UACCE, optionally enables SR-IOV, and initializes PM.

Hardware setup configures QM user/cache attributes, ZIP port cache/user attributes, optional SVA SSV user bits, prefetch, core enable bitmaps, SQ/CQ writeback, compression performance mode, literal-length behavior, clock gating, and DAE memory. Remove reverses registration and hardware state.

## State And Persistence
State is per-device and in memory: embedded `struct hisi_qm`, PF control object, DFX counters, capability records, debugfs entries, last register snapshots, and module parameter values. Hardware state includes ZIP core enables, cache/user-domain registers, SVA prefetch, RAS masks, OOO shutdown, clock gating, and DAE registers. No durable persistence exists.

## Dependencies And Integration Points
The file depends on PCI, debugfs, PM runtime, UACCE, HiSilicon QM common code, SR-IOV helpers, and DAE/ZIP crypto module-local APIs. It is the integration hub for `zip_crypto.c`, `zip.h`, and `dae_main.c`.

## Risks
Hardware-version capability handling is the main risk. Core counts drive debugfs register bases and last-register snapshot sizing, so bad capability values can misaddress MMIO. ZIP RAS mask registers use inverted interrupt-mask semantics in some paths, which is error-prone. DAE reset results can force ZIP recovery. Initialization logs debugfs failure but continues, so observability may be absent on otherwise working devices.

## Test Signals
Test PF/VF probe/remove, v1 VF queue special casing, v2 SVA user-domain settings, v3+ clock gating and shaper rates, `perf_mode` validation, UACCE on/off, SR-IOV, DAE-supported and DAE-absent hardware, debugfs per-core layout, PCI error injection, runtime PM, and Crypto API algorithm presence filtered by capability bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/img-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/img-hash.c

## Purpose
This file implements the Imagination Technologies MD5/SHA1/SHA224/SHA256 hash accelerator as a platform driver and asynchronous hash provider. Digest requests can be processed by the hardware directly while update/final/import/export flows use software fallback transforms.

## Important APIs, Types, And Functions
Core types are `struct img_hash_dev` for one hardware device, `struct img_hash_ctx` for per-transform state and fallback ahash, `struct img_hash_request_ctx` for per-request digest/DMA/scatterlist state, and global `struct img_hash_drv img_hash` for the device list. Algorithms are registered in `img_algs[]`.

Important functions include `img_hash_probe()` and `img_hash_remove()` for platform lifecycle, `img_register_algs()` and `img_unregister_algs()`, `img_hash_digest()` for hardware digest submission, `img_hash_handle_queue()` for serialized request queueing, `img_hash_hw_init()` and `img_hash_start()` for register programming, `img_hash_write_via_cpu()` and `img_hash_write_via_dma()` for data transfer, `img_hash_dma_task()` and `img_hash_done_task()` tasklets, and `img_irq_handler()` for completion interrupts. Fallback setup is in `img_hash_cra_init()` with `md5-lib`, `sha1-lib`, `sha224-lib`, or `sha256-lib`.

## Control Flow
Probe maps two MMIO resources, requests an IRQ, enables `hash` and `sys` clocks, configures a DMA channel, adds the device to the global list, and registers four ahash algorithms. A digest request selects a device, sets digest flags by digest size, initializes scatterlist walk state, and enqueues on the per-device crypto queue. The queue handler initializes hardware message length and algorithm mode, then chooses DMA for requests at least 64 bytes or CPU writes for smaller requests.

DMA transfer walks one scatterlist segment at a time and rounds each DMA transfer down to a 4-byte multiple because hardware lacks a data-valid mask. Leftover bytes are buffered and prepended to the next transfer or sent by CPU. Interrupts set output-ready and DMA-ready flags and schedule the done tasklet, which unmaps DMA, reads result words in reverse order from the result queue, copies the digest to the caller, completes the request, and advances the queue.

## State And Persistence
Runtime state includes the global device list, per-device spinlock, queue, active request pointer, tasklets, DMA channel, clocks, MMIO bases, and flags. Per-request state tracks digest bytes, sg cursor, offset, bytes sent, temporary buffer, and fallback request. No persistent state exists; hardware is reset per request.

## Dependencies And Integration Points
The driver depends on platform device resources, device tree compatible `img,hash-accelerator`, clk framework, DMAengine, IRQs, scatterlist helpers, and Crypto API ahash internals. It integrates with software hash libraries through fallback transforms.

## Risks
Only `digest` uses hardware; multi-call update/final paths are fallback-only, so performance differs by API usage. Queue handling serializes one request per device. DMA error fallback to CPU is partial and relies on correctly resetting `hdev->err`. `img_hash_write_via_cpu()` appears to set `ctx->bufcnt` from `sg_copy_to_buffer()` and then zero it before transmitting `ctx->buffer`, which is suspicious because the copied byte count is discarded while `ctx->total` is retained. Suspend disables clocks without explicit queue quiescing in this file.

## Test Signals
Run ahash known-answer tests for md5, sha1, sha224, and sha256 using digest, update/final, finup, import/export. Exercise small CPU path, DMA path, unaligned scatterlists, multi-SG leftovers, zero-length digest, DMA channel failure, IRQ error bits, suspend/resume, and concurrent requests to validate queue/backlog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/img-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/Makefile

## Purpose
This Makefile builds Inside Secure crypto accelerator drivers. It selects the Safexcel composite object when `CONFIG_CRYPTO_DEV_SAFEXCEL` is enabled and always descends into the `eip93/` subdirectory for its own Kconfig-controlled build.

## Important APIs, Types, And Functions
There are no runtime APIs. Kbuild variables define `crypto_safexcel.o` and its object list: `safexcel.o`, `safexcel_ring.o`, `safexcel_cipher.o`, and `safexcel_hash.o`. The `obj-y += eip93/` line includes the EIP93 subdirectory in the build traversal.

## Control Flow
Kbuild composes `crypto_safexcel.o` conditionally and visits `eip93/` unconditionally, where `eip93/Makefile` decides whether `crypto-hw-eip93.o` is built.

## State And Persistence
No runtime state exists. The file controls build graph shape only.

## Dependencies And Integration Points
It integrates two Inside Secure driver families under one directory: Safexcel and EIP93. It depends on each subdriver's Kconfig symbols and object lists.

## Risks
The unconditional `obj-y += eip93/` is safe because the subdirectory has its own config guard, but build errors in the subdirectory can still affect all builds that traverse it. Object-list drift would cause missing symbols or dead code.

## Test Signals
Build with Safexcel on/off and EIP93 on/off, both built-in and modular, and confirm modpost has no unresolved symbols and expected modules are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Kconfig

## Purpose
This Kconfig entry exposes the EIP93 hardware crypto accelerator driver. It controls whether the EIP93 module is built and pulls in the Crypto API primitives required by its cipher, AEAD, and hash implementations.

## Important APIs, Types, And Functions
The symbol is `CRYPTO_DEV_EIP93`, a tristate prompt described as support for EIP93 crypto hardware accelerators. It depends on `SOC_MT7621 || ARCH_AIROHA || ECONET || COMPILE_TEST`. It selects AES and DES crypto libraries, skcipher, AEAD, authenc, MD5, SHA1, and SHA256 support.

## Control Flow
There is no executable flow. Build-time configuration presents the option only on supported SoCs or compile-test builds. When enabled, `eip93/Makefile` builds the composite EIP93 driver.

## State And Persistence
No runtime state exists. The Kconfig state persists only in the kernel configuration.

## Dependencies And Integration Points
The selected Crypto API dependencies match the algorithms described in the help text: AES ECB/CBC/CTR, DES/3DES ECB/CBC, and AEAD authenc HMAC/cipher combinations. The SoC dependencies tie the driver to MediaTek/Airoha/Econet platforms while allowing broader compile coverage.

## Risks
Over-selecting crypto primitives can enlarge builds, while under-selecting would break link or runtime registration. The help text says "EIP93 have" and "this provide", but that is documentation quality rather than behavior.

## Test Signals
Kconfig tests should verify visibility under supported SoCs and `COMPILE_TEST`, dependency selection, built-in and module configurations, and allnoconfig/allmodconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Makefile

## Purpose
This Makefile builds the EIP93 hardware crypto accelerator as a composite object when `CONFIG_CRYPTO_DEV_EIP93` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. Kbuild creates `crypto-hw-eip93.o` from `eip93-main.o`, `eip93-common.o`, `eip93-cipher.o`, `eip93-aead.o`, and `eip93-hash.o`.

## Control Flow
The first line conditionally adds the composite object to the build. Subsequent `crypto-hw-eip93-y += ...` lines list mandatory objects for the composite driver.

## State And Persistence
No runtime state exists. This file only affects kernel build artifacts.

## Dependencies And Integration Points
The object split indicates major implementation areas: main platform/device code, shared helpers, skcipher, AEAD, and hash support. It is included from the parent Inside Secure Makefile.

## Risks
Object ordering and completeness matter for link success. If a new algorithm file is added without updating this list, the Kconfig symbol may enable an incomplete driver.

## Test Signals
Build `CONFIG_CRYPTO_DEV_EIP93=y` and `=m`, inspect that the resulting object/module contains all five implementation units, and run modpost for unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Makefile -->
