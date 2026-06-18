# Research: subset-b-001231

This grouped report covers Intel crypto driver files under `sources/distributed-fs/ceph-client/drivers/crypto/intel`. Each section is delimited for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.c

## Purpose
This file implements optional debugfs statistics for the Intel IAA crypto compression driver. It tracks global compression/decompression counters, completion error counters, per-IAA-device counters, and per-workqueue counters, then exposes them through debugfs files under `iaa_crypto`.

## Important APIs, Types, And Functions
- Global update APIs: `update_total_comp_calls()`, `update_total_comp_bytes_out()`, `update_total_decomp_calls()`, `update_total_sw_decomp_calls()`, `update_total_decomp_bytes_in()`, and the three `update_completion_*_errs()` helpers increment `atomic64_t` global counters.
- Workqueue update APIs: `update_wq_comp_calls()`, `update_wq_comp_bytes()`, `update_wq_decomp_calls()`, and `update_wq_decomp_bytes()` use `idxd_wq_get_private()` to find the driver-private `struct iaa_wq`, then update both the workqueue and owning `struct iaa_device`.
- Debugfs show functions: `global_stats_show()` prints global atomics; `wq_stats_show()` takes `iaa_devices_lock`, iterates `iaa_devices`, and calls `device_stats_show()`/`wq_show()`.
- Reset path: `iaa_crypto_stats_reset()` clears global counters and, while holding `iaa_devices_lock`, clears each device and workqueue counter.
- Lifecycle: `iaa_crypto_debugfs_init()` creates `global_stats`, `wq_stats`, and `stats_reset`; `iaa_crypto_debugfs_cleanup()` removes the whole debugfs subtree.

## Control Flow
Fast-path compression/decompression code calls the update helpers directly. Debugfs reads enter `single_open()`, use `seq_file` output helpers, and return a point-in-time atomic snapshot. Writing `stats_reset` through the `DEFINE_DEBUGFS_ATTRIBUTE` write callback clears all visible counters.

## State And Persistence
State is in static `atomic64_t` counters plus counters embedded in runtime `iaa_device` and `iaa_wq` objects. It is kernel-memory-only diagnostic state and is lost on module unload/reload. Per-device traversal is protected by `iaa_devices_lock`; individual counters use atomics and can change while a debugfs read is in progress.

## Dependencies And Integration Points
The file depends on the IAA crypto driver's internal `iaa_crypto.h` structures, IDXD workqueue private data, the global `iaa_devices` list and lock, Linux debugfs, and `seq_file`. It integrates with the header `iaa_crypto_stats.h`, which compiles these functions out when stats support is disabled.

## Risks
- `iaa_crypto_debugfs_init()` does not check each debugfs creation return value; missing files are not reported.
- Reset races are intentionally weak: fast-path updates can occur during or immediately after reset, so reset is not a strict quiescent boundary.
- Workqueue update helpers assume `idxd_wq_get_private()` returns a valid `struct iaa_wq` with a valid owning `iaa_device`.

## Test Signals
- With `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`, exercise IAA compression/decompression and verify counter increments in `/sys/kernel/debug/iaa_crypto/global_stats` and `wq_stats`.
- Trigger software fallback decompression and error paths, then verify the matching counters.
- Write to `stats_reset` and confirm global, device, and workqueue counters return to zero without warnings while I/O is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.h

## Purpose
This header is the compile-time interface for optional IAA crypto statistics. It declares debugfs lifecycle and counter update functions when `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` is enabled, and otherwise replaces every function with an empty inline stub.

## Important APIs, Types, And Functions
- Enabled configuration declarations: `iaa_crypto_debugfs_init()`, `iaa_crypto_debugfs_cleanup()`, global update helpers, completion error update helpers, and workqueue update helpers.
- Disabled configuration stubs: exact-signature inline no-ops for all update functions and a zero-returning `iaa_crypto_debugfs_init()`.
- The workqueue APIs accept `struct idxd_wq *` but rely on other included driver headers to define it before use.

## Control Flow
Callers can unconditionally invoke stats hooks from IAA crypto code. The preprocessor either routes to the real implementation in `iaa_crypto_stats.c` or compiles away the calls with no runtime branch.

## State And Persistence
The header owns no state. It controls whether the state in `iaa_crypto_stats.c` exists at all.

## Dependencies And Integration Points
The file is consumed by IAA crypto code and coupled to the Kconfig symbol `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`. It also indirectly depends on IDXD workqueue types.

## Risks
- Disabled builds silently discard all stats, so tests that expect debugfs files must select the stats Kconfig option.
- The trailing `#endif // CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS` uses C++ comment style, accepted by kernel C but less common than block comments in some older kernel code.

## Test Signals
- Build both with and without `CONFIG_CRYPTO_DEV_IAA_CRYPTO_STATS`.
- In disabled builds, verify callers link without `iaa_crypto_stats.c` and debugfs lifecycle calls return success/no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Kconfig

## Purpose
This Kconfig file defines `CRYPTO_DEV_IXP4XX`, the build option for the Intel IXP4xx NPE crypto acceleration driver.

## Important APIs, Types, And Functions
The symbol is a tristate named "Driver for IXP4xx crypto hardware acceleration". It depends on `ARCH_IXP4XX` or `COMPILE_TEST`, and on the platform queue manager and NPE support symbols `IXP4XX_QMGR` and `IXP4XX_NPE`.

## Control Flow
Selecting the option pulls in crypto API dependencies used by `ixp4xx_crypto.c`, including AES, DES, ECB, CBC, CTR, DES library helpers, AEAD, AUTHENC, and SKCIPHER support.

## State And Persistence
No runtime state is stored here. The Kconfig choice controls whether the driver is built in, built as a module, or omitted.

## Dependencies And Integration Points
The option integrates with the `Makefile` in the same directory through `obj-$(CONFIG_CRYPTO_DEV_IXP4XX) += ixp4xx_crypto.o`.

## Risks
- The driver has hardware/platform dependencies, so `COMPILE_TEST` can prove build coverage but not runtime correctness.
- Selecting broad crypto dependencies can increase the kernel/module footprint.

## Test Signals
- Build with `CRYPTO_DEV_IXP4XX=m` and `=y` on IXP4xx-capable or compile-test configurations.
- Confirm the corresponding object is included only when the symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Makefile

## Purpose
This Makefile wires the IXP4xx crypto driver object into Kbuild.

## Important APIs, Types, And Functions
It contains one build rule: `obj-$(CONFIG_CRYPTO_DEV_IXP4XX) += ixp4xx_crypto.o`.

## Control Flow
Kbuild compiles and links `ixp4xx_crypto.o` when the Kconfig symbol is enabled, either into vmlinux or as a module depending on the tristate value.

## State And Persistence
There is no runtime state. The file influences build output only.

## Dependencies And Integration Points
It is paired with `Kconfig` and the source file `ixp4xx_crypto.c`.

## Risks
Low risk. Any rename of the C file or Kconfig symbol must be mirrored here.

## Test Signals
Run a kernel build with `CONFIG_CRYPTO_DEV_IXP4XX=m` and confirm `ixp4xx_crypto.ko` is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/ixp4xx_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/ixp4xx_crypto.c

## Purpose
This file implements a legacy Intel IXP4xx NPE-C hardware crypto driver for the Linux Crypto API. It registers asynchronous SKCIPHER and AEAD algorithms backed by the IXP4xx queue manager/NPE firmware, including DES, 3DES, AES ECB/CBC/CTR/RFC3686 CTR, and authenc HMAC-MD5/HMAC-SHA1 with CBC ciphers.

## Important APIs, Types, And Functions
- Hardware descriptors: `struct buffer_desc` represents NPE buffer chains; `struct crypt_ctl` is the command/control block submitted to the NPE.
- Per-request contexts: `struct ablk_ctx` tracks SKCIPHER source/destination descriptors, IV, encrypt flag, and fallback request; `struct aead_ctx` tracks AEAD DMA chains, IV scatterlist, scattered HMAC storage, and encrypt flag.
- Transform context: `struct ixp_ctx` owns encrypt/decrypt security-association contexts, auth/encryption keys, RFC3686 nonce/salt state, setup completion, and SKCIPHER fallback tfm.
- Descriptor allocation: `setup_crypt_desc()`, `get_crypt_desc()`, and `get_crypt_desc_emerg()` allocate coherent descriptor memory and hand out normal or emergency command slots under spinlocks.
- Initialization: `init_ixp_crypto()` locates the NPE/queue IDs from device tree or legacy defaults, loads/probes firmware, checks AES support, creates DMA pools, requests queue manager queues, and enables receive interrupts.
- Transform setup: `setup_cipher()`, `gen_rev_aes_key()`, `setup_auth()`, and `register_chain_var()` build NPE context memory and submit setup commands for AES reverse keys and HMAC inner/outer pads.
- Data submission: `ablk_perform()` and `aead_perform()` map scatterlists into NPE buffer chains, populate `crypt_ctl`, and submit queue entries. `ablk_rfc3686_crypt()` constructs the RFC3686 counter block.
- Completion: `irqhandler()` schedules `crypto_done_tasklet`; `crypto_done_action()` drains the receive queue; `one_packet()` frees DMA chains, restores/updates IVs, copies scattered tags, and calls Crypto API completion callbacks.
- Registration: `ixp_crypto_probe()` registers `ixp4xx_algos[]` and `ixp4xx_aeads[]`; `ixp_crypto_remove()` unregisters them and releases queues/pools/NPE resources.

## Control Flow
Probe initializes hardware resources, derives firmware capabilities, then registers supported Crypto API algorithms. A caller sets a key, which resets SA contexts and may submit asynchronous NPE setup work; the setkey path waits for setup completion before returning. Encrypt/decrypt requests check queue/configuration readiness, allocate a control descriptor, chain DMA buffers from SG lists, submit the descriptor to `send_qid`, and return `-EINPROGRESS`. The queue manager receive interrupt schedules a tasklet that consumes completed physical descriptor addresses, decodes success versus authentication failure from low bits, completes the original request, and returns the descriptor to the free pool.

## State And Persistence
Global runtime state includes the selected `npe_c`, queue IDs, DMA pools, coherent `crypt_virt`/`crypt_phys`, AES capability flag, and platform device pointer. Per-transform state persists keys and NPE context memory until tfm exit. Per-request state lives in Crypto API request contexts and is cleaned on completion/error. No state persists across driver unload or system reboot.

## Dependencies And Integration Points
The driver depends on IXP4xx platform NPE and queue-manager APIs, DMA pools/coherent memory, device tree phandles (`intel,npe-handle`, `queue-rx`, `queue-txready`), Crypto API SKCIPHER/AEAD/AUTHENC internals, DES/AES/HMAC helpers, tasklets, and platform driver matching for `intel,ixp4xx-crypto`.

## Risks
- `aead_perform()` uses `crypt->auth_len = req->assoclen + cryptlen` and special scattered-HMAC handling; off-by-one or SG length mismatches can corrupt authentication tag handling.
- SKCIPHER fallback is used for multi-entry source or destination SG lists, so hardware coverage is narrower than the registered algorithms suggest.
- Descriptor allocation uses only `NPE_QLEN` coherent descriptors despite emergency indexing up to `NPE_QLEN_TOTAL`; this deserves scrutiny because `setup_crypt_desc()` allocates `NPE_QLEN * sizeof(struct crypt_ctl)` while emergency slots index beyond `NPE_QLEN`.
- The AEAD registration loop checks `ixp4xx_algos[i].cfg_enc` when deciding AES support for AEAD entries; indexing a different array can skip or include the wrong AEADs if array order/length diverges.
- Several paths rely on `BUG_ON(qmgr_stat_overflow(send_qid))`, which can crash the kernel on queue-manager overflow.
- The driver uses legacy tasklets and direct SG virtual mapping assumptions (`sg_virt()`), both of which are sensitive to platform constraints.

## Test Signals
- Crypto API self-tests for all registered algorithms, including authenc MD5/SHA1 with DES/3DES/AES and RFC3686 CTR.
- Runtime tests on firmware revisions with and without AES support to verify registration filtering.
- Stress tests with queue saturation, in-place and out-of-place buffers, short tags, scattered tags, and asynchronous completions.
- KASAN/DMA API debug checks around descriptor allocation, SG mapping/unmapping, and error exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/ixp4xx_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Kconfig

## Purpose
This Kconfig file defines build options for Intel Keem Bay OCS crypto accelerators: AES/SM4, optional ECB and CTS modes, ECC/ECDH, HCU hash/HMAC, and optional SHA224/HMAC-SHA224.

## Important APIs, Types, And Functions
- `CRYPTO_DEV_KEEMBAY_OCS_AES_SM4`: tristate AES/SM4 accelerator selecting SKCIPHER, AEAD, and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_AES_SM4_ECB` and `_CTS`: optional bools gated by the AES/SM4 driver, with help text warning Intel does not recommend those modes.
- `CRYPTO_DEV_KEEMBAY_OCS_ECC`: tristate ECDH accelerator requiring OF and I/O memory and selecting ECDH and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_HCU`: tristate hash/HMAC accelerator selecting HASH and CRYPTO_ENGINE.
- `CRYPTO_DEV_KEEMBAY_OCS_HCU_HMAC_SHA224`: optional SHA224/HMAC-SHA224 support, disabled by default because Intel recommends not using those algorithms.

## Control Flow
Kconfig symbols control which platform drivers and algorithms are compiled. The AES/SM4 optional symbols conditionally include ECB/CTS algorithm registrations and module aliases in `keembay-ocs-aes-core.c`; the HCU SHA224 symbol conditionally includes SHA224 algorithm table entries.

## State And Persistence
No runtime state is stored here. The file determines compile-time driver coverage.

## Dependencies And Integration Points
The symbols integrate with `keembay/Makefile` and the Linux Crypto API. Platform drivers require Keem Bay hardware or `COMPILE_TEST`; ECC and HCU also require Open Firmware device matching.

## Risks
- Optional unsafe/legacy modes are deliberately exposed when selected; downstream configs must choose them intentionally.
- Compile-test builds cannot validate register-level behavior.

## Test Signals
- Build matrix covering base AES/SM4, optional ECB/CTS, ECC, HCU, and SHA224.
- Confirm optional algorithm aliases appear only when the related Kconfig symbols are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Makefile

## Purpose
This Makefile defines the object composition for Keem Bay OCS crypto drivers.

## Important APIs, Types, And Functions
- `keembay-ocs-aes.o` is built from `keembay-ocs-aes-core.o` and `ocs-aes.o`.
- `keembay-ocs-ecc.o` is built as a single-object module.
- `keembay-ocs-hcu.o` is built from `keembay-ocs-hcu-core.o` and `ocs-hcu.o`.

## Control Flow
Kbuild includes each module based on its Kconfig symbol. The core files implement Crypto API/platform-driver glue, while `ocs-aes.o` and `ocs-hcu.o` provide lower-level register/DMA primitives.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
This file is coupled to `Kconfig` and the source file names in the same directory.

## Risks
Low risk. Build failures will occur if object names drift from source names.

## Test Signals
Build each Keem Bay crypto option as module and built-in, verifying multi-object modules link correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-aes-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-aes-core.c

## Purpose
This is the Crypto API and platform-driver front end for the Intel Keem Bay OCS AES/SM4 accelerator. It registers asynchronous SKCIPHER and AEAD algorithms, queues requests through `crypto_engine`, prepares DMA linked lists, invokes the low-level `ocs-aes.c` hardware helpers, and handles software fallback for AES-192.

## Important APIs, Types, And Functions
- `struct ocs_aes_tctx` stores selected OCS device, key material, key length, cipher type, fallback cipher, and fallback flag.
- `struct ocs_aes_rctx` stores per-request instruction/mode, SG/DMA counts, linked-list descriptors, CBC/CTS scratch state, and AEAD tag buffers.
- Device registry: `struct ocs_aes_drv ocs_aes` and `kmb_ocs_aes_find_dev()` maintain the single expected platform device and bind transforms to it.
- Key setup: `check_key()`, `save_key()`, `kmb_ocs_sk_set_key()`, and `kmb_ocs_aead_set_key()` validate keys and route AES-192 to fallback.
- SKCIPHER path: `kmb_ocs_sk_common()` validates input, handles zero-length cases, or queues to the engine; `kmb_ocs_sk_run()` prepares DMA, invokes `ocs_aes_op()`, updates IVs, and performs CTS CS2/CS3 block swaps.
- AEAD path: `kmb_ocs_aead_common()` queues requests or uses fallback; `kmb_ocs_aead_dma_prepare()` builds AAD and payload linked lists; `kmb_ocs_aead_run()` invokes CCM/GCM helpers and handles tag compare/copy.
- Engine callbacks: `kmb_ocs_aes_sk_do_one_request()` and `kmb_ocs_aes_aead_do_one_request()` program the hardware key then run the request and finalize it.
- Algorithm tables: `algs[]` and `algs_aead[]` register AES/SM4 ECB/CBC/CTR/CTS and GCM/CCM variants, with optional ECB/CTS entries behind Kconfig.
- Platform lifecycle: `kmb_ocs_aes_probe()` configures a 32-bit DMA mask, maps registers, requests IRQ, starts the crypto engine, and registers algorithms; remove unregisters and exits the engine.

## Control Flow
Transform initialization allocates fallback tfms where needed and sets request-context size. Setkey validates or configures fallback. Encrypt/decrypt calls initialize request context and enqueue to the device engine. The engine callback programs the hardware key, maps SG lists into OCS DMA descriptors, runs the synchronous low-level operation, unmaps DMA, performs required post-processing (CBC IV update, CTS swap, GCM tag append/compare), and finalizes the Crypto API request.

## State And Persistence
Device state lives in `struct ocs_aes_dev` and the global device list. Transform state holds keys until tfm exit, where `clear_key()` zeroes both memory and hardware key registers if a device is bound. Request state is transient and cleaned by `kmb_ocs_sk_dma_cleanup()` or `kmb_ocs_aead_dma_cleanup()`. No persistent on-disk state exists.

## Dependencies And Integration Points
The file depends on the low-level OCS AES API in `ocs-aes.h`, Crypto API engine helpers, platform device resources, threaded IRQ registration, DMA mapping, scatterlist copy helpers, GCM authentication-size helpers, and Kconfig optional mode symbols.

## Risks
- AES-192 fallback must preserve request flags/authsize and request sizing; AEAD fallback stores a subrequest in request context and is sensitive to `crypto_aead_reqsize()`.
- In `register_aes_algs()`, the error unwind unregisters `ARRAY_SIZE(algs)` AEAD entries instead of `ARRAY_SIZE(algs_aead)`, which looks suspicious and should be tested.
- The non-in-place AEAD AAD copy uses `ocs_aes_bypass_op(..., req->cryptlen)` after building AAD lists of `req->assoclen`; this length mismatch is a risk signal.
- GCM decrypt uses `memcmp()` for tag comparison rather than a constant-time compare.
- The driver assumes one OCS device; list-first lookup without an empty-list check can be unsafe if transform initialization races platform removal.
- DMA linked-list creation failures rely on later cleanup; every error path needs DMA API debug coverage.

## Test Signals
- Crypto API self-tests for AES and SM4 CBC/CTR/GCM/CCM, plus optional ECB/CTS.
- AES-192 fallback tests for SKCIPHER and AEAD.
- In-place and out-of-place SG tests with nonzero AAD, empty payload, empty AAD, and multi-entry SG.
- CTS compatibility vectors for CBC-CS3 semantics.
- DMA API debug and KASAN tests around all preparation error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-aes-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-ecc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-ecc.c

## Purpose
This file implements the Keem Bay OCS ECC platform driver and Crypto API KPP algorithms for ECDH over NIST P-256 and P-384. It uses the hardware ECC block for scalar multiplication and modular arithmetic, with software ECC helpers for representation and validation.

## Important APIs, Types, And Functions
- `struct ocs_ecc_dev` holds the platform device, MMIO base, crypto engine, IRQ completion, and IRQ number.
- `struct ocs_ecc_ctx` holds the selected OCS device, curve, and private key.
- MMIO helpers: `ocs_ecc_wait_idle()`, `ocs_ecc_cmd_start()`, `ocs_ecc_write_cmd_and_data()`, `ocs_ecc_trigger_op()`, `ocs_ecc_read_cx_out()`, and `ocs_ecc_read_cy_out()`.
- Hardware math: `kmb_ecc_point_mult()` loads point/scalar/curve parameters, uses RNG-generated side-channel mask data, triggers multiplication, and reads X/Y output. `kmb_ecc_do_scalar_op()` performs modular multiply, add, or power operations.
- Validation: `kmb_ocs_ecc_is_pubkey_valid_partial()` checks nonzero, coordinate ranges, and curve equation; `kmb_ocs_ecc_is_pubkey_valid_full()` also checks `nQ` is zero.
- Key handling: `kmb_ecc_is_key_valid()` enforces private-key range; `kmb_ecc_gen_privkey()` generates a private key with random bits and validates it; `kmb_ocs_ecdh_set_secret()` decodes and stores or generates the private key.
- KPP operations: `kmb_ecc_do_shared_secret()` validates peer public key and computes shared X coordinate; `kmb_ecc_do_public_key()` computes and validates the public key.
- Algorithm registrations: `ocs_ecdh_p256` and `ocs_ecdh_p384` are `kpp_engine_alg` registrations.
- Platform lifecycle: `kmb_ocs_ecc_probe()` maps registers, requests IRQ, adds the device, starts crypto engine, and registers KPP algorithms; remove unregisters and exits.

## Control Flow
Transform init selects the curve and binds the single OCS ECC device. `set_secret` decodes user ECDH parameters and stores a private key in internal digit order. Public-key or shared-secret requests validate sizes and queue to `crypto_engine`. The engine callback dispatches based on `req->src`: no source means generate public key; source means compute shared secret. Hardware operations wait for idle, load operands through DATA_IN, trigger an interrupt-producing command, wait for completion, and read result registers.

## State And Persistence
Per-device state is runtime-only MMIO/engine/IRQ state in `ocs_ecc_dev`. Per-transform state persists the private key until tfm exit, where only the first word is currently zeroed via `memzero_explicit(tctx->private_key, sizeof(*tctx->private_key))`; the intended cleanup likely should cover the whole array. Request-local buffers for public/shared keys are stack or allocated ECC points and are freed before return.

## Dependencies And Integration Points
The driver depends on Crypto API KPP/ECDH, `crypto_engine`, Linux ECC internals (`ecc_curve`, `ecc_point`, `vli_*`, `ecc_swap_digits()`), kernel RNG, platform resources, MMIO polling, IRQ completions, OF matching on `intel,keembay-ocs-ecc`, and FIPS-related headers.

## Risks
- `kmb_ocs_ecdh_exit_tfm()` appears to clear only one `u64` of `private_key`, leaving most key material in memory.
- `kmb_ecc_gen_privkey()` generates one random candidate and fails if invalid instead of retrying, so key generation can spuriously fail.
- Public-key validation and scalar operations are hardware-assisted but involve many sequential operations; timeout or interrupt handling failures must be surfaced cleanly.
- Shared-secret output copies only `min(curve_bytes, req->dst_len)` after earlier size checks are limited; consumers need clear expectations for truncation.
- Device list lookup assumes a device is present during tfm init and may be fragile around hot-unplug/remove races.

## Test Signals
- KPP self-tests for `ecdh-nist-p256-keembay-ocs` and `ecdh-nist-p384-keembay-ocs`.
- Negative tests for invalid private keys, invalid public coordinates, zero points, wrong source/destination sizes, and RNG failure injection.
- KASAN/KMSAN checks to confirm private-key cleanup covers all words.
- IRQ timeout and spurious interrupt tests around `ocs_ecc_trigger_op()` and `ocs_ecc_irq_handler()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-hcu-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-hcu-core.c

## Purpose
This file is the Crypto API/front-end driver for the Keem Bay OCS Hash Control Unit. It registers asynchronous hash and HMAC algorithms, manages request buffering and DMA-list preparation, chooses hardware versus software-assisted HMAC, and delegates register-level operations to `ocs-hcu.c`.

## Important APIs, Types, And Functions
- `struct ocs_hcu_ctx` stores the bound device, HMAC key, key length, and transform flags for SM3/HMAC.
- `struct ocs_hcu_rctx` stores request flags, algorithm, block/digest sizes, DMA list, intermediate hash context, a double-block buffer, SG cursor state, and DMA mapping metadata.
- Device lookup: `kmb_ocs_hcu_find_dev()` binds transforms to the single expected HCU device.
- Buffering: `kmb_get_total_data()` and `flush_sg_to_ocs_buffer()` manage block-aligned streaming hash state.
- DMA preparation/cleanup: `kmb_ocs_dma_prepare()` maps the request buffer and the processable part of the SG list into an OCS DMA list; `kmb_ocs_hcu_dma_cleanup()` unmaps and frees it.
- HMAC helpers: `prepare_ipad()` prepares software-assisted HMAC inner padding; `kmb_ocs_hcu_setkey()` stores short keys or hashes long keys using the corresponding OCS hash algorithm.
- Request execution: `kmb_ocs_hcu_do_one_request()` handles update, final/finup, hardware HMAC, and software-assisted OPAD finalization.
- Crypto API methods: `kmb_ocs_hcu_init()`, `update()`, `final()`, `finup()`, `digest()`, `export()`, and `import()`.
- Algorithm table: `ocs_hcu_algs[]` registers SHA256, SM3, SHA384, SHA512, their HMACs, and optional SHA224/HMAC-SHA224.
- Platform lifecycle: `kmb_ocs_hcu_probe()` configures DMA mask, maps registers, requests IRQ, starts the crypto engine, and registers ahashes; remove unregisters and exits.

## Control Flow
`init()` resets request state and selects the algorithm from digest size and transform flags. `update()` either buffers small data or queues a block-aligned DMA update. `final()`/`finup()` mark the request final and choose hardware HMAC if the entire HMAC can be processed in one final request with a hardware-supported key length; otherwise they use software-assisted HMAC. The engine callback maps data, calls `ocs_hcu_hash_update()`, `ocs_hcu_hash_finup()`, `ocs_hcu_hash_final()`, `ocs_hcu_digest()`, or `ocs_hcu_hmac()`, then finalizes the Crypto API request.

## State And Persistence
Transform state persists HMAC keys until tfm exit, where HMAC transforms clear the key. Request state, including intermediate digest and partial buffers, is exportable/importable through raw `struct ocs_hcu_rctx` copies. DMA mappings and OCS DMA lists are transient and cleaned after each engine operation. There is no disk persistence.

## Dependencies And Integration Points
This file depends on `ocs-hcu.h`, Crypto API ahash/engine helpers, SHA2/SM3/HMAC constants, DMA mapping, scatterlist copy helpers, platform resources, and OF matching on `intel,keembay-ocs-hcu`.

## Risks
- `export()`/`import()` memcpy the whole request context, including pointers and device references. This is a known pattern in some drivers but can be risky if imported across device lifetime changes.
- Hardware HMAC supports only nonzero final messages and key length <= 64; all other cases rely on software-assisted ipad/opad sequencing.
- `kmb_ocs_hcu_do_one_request()` returns errors directly in some paths instead of always finalizing through `crypto_finalize_hash_request()`, so engine error semantics should be verified.
- `ocs_hcu_digest()` in the low-level helper has an error path that can return before `dma_unmap_single()`, which this front end may expose through long-key hashing or SW HMAC OPAD digest.
- Buffer accounting is subtle because update requests process block-aligned data and retain remainders in `buffer`.

## Test Signals
- Ahash self-tests for SHA256, SM3, SHA384, SHA512, all HMAC variants, and optional SHA224.
- Streaming tests with one-byte updates, block-boundary updates, `final()` with no new data, `finup()`, `digest()`, and export/import.
- HMAC tests covering short key, exactly block-size key, long key hashing, zero-length message, and multi-update message.
- DMA API debug and fault-injection tests around DMA map/list allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-hcu-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.c

## Purpose
This file provides low-level MMIO, DMA, interrupt, and mode sequencing primitives for the Keem Bay OCS AES/SM4 block. It is used by `keembay-ocs-aes-core.c` to perform ECB/CBC/CTR/CTS, GCM, CCM, and DMA bypass operations.

## Important APIs, Types, And Functions
- Register definitions cover AES command/key/IV/status, DMA source/destination/list registers, interrupt registers, tag/MAC registers, payload length, and byte-order configuration.
- `struct ocs_dma_linked_list` is the hardware DMA descriptor layout; public linked-list descriptors are represented by `struct ocs_dll_desc` from the header.
- IRQ helpers: `aes_irq_disable()`, `aes_irq_enable()`, `ocs_aes_irq_enable_and_wait()`, and `ocs_aes_irq_handler()` drive completion and DMA error reporting through `aes_dev->irq_completion` and `dma_err_mask`.
- Key programming: `ocs_aes_set_key()` validates AES/SM4 key sizes and writes key registers plus key-size register.
- Generic operation: `ocs_aes_validate_inputs()`, `set_ocs_aes_command()`, `ocs_aes_init()`, and `ocs_aes_op()` validate, configure, run, and wait for non-AEAD modes.
- GCM: `ocs_aes_gcm_op()` writes J0, tag length, payload/AAD bit lengths, processes AAD then payload, and reads tag registers through `ocs_aes_gcm_read_tag()`.
- CCM: `ocs_aes_ccm_op()` normalizes counter, writes B0 and AAD length encoding, processes AAD and payload, writes encrypted tag for decrypt, and compares tag registers through `ccm_compare_tag_to_yr()`.
- DMA list creation: `ocs_create_linked_list_from_sg()` builds coherent OCS DMA linked lists from already mapped SG entries and supports offsets into SG data.

## Control Flow
All operations initialize hardware by disabling/clearing interrupts, setting byte order, and writing the command register. Non-AEAD modes trigger the AES engine, configure source and destination linked-list DMA, set termination or CTS last-block signaling, wait for AES completion, and read CTR IV back when required. GCM/CCM split AAD and payload phases, using DMA source-done interrupts for AAD/payload feeding and AES-complete interrupts for final authentication/tag completion.

## State And Persistence
State is in hardware registers and `struct ocs_aes_dev` fields. `dma_err_mask` is written by the IRQ handler and consumed by wait helpers. Coherent DMA linked lists are allocated by the caller-facing helper and freed by front-end cleanup. No state persists beyond the operation except updated hardware registers and caller-managed IV/tag data.

## Dependencies And Integration Points
The file depends on Linux MMIO accessors, completions, IRQ handling, DMA coherent allocation, scatterlist DMA metadata, AES/GCM constants, and the public types declared in `ocs-aes.h`.

## Risks
- Many wait loops are busy loops without explicit timeout (`aes_a_wait_last_gcx()`, `aes_a_dma_wait_input_buffer_occupancy()`, performance-counter waits), so hardware hangs can stall the crypto engine worker.
- `ocs_aes_irq_enable_and_wait()` uses interruptible waits; signal interruptions propagate as errors but hardware may still be active.
- `ocs_aes_set_key()` casts arbitrary key pointers to `u32 *`, relying on alignment that may not be guaranteed on all architectures.
- `ocs_aes_ccm_op()` mutates the caller-provided IV by zeroing the counter field.
- `ocs_create_linked_list_from_sg()` assumes `sg_dma_len()`/`sg_dma_address()` are valid because the caller already mapped the SG list; misuse will produce invalid DMA descriptors.
- GCM and CCM tag compares are not constant-time.

## Test Signals
- Low-level mode vectors through the front-end driver for ECB/CBC/CTR/CTS/GCM/CCM and SM4 equivalents.
- Fault-injection around IRQ errors and DMA error bits to verify `-EIO` propagation.
- Hardware hang tests or instrumentation for busy-wait loops.
- SG offset/list tests for `ocs_create_linked_list_from_sg()` with zero data, offset crossing entries, and invalid lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.h

## Purpose
This header declares the public low-level OCS AES/SM4 interface shared between the Keem Bay AES/SM4 Crypto API front end and register/DMA implementation.

## Important APIs, Types, And Functions
- `enum ocs_cipher` selects AES or SM4.
- `enum ocs_mode` enumerates ECB, CBC, CTR, CCM, GCM, and CTS hardware modes.
- `enum ocs_instruction` selects encrypt, decrypt, expand, or bypass.
- `struct ocs_aes_dev` stores device list linkage, device pointer, IRQ, MMIO base, interrupt completion, DMA error mask, and crypto engine.
- `struct ocs_dll_desc` describes a coherent OCS DMA linked list.
- Public functions include `ocs_aes_set_key()`, `ocs_aes_op()`, `ocs_aes_gcm_op()`, `ocs_aes_ccm_op()`, `ocs_create_linked_list_from_sg()`, and `ocs_aes_irq_handler()`.
- Inline `ocs_aes_bypass_op()` wraps `ocs_aes_op()` in bypass mode for DMA copying.

## Control Flow
The front-end driver allocates/owns `struct ocs_aes_dev`, builds DMA lists into `struct ocs_dll_desc`, then calls these functions to program hardware. IRQ handling is exported so the platform probe can register it directly.

## State And Persistence
The header defines runtime state containers but stores no state by itself. State persists as long as the platform device or request context owns those structures.

## Dependencies And Integration Points
It depends on DMA mapping types and forward uses `struct scatterlist` and `struct crypto_engine` through included kernel headers from consumers. It is paired with `ocs-aes.c` and `keembay-ocs-aes-core.c`.

## Risks
- `ocs_aes_bypass_op()` hardcodes AES ECB mode with BYPASS instruction; callers must ensure this remains semantically a DMA copy and not a crypto operation.
- Header consumers must initialize `irq_completion`, `base_reg`, `dev`, and `engine` before using the public APIs.

## Test Signals
- Compile coverage for both front-end and low-level objects.
- Runtime bypass-copy tests through CTS/non-in-place and AEAD AAD-copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.c

## Purpose
This file implements low-level register, DMA, interrupt, and hash/HMAC sequencing for the Keem Bay OCS Hash Control Unit. It is the hardware primitive layer consumed by `keembay-ocs-hcu-core.c`.

## Important APIs, Types, And Functions
- Register definitions cover HCU mode, chain, operation, key, interrupt/status, message length, DMA, and MSI registers.
- `struct ocs_hcu_dma_entry` and `struct ocs_hcu_dma_list` implement the coherent linked-list format for source DMA.
- Utility helpers: `ocs_hcu_num_chains()`, `ocs_hcu_digest_size()`, `ocs_hcu_wait_busy()`, interrupt enable/disable/wait helpers, and intermediate digest get/set helpers.
- Hardware configuration: `ocs_hcu_hw_cfg()` selects algorithm, endianness, and hardware HMAC mode.
- Key handling: `ocs_hcu_write_key()` writes and byte-swaps/pads the hardware HMAC key; `ocs_hcu_clear_key()` clears key registers.
- DMA operations: `ocs_hcu_ll_dma_start()` runs linked-list DMA and waits on either DMA or HCU completion depending on finality.
- Public DMA-list APIs: `ocs_hcu_dma_list_alloc()`, `ocs_hcu_dma_list_free()`, and `ocs_hcu_dma_list_add_tail()`.
- Public hash APIs: `ocs_hcu_hash_init()`, `ocs_hcu_hash_update()`, `ocs_hcu_hash_finup()`, `ocs_hcu_hash_final()`, `ocs_hcu_digest()`, and `ocs_hcu_hmac()`.
- IRQ handling: `ocs_hcu_irq_handler()` reads and clears HCU and DMA interrupt status, records error state, and completes waiters.

## Control Flow
Hash update configures hardware, restores intermediate state if present, starts linked-list DMA without termination, then reads back intermediate state. Finup configures/restores state, starts linked-list DMA with termination, waits for HCU completion, and reads the digest. Final without new data configures/restores state, writes terminate, waits, and reads digest. One-shot digest maps a linear buffer and starts direct DMA. Hardware HMAC configures HMAC mode, writes the key, runs final linked-list DMA, clears hardware key registers, and reads digest.

## State And Persistence
Persistent runtime state exists in hardware chain/message-length registers during an active operation and in `struct ocs_hcu_hash_ctx` between updates. `hcu_dev->irq_err` records whether the IRQ handler saw an error before the wait returns. DMA list memory is coherent and caller-owned. Hardware HMAC keys are cleared after use.

## Dependencies And Integration Points
The file depends on `ocs-hcu.h`, Linux MMIO and polling helpers, DMA mapping/coherent allocation, completions, IRQ handling, SHA2 constants, and front-end request code that supplies mapped data through DMA lists.

## Risks
- `ocs_hcu_digest()` returns immediately on `ocs_hcu_wait_and_disable_irq()` error without unmapping the direct DMA buffer, creating a DMA mapping leak on that error path.
- `kmalloc_obj(*dma_list)` is nonstandard-looking; build coverage should confirm the local tree provides this macro/helper.
- `ocs_hcu_dma_list_add_tail()` truncates DMA addresses to 32 bits after checking against `OCS_HCU_DMA_BIT_MASK`, so correct 32-bit DMA mask setup is mandatory.
- Interruptible waits can return early while hardware may still be active.
- Direct one-shot digest does not check `data`/`dgst` for NULL before DMA/register use; callers are expected to validate.

## Test Signals
- Front-end hash/HMAC Crypto API vectors exercising update, finup, final, digest, and HMAC.
- DMA API debug with injected interrupt errors to catch the one-shot digest unmap leak.
- Tests for DMA list append capacity, zero-length entries, and invalid high DMA addresses.
- IRQ error-bit injection to verify `irq_err` propagation and clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.h

## Purpose
This header defines the public low-level OCS HCU interface for the Keem Bay hash front end. It declares device/context structures, supported algorithms, DMA-list APIs, hash/HMAC APIs, and the IRQ handler.

## Important APIs, Types, And Functions
- Constants: `OCS_HCU_DMA_BIT_MASK` enforces 32-bit DMA addressing; `OCS_HCU_HW_KEY_LEN` defines the maximum hardware HMAC key register vector.
- `enum ocs_hcu_algo` enumerates SHA256, SHA224, SHA384, SHA512, and SM3 hardware algorithm IDs.
- `struct ocs_hcu_dev` holds device list linkage, device pointer, MMIO base, crypto engine, IRQ state, and error flag.
- `struct ocs_hcu_idata` stores message length and digest/intermediate chain data.
- `struct ocs_hcu_hash_ctx` pairs algorithm selection with intermediate data.
- Public APIs cover DMA list allocation/free/add, streaming hash update/finup/final, one-shot digest, hardware HMAC, and IRQ handling.

## Control Flow
The front end initializes `struct ocs_hcu_dev` during platform probe and embeds `struct ocs_hcu_hash_ctx` in each request context. It then uses the declared APIs to build DMA lists and advance/finalize hardware hash state.

## State And Persistence
The header declares state containers but owns no storage. Intermediate state can be copied/exported by higher layers through `struct ocs_hcu_hash_ctx`.

## Dependencies And Integration Points
It depends on DMA mapping types and SHA512 digest size. It is consumed by both `ocs-hcu.c` and `keembay-ocs-hcu-core.c`.

## Risks
- Consumers must respect the 32-bit DMA mask and initialize completions/IRQ state before invoking low-level operations.
- `struct ocs_hcu_idata` always allocates SHA512-sized digest storage, which is safe for smaller algorithms but requires correct digest-size validation on output.

## Test Signals
- Compile coverage of both HCU objects.
- Runtime coverage for every declared public operation through the Crypto API front end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/ocs-hcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Kconfig

## Purpose
This Kconfig file defines Intel QuickAssist Technology driver symbols, including the shared `CRYPTO_DEV_QAT` core and multiple physical/virtual device families.

## Important APIs, Types, And Functions
- `CRYPTO_DEV_QAT` is a hidden tristate selected by all QAT device drivers and selects crypto/compression dependencies, firmware loader, and CRC8.
- Device symbols include DH895xCC, C3XXX, C62X, QAT_4XXX, QAT_420XX, QAT_6XXX, and VF variants for older devices.
- Physical-function symbols depend on PCI and endian/architecture constraints, then select `CRYPTO_DEV_QAT`.
- VF symbols also select `PCI_IOV`.
- `CRYPTO_DEV_QAT_ERROR_INJECTION` enables debugfs heartbeat error injection for developer testing.

## Control Flow
Selecting a device-family symbol causes Kbuild to enter the matching subdirectory via the QAT Makefile and build family-specific PCI/hardware-data code plus common QAT infrastructure.

## State And Persistence
No runtime state is stored here. Symbols control compile-time inclusion and module availability.

## Dependencies And Integration Points
The file integrates with `drivers/crypto/intel/qat/Makefile`, QAT common code, PCI/SRIOV, Crypto API algorithms, firmware loading, and compression dependencies such as ZSTD.

## Risks
- The hidden common symbol selects many Crypto API capabilities; enabling any QAT family expands kernel/module dependencies.
- Device support under `COMPILE_TEST` cannot validate firmware loading or accelerator runtime behavior.

## Test Signals
- Build selected PF and VF symbols as modules.
- Confirm `CRYPTO_DEV_QAT_420XX` produces the `qat_420xx` module and pulls in `qat_common`.
- For error injection, confirm debugfs entries exist only with `DEBUG_FS` and the option enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Makefile

## Purpose
This Makefile routes QAT Kconfig symbols to common and family-specific subdirectories.

## Important APIs, Types, And Functions
It sets `subdir-ccflags-y := -I$(src)/qat_common` and conditionally includes `qat_common/` plus subdirectories for DH895xCC, C3XXX, C62X, QAT_4XXX, QAT_420XX, QAT_6XXX, and legacy VF devices.

## Control Flow
When any QAT device selects `CRYPTO_DEV_QAT`, `qat_common/` is built. Each device-family symbol adds its matching subdirectory to the build.

## State And Persistence
No runtime state exists here. It affects include paths and object traversal during build.

## Dependencies And Integration Points
The include path makes common headers available to subdirectory code. The file is coupled to `qat/Kconfig` and each family subdirectory Makefile.

## Risks
Low to moderate build-system risk: common include-path changes affect all QAT family builds.

## Test Signals
Kernel build with multiple QAT family symbols enabled to confirm all subdirectories see `qat_common` headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/Makefile

## Purpose
This Makefile defines the module composition for the Intel QAT 420xx device family.

## Important APIs, Types, And Functions
It builds `qat_420xx.o` when `CONFIG_CRYPTO_DEV_QAT_420XX` is enabled, with constituent objects `adf_drv.o` and `adf_420xx_hw_data.o`.

## Control Flow
Kbuild links the family PCI driver and hardware-data table into a single module or built-in object.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
The file integrates with the parent QAT Makefile and the hardware-data implementation in this directory.

## Risks
Low risk. Object-name drift would break the family module build.

## Test Signals
Build `CONFIG_CRYPTO_DEV_QAT_420XX=m` and confirm `qat_420xx.ko` includes both objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.c

## Purpose
This file initializes the hardware abstraction table for Intel QAT 420xx devices. It defines firmware object layouts, acceleration-engine masks, feature capability calculation, rate-limit data, firmware object callbacks, error masks, and gen4 operation hooks assigned into `struct adf_hw_device_data`.

## Important APIs, Types, And Functions
- Firmware object tables: `adf_420xx_fw_objs[]` names sym/asym/DC/admin objects; `adf_fw_*_config[]` map AE groups to firmware objects for service modes such as SYM_ASYM, DC, DCC, SYM, ASYM, ASYM_DC, and SYM_DC.
- AE masks: `get_ae_mask()` masks off fused-out AE groups based on `ADF_FUSECTL4`; `update_ae_mask()` intersects physical AE availability with the selected firmware service layout.
- Firmware callbacks: `uof_get_num_objs()`, `get_fw_config()`, `uof_get_name_420xx()`, `uof_get_obj_type()`, and `uof_get_ae_mask()` describe firmware images and AE assignment to common QAT loader code.
- Capability calculation: `get_accel_cap()` reads `ADF_GEN4_FUSECTL1_OFFSET`, clears capabilities for fused-off slices, and filters the final mask by enabled service mode.
- Arbiter/ring helpers: `adf_get_arbiter_mapping()`, `get_rp_group()`, and `get_ena_thd_mask()` configure gen4 arbitration and thread masks.
- Rate limiting: `adf_init_rl_data()` fills token-bucket offsets, scale factors, max throughput, scan interval, slice reference, and service-AE counts.
- Error reporting: `adf_gen4_set_err_mask()` fills 420xx-specific parity/error masks.
- Public lifecycle: `adf_init_hw_data_420xx()` populates `struct adf_hw_device_data` with 420xx constants and many gen4 common function pointers; `adf_clean_hw_data_420xx()` decrements the class instance count.

## Control Flow
The 420xx PCI driver calls `adf_init_hw_data_420xx()` during device setup. That function sets counts, masks, firmware names, callbacks, reset/interrupt/admin/arbiter/PFVF/DC/RAS/TL/VF-migration/rate-limit hooks, and capability functions. Later common QAT code calls these hooks to derive AE masks, load the right firmware images, expose capabilities, configure ring services, manage power/heartbeat/timers, and handle resets/migration. Cleanup decrements the per-class instance counter.

## State And Persistence
The file writes runtime configuration into caller-owned `struct adf_hw_device_data`. Static firmware config arrays and the static `adf_420xx_class` persist for the module lifetime. Device capability state depends on PCI fuse registers and selected service configuration; it is not persisted outside runtime driver state.

## Dependencies And Integration Points
This file is tightly integrated with QAT common and gen4 infrastructure: `adf_accel_devices`, admin, bank state, cfg services, clock, firmware config, gen4 CSR/hardware/PFVF/PM/RAS/TL/VF migration, timers, and `icp_qat_hw` capability bits. It also relies on constants from `adf_420xx_hw_data.h`.

## Risks
- Capability reporting is fuse and service-mode sensitive; any mismatch between firmware layout and capability mask can expose unsupported services or hide working ones.
- `update_ae_mask()` assumes `get_fw_config()` returns non-NULL when `uof_get_num_objs()` is nonzero; unexpected service values must remain impossible or guarded by callers.
- `get_rp_group()` has special handling for AE group 2 depending on whether the config pointer equals `adf_fw_cy_config`; changes to config table identity may affect routing.
- `adf_clean_hw_data_420xx()` blindly decrements the class instance count; double cleanup would underflow logical instance accounting.

## Test Signals
- QAT 420xx probe tests for every service mode, verifying loaded firmware objects, AE masks, capabilities, and ring-to-service maps.
- Fuse simulation or hardware SKU coverage to ensure capability bits are cleared for disabled slices.
- Rate-limit tests for SYM/ASYM/DC throughput constants.
- Error injection/RAS tests to confirm the configured parity masks catch expected hardware errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.h

## Purpose
This header provides 420xx-specific constants and lifecycle declarations used by the QAT 420xx hardware-data implementation and family driver.

## Important APIs, Types, And Functions
- Hardware shape constants: `ADF_420XX_MAX_ACCELENGINES`, `ADF_420XX_ACCELENGINES_MASK`, and `ADF_420XX_ADMIN_AE_MASK`.
- Error/parity masks: CPP agent command parity, ATH/CPH, CPR/XLT, DCPR/UCS, PKE, WAT/WCP, and `ADF_420XX_SSMFEATREN_MASK`.
- Firmware names: `qat_420xx.bin`, `qat_420xx_mmp.bin`, and per-service object binaries for sym, DC, asym, and admin.
- Rate-limit constants: PCIe scale factors, decompression correction, scan rate, max throughput per service, and slice reference.
- Clock constant: `ADF_420XX_AE_FREQ`.
- Public functions: `adf_init_hw_data_420xx()` and `adf_clean_hw_data_420xx()`.

## Control Flow
The family driver includes this header to initialize and clean `struct adf_hw_device_data`. The C implementation uses the constants when installing gen4 operation hooks and reporting firmware/capability/rate-limit metadata.

## State And Persistence
The header owns no runtime state. Its constants define runtime hardware-data values loaded into device structures.

## Dependencies And Integration Points
It depends on `adf_accel_devices.h` and gen4/common QAT infrastructure that interprets these values.

## Risks
- Firmware filename constants must match installed firmware package names.
- Throughput and clock constants influence rate limiting and heartbeat timing; incorrect values can affect performance management.
- Error masks are hardware-specific and must remain synchronized with 420xx register definitions.

## Test Signals
- Build coverage for QAT 420xx.
- Firmware loading tests confirming all named binaries are requested as expected.
- Runtime sanity checks that reported number of AEs and masks match hardware documentation/SKU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/adf_420xx_hw_data.h -->
