# Research: subset-b-001244

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-aes.c

Purpose: registers and implements TI K3 DTHE V2 AES acceleration for Linux skcipher and AEAD crypto API users. It exposes ECB/CBC/CTR/XTS AES skciphers plus GCM/CCM AEAD modes, queues work through `crypto_engine`, drives DTHE AES registers, and uses DMA for data movement.

Important APIs, types, and functions: the file consumes `struct dthe_tfm_ctx`, `struct dthe_aes_req_ctx`, and `dthe_data` from `dthev2-common.h`. Key routines are `dthe_aes_set_ctrl_key()` for programming keys, IV, mode, direction, and key size; `dthe_aes_run()` for skcipher DMA execution; `dthe_aead_run()` for AEAD AAD/data DMA and tag handling; `dthe_aead_read_tag()`, `dthe_aead_enc_get_tag()`, and `dthe_aead_dec_verify_tag()` for authentication; and `dthe_register_aes_algs()` / `dthe_unregister_aes_algs()` for crypto registration. Fallback entry points are `dthe_aes_do_fallback()` and `dthe_aead_do_fallback()`.

Control flow: crypto API setkey initializes `ctx->aes_mode`, validates AES key sizes, copies key material, and initializes software fallback transforms where needed. Encrypt/decrypt callbacks set `rctx->enc` and either reject invalid block lengths, choose software fallback for unsupported XTS/AEAD edge cases, or transfer the request to the device crypto engine. The engine callback programs hardware, builds padded scatterlists for CTR/AEAD partial blocks, maps scatterlists to DMA, submits RX/TX descriptors, waits for a completion with a timeout, reads back updated IV/tag state, unmaps/frees temporary scatterlists, and finalizes the original crypto request.

State and persistence: persistent per-transform state includes key words, key length, mode, auth size, fallback transform pointers, and cached device pointer. Per-request state stores the encryption flag, completion, and two AES-block padding buffers. Hardware state lives in DTHE AES MMIO registers under `DTHE_P_AES_BASE`, including key slots, IV/context, control, length, tag, IRQ, and DMA enable registers. No disk state is written; secrets are copied into transform memory and hardware registers, with temporary padding zeroed on cleanup.

Dependencies and integration points: depends on the Linux crypto API, crypto engine framework, DMA engine, scatterlist helpers, `readl_relaxed_poll_timeout()`, AES/GCM constants, and the common DTHE platform driver for device selection and DMA channels. Integration is through registered algorithm names `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `xts(aes)`, `gcm(aes)`, and `ccm(aes)` with DTHE-specific driver names and priority 299.

Risks and test signals: notable risk areas are DMA completion timeout handling, temporary scatterlist construction with `GFP_ATOMIC`, in-place vs separate src/dst DMA directions, IV endianness/word layout, fallback consistency, and a documented hardware workaround for AAD-only AEAD after prior payload-only operations. AEAD decryption subtracts `authsize` from `cryptlen`, so underflow prevention is a critical test. Test signals should include crypto selftests for all registered modes, partial CTR input, XTS ciphertext-stealing fallback, zero-length rules, GCM/CCM tag mismatch, AAD-only and data-only AEAD, DMA timeout injection, fallback transform allocation failure, and module unload after active transforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.c

Purpose: platform and common support for the TI DTHE V2 crypto accelerator. It owns device discovery, MMIO mapping, DMA channel setup, crypto engine lifecycle, global device list management, and delegates algorithm registration to the AES implementation.

Important APIs, types, and functions: `dthe_get_dev()` chooses a DTHE device for transform contexts and rotates the global list for basic load spreading. `dthe_copy_sg()` copies scatterlist entries by virtual address into a new scatterlist prefix. `dthe_dma_init()` requests and configures `"rx"`, `"tx1"`, and `"tx2"` DMA channels. `dthe_probe()` maps resources, links the device into the global list, starts a single-depth crypto engine, and calls `dthe_register_algs()`. `dthe_remove()` unregisters algorithms, exits the engine, releases DMA channels, and removes the device from the list.

Control flow: platform probe allocates `dthe_data`, maps MMIO resource 0, stores driver data, adds the device to `dthe_dev_list`, initializes DMA, allocates/starts `crypto_engine`, then registers algorithms. Error paths unwind in reverse order. Removal takes the device out of the global list first, unregisters algorithms, exits the engine, and releases all DMA channels.

State and persistence: software state is `struct dthe_data` plus the file-static `dthe_dev_list` protected by a spinlock. DMA channel pointers and the crypto engine persist for the platform device lifetime. There is no persistent storage beyond hardware registers and in-memory device list entries.

Dependencies and integration points: depends on platform driver probing, OF compatible `"ti,am62l-dthev2"`, devm allocation/ioremap, DMA engine slave configuration, crypto engine, and algorithm registration exported by `dthev2-aes.c`. The SHA TX DMA channel is requested even though this subset only registers AES algorithms, suggesting planned/shared support.

Risks and test signals: `dthe_get_dev()` assumes at least one device exists and uses `list_first_entry()` without an empty-list guard, so algorithm use before probe or after teardown would be dangerous if registration ordering breaks. `dthe_copy_sg()` uses `sg_virt()` and therefore assumes CPU-addressable scatterlist entries. Probe failure unwind and remove paths should be tested with missing DMA channels, engine start failure, algorithm registration failure, and multiple DTHE devices to verify list rotation and locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.h

Purpose: shared definitions for the TI DTHE V2 driver. It defines device, transform, request, mode, timeout, and helper prototypes used by the common platform layer and AES implementation.

Important APIs, types, and functions: constants include `DTHE_REG_SIZE`, `DTHE_DMA_TIMEOUT_MS`, and `DTHE_MAX_KEYSIZE`. `enum dthe_aes_mode` enumerates ECB/CBC/CTR/XTS/GCM/CCM. `struct dthe_data` stores device, MMIO base, list node, crypto engine, and AES/SHA DMA channels. `struct dthe_tfm_ctx` holds per-transform key/auth/mode state and a union of skcipher or AEAD fallback transforms. `struct dthe_aes_req_ctx` carries request direction, padding, and completion. Prototypes cover device lookup, scatterlist copy, and AES algorithm registration.

Control flow: the header itself has no runtime control flow, but it fixes the contracts used by `dthev2-common.c` probe/device management and `dthev2-aes.c` request execution. The fallback pointer union relies on each algorithm family using the correct init/exit path.

State and persistence: all defined state is in-memory kernel driver state. The largest secret-bearing allocation is `dthe_tfm_ctx.key`, sized for XTS-AES-256. Request padding is transient and should be zeroed by users after partial-block handling.

Dependencies and integration points: includes Linux crypto internal headers, DMA engine, DMA mapping, scatterlist, I/O helpers, and AES/hash types. It is the private ABI between DTHE source files, not an external userspace ABI.

Risks and test signals: the union between AEAD and skcipher fallback pointers saves space but makes algorithm init/exit pairing important. `DTHE_DMA_TIMEOUT_MS` controls request completion behavior globally. Tests should verify transform context size, request context size, and that every algorithm using fallback initializes and frees the correct union member.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ti/dthev2-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/Kconfig

Purpose: build-time configuration for the virtio crypto driver.

Important APIs, types, and functions: `config CRYPTO_DEV_VIRTIO` defines a tristate option named "VirtIO crypto driver". It depends on `VIRTIO` and selects crypto subsystems needed by this implementation: AEAD, AKCIPHER2, SKCIPHER, CRYPTO_ENGINE, RSA, and MPILIB.

Control flow: Kconfig selection controls whether the module is built in, built as `virtio_crypto`, or omitted. No runtime logic is present.

State and persistence: no runtime state is stored in this file. It affects kernel configuration state and module availability.

Dependencies and integration points: integrates with the kernel crypto menu and virtio stack. The selected RSA/MPILIB symbols match `virtio_crypto_akcipher_algs.c`, while skcipher and engine symbols support AES-CBC request queuing.

Risks and test signals: dependency drift is the key risk. If algorithm files gain AEAD/hash implementations, Kconfig selections must remain aligned. Test signals are successful allmodconfig/build coverage, module load with `CONFIG_CRYPTO_DEV_VIRTIO=m`, and absence of unresolved crypto symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/Makefile

Purpose: composes the virtio crypto module objects.

Important APIs, types, and functions: `obj-$(CONFIG_CRYPTO_DEV_VIRTIO) += virtio_crypto.o` declares the module, and `virtio_crypto-objs` links skcipher algorithms, akcipher algorithms, device manager, and core virtio driver objects.

Control flow: no runtime flow; object ordering ensures all implementation units are linked into `virtio_crypto.o`.

State and persistence: no runtime state. Build state is driven by `CONFIG_CRYPTO_DEV_VIRTIO`.

Dependencies and integration points: integrates with Kbuild and the Kconfig option in the same directory. All listed objects share `virtio_crypto_common.h`.

Risks and test signals: missing an object would surface as unresolved symbols for registration or request paths. Test signals are module build, `modinfo virtio_crypto`, and load/unload with both skcipher and akcipher code linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_akcipher_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_akcipher_algs.c

Purpose: implements virtio crypto asymmetric RSA algorithms for the kernel akcipher API. It creates host-side virtio crypto sessions for RSA keys and queues RSA encrypt/decrypt requests to a virtio data queue.

Important APIs, types, and functions: `struct virtio_crypto_akcipher_ctx` tracks selected virtio device, session validity, session id, and RSA key size. `virtio_crypto_alg_akcipher_init_session()` and `virtio_crypto_alg_akcipher_close_session()` issue control-queue create/destroy session commands. `virtio_crypto_rsa_set_key()` parses public/private RSA keys, discovers a device, selects raw or PKCS#1 padding parameters, and creates the session. `virtio_crypto_rsa_do_req()` builds data request headers, and `__virtio_crypto_akcipher_do_req()` copies sg input/output through temporary contiguous buffers and adds virtqueue sg entries. Registration functions maintain global `active_devs` counts.

Control flow: setting a key parses RSA modulus to calculate `max_size`, gets a compatible virtio device if needed, closes a prior session on rekey, and sends a control request with key bytes. Encrypt/decrypt sets the opcode and transfers the request to queue 0's crypto engine. The engine callback allocates request data, builds virtio headers and sg arrays, kicks the data virtqueue, and returns asynchronously. Completion callback maps virtio status to Linux errors, copies output bytes back to the request dst sg, updates `dst_len`, frees temporary buffers and request data, and finalizes the akcipher request.

State and persistence: state persists in `session_id` on the host backend and in the transform context while the key is active. Request state holds copied source/destination buffers, opcode, status byte, and allocated request header until completion. The global algorithm table stores active device counts to avoid duplicate registration.

Dependencies and integration points: depends on `crypto_engine`, `crypto/internal/akcipher.h`, RSA parser helpers, MPI for modulus sizing, scatterlist copy helpers, virtio crypto UAPI structures, and device-manager functions for device selection/refcounting. It registers `rsa` and `pkcs1pad(rsa)` with priority 150.

Risks and test signals: `virtio_crypto_rsa_exit_tfm()` calls `virtcrypto_dev_put(ctx->vcrypto)` without a visible NULL guard, so init/exit paths with no successful key should be checked. Contiguous buffer allocation scales with request size and may fail under memory pressure. PKCS#1 padded RSA forces SHA1 in session parameters because QEMU expects a hash setting, even though encrypt/decrypt do not use it. Test signals include RSA selftests for raw and pkcs1pad, public/private key parsing failure, rekey session replacement, invalid session status, short output length, request allocation failure, and unplug while sessions exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_akcipher_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_common.h

Purpose: private shared header for virtio crypto core, manager, and algorithm implementations.

Important APIs, types, and functions: `struct data_queue` wraps a virtqueue, lock, queue name, crypto engine, and completion work. `struct virtio_crypto` stores the virtio device, control and data queues, config work, control lock, negotiated capability masks, size limits, status/refcount/list/owner/id, and affinity state. `struct virtio_crypto_ctrl_request` packages control operation, input/status, and completion. `struct virtio_crypto_request` is the common data-queue request envelope with status, request header, sg pointer array, queue pointer, and algorithm callback. Prototypes expose device-manager, algorithm registration, control request, request clear, and NUMA node helper APIs.

Control flow: no standalone runtime flow, but the header defines how core callbacks deliver completed virtqueue buffers to per-algorithm callbacks and how algorithm code finds devices and queues requests.

State and persistence: all state is in-memory kernel/module state. Device capability masks mirror virtio config space, while session ids are held by algorithm-specific contexts.

Dependencies and integration points: includes virtio, crypto, spinlock, workqueue, AES/AEAD, crypto engine, and `uapi/linux/virtio_crypto.h`. The inline NUMA helper briefly pins the current CPU to derive a node for device selection.

Risks and test signals: correctness depends on every data request setting `alg_cb`, `dataq`, `req_data`, and `sgs` consistently so `virtcrypto_clear_request()` can clean up. Capability masks are split into low/high fields for some services, so algorithm numbers above 31 need coverage. Test signals are sparse/clang builds across enabled algorithm subsets, hot-unplug with pending requests, and NUMA fallback device selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_core.c

Purpose: virtio device driver core for virtio crypto. It probes virtio crypto devices, reads capability/configuration, allocates queues and crypto engines, handles control/data virtqueue callbacks, config changes, remove, and suspend/resume.

Important APIs, types, and functions: `virtcrypto_clear_request()` frees common request allocations. `virtio_crypto_ctrl_vq_request()` submits synchronous control queue commands. `virtcrypto_done_work()` drains completed data-queue buffers and invokes algorithm callbacks. `virtcrypto_find_vqs()`, `virtcrypto_init_vqs()`, and `virtcrypto_del_vqs()` manage virtqueues and per-data-queue engines. `virtcrypto_update_status()` starts/stops algorithm registration based on `VIRTIO_CRYPTO_S_HW_READY`. `virtcrypto_probe()`, `virtcrypto_remove()`, `virtcrypto_freeze()`, and `virtcrypto_restore()` implement driver lifecycle.

Control flow: probe requires virtio 1.0 and config access, rejects bad NUMA placement, allocates `virtio_crypto`, reads config fields, adds the device to the manager, initializes data/control queues, starts per-queue crypto engines, marks the device ready, updates hardware status, and installs config work. Data queue interrupts schedule bottom-half work that drains virtqueue buffers under a queue lock. Control queue callbacks complete synchronous waiters. Config changes schedule work that reads status and registers/unregisters algorithms through the manager.

State and persistence: per-device state includes capability masks, queue arrays, per-queue crypto engines, current status bits, refcount, list node, and affinity hints. Pending request state remains attached to virtqueue buffers until completion or detach during reset/remove. No persistent storage exists outside virtio device state.

Dependencies and integration points: integrates with the virtio bus through `module_virtio_driver`, virtio config access, vring size, virtqueue affinity, CPU masks, system bottom-half workqueue, crypto engine framework, and manager/algorithm modules. Device ID is `VIRTIO_ID_CRYPTO`.

Risks and test signals: `virtio_crypto_ctrl_vq_request()` waits without a timeout, so a broken host can hang control operations. `virtcrypto_find_vqs()` failure after allocating some per-queue engines relies on later reset/free paths and should be audited for partial cleanup. Affinity hints lack CPU hotplug notifier support per TODO. Test signals include virtio feature negotiation, queue count 0 fallback to 1, host status unknown-bit handling, config change start/stop, unplug with pending requests, suspend/resume, control queue failure, and multiple data queue initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_mgr.c

Purpose: global manager for virtio crypto devices and algorithm registration notifications.

Important APIs, types, and functions: file-static `virtio_crypto_table`, `num_devices`, and `table_lock` track up to `VIRTIO_CRYPTO_MAX_DEVICES`. `virtcrypto_devmgr_add_dev()` / `virtcrypto_devmgr_rm_dev()` add and remove devices. `virtcrypto_dev_get()` / `virtcrypto_dev_put()` manage per-device reference counts and module references. `virtcrypto_get_dev_node()` finds the least-used compatible started device near a NUMA node. `virtcrypto_dev_start()` and `virtcrypto_dev_stop()` register/unregister skcipher and akcipher algorithms. `virtcrypto_algo_is_supported()` checks service/algo bitmaps.

Control flow: probe adds devices to the table before queue setup. When hardware status becomes ready, `virtcrypto_dev_start()` registers algorithm families if supported. Algorithm setkey paths call `virtcrypto_get_dev_node()`, which scans same-node devices, falls back to any started compatible device, unlocks, then bumps references. Stop unregisters algorithms for the device.

State and persistence: the global list and device count persist for module lifetime. Each device stores an atomic user count and module owner pointer. Algorithm tables in separate files retain active device counts.

Dependencies and integration points: depends on mutex/list/module APIs, virtio crypto UAPI service constants, and common header structures. It is the bridge between core device status and crypto API algorithm availability.

Risks and test signals: `virtcrypto_dev_get()` increments the atomic before `try_module_get()` and does not roll back on failure, which is a refcount consistency risk. `virtcrypto_get_dev_node()` calls `virtcrypto_dev_get()` after dropping `table_lock`, so removal concurrency relies on higher-level algorithm/device lifetime constraints. Algorithm bit checking shifts `1u << algo` after subtracting 32 for high algorithms and needs bounds validation. Test signals are max-device limit, duplicate add, NUMA selection, fallback selection, module refcount failure injection, hot-unplug while transforms hold refs, and high-number algorithm masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_skcipher_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_skcipher_algs.c

Purpose: implements virtio crypto AES-CBC skcipher support for the Linux crypto API.

Important APIs, types, and functions: `struct virtio_crypto_skcipher_ctx` stores a selected device and separate encrypt/decrypt session ids. `virtio_crypto_alg_skcipher_init_session()` and close/session helpers manage host sessions through the control queue. `virtio_crypto_skcipher_setkey()` validates AES key sizes, selects a device, and creates both sessions. `__virtio_crypto_skcipher_do_req()` builds a virtio cipher data request with header, IV, src, dst, and status sg entries. `virtio_crypto_skcipher_encrypt()` / `decrypt()` validate block-aligned lengths and queue requests to crypto engine. `virtio_crypto_skcipher_finalize_req()` updates IV, frees allocations, and finalizes the request.

Control flow: setkey validates AES-128/192/256 and creates encrypt and decrypt sessions for `VIRTIO_CRYPTO_CIPHER_AES_CBC`. Encrypt/decrypt select data queue 0, attach callback state, reject zero or non-block-multiple input appropriately, and transfer to the queue's engine. The engine callback allocates request header and sg pointer array, copies the IV to DMA-safe memory, snapshots decrypt IV from the last source block, checks total request size against device `max_size`, submits to the virtqueue, and returns asynchronously. Completion maps virtio status, updates output IV from the last ciphertext block on encryption, frees IV/request allocations, and finalizes.

State and persistence: transform state is selected virtio device plus encrypt/decrypt session ids. Request state includes allocated virtio data header, sg array, DMA-safe IV buffer, status byte, and data-queue pointer. Algorithm registration state is an `active_devs` count in the static algorithm table.

Dependencies and integration points: depends on crypto skcipher/engine APIs, AES constants, scatterwalk, virtqueue locking, manager device selection, control queue helpers, and virtio crypto UAPI. Registers `cbc(aes)` as `virtio_crypto_aes_cbc` with priority 150.

Risks and test signals: only CBC is implemented despite broader Kconfig selections. The code uses `sg_nents(req->dst)` rather than `sg_nents_for_len()` for dst, so oversized dst lists affect sg count and request size. IV update rules are correctness-sensitive, especially in-place decrypt. `virtqueue_kick()` is called even if `virtqueue_add_sgs()` returns an error. Test signals include AES-CBC selftests, 128/192/256-bit keys, zero length, non-block length rejection, max_size rejection, rekey close/recreate, virtqueue add failure, status mapping, and unplug while sessions are live.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/virtio/virtio_crypto_skcipher_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/Makefile

Purpose: Kbuild rules for Xilinx/AMD crypto drivers.

Important APIs, types, and functions: maps `CONFIG_CRYPTO_DEV_XILINX_TRNG` to `xilinx-trng.o`, `CONFIG_CRYPTO_DEV_ZYNQMP_AES` to `zynqmp-aes-gcm.o`, and `CONFIG_CRYPTO_DEV_ZYNQMP_SHA3` to `zynqmp-sha.o`.

Control flow: no runtime flow. The file determines which driver objects are compiled and linked based on kernel configuration.

State and persistence: no runtime state.

Dependencies and integration points: integrates with the parent crypto Kbuild and the corresponding Kconfig options outside this subset.

Risks and test signals: build coverage should verify each config can be built independently and together. Missing Kconfig dependencies would surface as unresolved firmware, crypto, or hwrng symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/xilinx-trng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/xilinx-trng.c

Purpose: AMD/Xilinx Versal True Random Number Generator driver. It registers both a crypto RNG named `stdrng` with driver `xilinx-trng` and an hwrng provider backed by Versal TRNG hardware.

Important APIs, types, and functions: `struct xilinx_rng` stores MMIO base, scratchpad, AES derivation-function key, mutex, and `hwrng`. `xtrng_collect_random_data()` starts PRNG/TRNG output and reads 16-byte chunks from output registers. `xtrng_reseed_internal()` enables entropy mode, collects seed material, runs `crypto_drbg_ctr_df()`, writes external seed registers, and triggers reseed. `xtrng_random_bytes_generate()` enables PRNG mode, reads random bytes, then reseeds. Crypto RNG hooks are `xtrng_trng_generate()`, `xtrng_trng_seed()`, and `xtrng_trng_init()`. HWRNG read is `xtrng_hwrng_trng_read()`. Probe/reset/remove own registration and sanitization.

Control flow: probe maps MMIO, allocates AES key and derivation-function scratchpad, resets hardware, performs an initial reseed, sets the global device pointer, initializes mutex, registers crypto RNG, then registers hwrng. Generate/read paths serialize through the mutex, collect requested bytes with optional polling waits, reseed after each generation, and return either crypto success or number of bytes read. Remove unregisters providers, zeros seed registers, holds reset, and clears the global pointer.

State and persistence: hardware state includes control, status, reset, oscillator enable, external seed, personalization, and output registers. Software state includes the global `xilinx_rng_dev`, mutex, scratchpad buffer, and AES key schedule storage. Seed-related buffers/registers are explicitly zeroed in remove and some error paths.

Dependencies and integration points: depends on platform/OF compatible `"xlnx,versal-trng"`, MMIO polling, hwrng framework, crypto RNG API, DRBG CTR derivation function, AES internals, and firmware headers.

Risks and test signals: `xtrng_hwrng_trng_read()` returns the last generation return value rather than total bytes copied, which may underreport successful multi-block reads. `xtrng_readwrite32()` takes a `u8 value` while masks include bits above 7, so setting `TRNG_CTRL_EUMODE_MASK` through this helper would not work if used that way; current high-bit writes mostly use `iowrite32()`. Frequent reseed-after-generate may affect throughput. Test signals include crypto RNG selftests, hwrng reads with wait and non-wait modes, entropy/reseed timeout injection, register zeroization on remove, concurrent readers, and partial byte requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/xilinx-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-aes-gcm.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-aes-gcm.c

Purpose: Xilinx/AMD ZynqMP and Versal AES-GCM/PAES-GCM AEAD acceleration driver using platform firmware secure monitor APIs. It registers `gcm(aes)` and `gcm(paes)` variants selected by platform family/features.

Important APIs, types, and functions: `struct xilinx_aead_dev`, `struct xilinx_aead_alg`, and `struct xilinx_aead_tfm_ctx` hold device, algorithm, key DMA, auth size, key source, and fallback state. ZynqMP execution is `zynqmp_aes_aead_cipher()` using `zynqmp_pm_aes_engine()`. Versal execution is `versal_aes_aead_cipher()` using `versal_pm_aes_op_init()`, AAD update, enc/dec update, final, and volatile key write/zero APIs. Fallback checks are `zynqmp_fallback_check()` and `versal_fallback_check()`. Key paths include KUP software key setters and PAES hardware key-info setters. `xilinx_handle_aes_req()` finalizes crypto-engine requests.

Control flow: module init registers a platform driver and synthetic platform device. Probe asks firmware helper `xlnx_get_crypto_dev_data()` for family-specific algorithms, allocates a singleton device, sets DMA mask, starts a crypto engine, and registers all sentinel-terminated AEAD algorithms. Setkey either copies software keys to DMA memory or records a validated hardware key selector magic/type. Encrypt/decrypt set request op, reject invalid hardware-key/fallback combinations, choose software fallback for unsupported software-key cases, or queue to the crypto engine. Engine execution copies sg input into a linear DMA buffer, builds firmware operation descriptors and IV, calls the firmware API sequence, copies output/tag back, clears volatile keys where needed, unmaps DMA, zeroes buffers, and finalizes.

State and persistence: singleton `aead_dev` persists while the module is loaded. Per-transform state includes key buffer/DMA address, key length, auth size, key source, and optional fallback AEAD. Hardware-key PAES transforms do not own key bytes, only selectors. Request state is only operation direction. Firmware and secure hardware hold transient AES state; volatile Versal user keys are explicitly zeroed after operation.

Dependencies and integration points: depends on firmware APIs in `linux/firmware/xlnx-zynqmp.h`, platform family feature discovery, DMA mapping, crypto engine, AEAD crypto API, GCM constants, scatterwalk, and fallback software AEAD. ZynqMP uses 32-bit DMA mask; Versal uses 64-bit.

Risks and test signals: linearizing requests can be costly and allocation-failure prone. ZynqMP hardware path supports only limited software-key cases: no AAD, 256-bit keys, word-aligned lengths, and normal tag size on decrypt. Versal rejects AES-192 and requires aligned assoc/crypt lengths. `xilinx_aes_aead_remove()` exits the engine before unregistering algorithms, which should be checked against in-flight requests. Hardware-key selector validation and fallback denial for PAES are critical. Test signals include AES-GCM selftests for software and PAES keys, tag mismatch mapping to `-EBADMSG`, AAD alignment fallback, unsupported hardware-key requests returning `-EOPNOTSUPP`, DMA mapping failures, volatile key zero calls, and module init/exit singleton behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-aes-gcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-sha.c

Purpose: ZynqMP SHA3-384 hardware acceleration driver. It registers a `sha3-384` shash implementation backed by firmware for one-shot digest and by software fallback for init/update/finup streaming operations.

Important APIs, types, and functions: `struct zynqmp_sha_drv_ctx` owns the shash algorithm and device pointer. `struct zynqmp_sha_tfm_ctx` stores device and fallback shash. `zynqmp_sha_init_tfm()` allocates fallback. `zynqmp_sha_init()`, `zynqmp_sha_update()`, and `zynqmp_sha_finup()` import/export fallback state. `__zynqmp_sha_digest()` calls `zynqmp_pm_sha_hash()` INIT/UPDATE/FINAL using coherent update/final buffers. `zynqmp_sha_digest()` serializes hardware digest with `zynqmp_sha_lock`.

Control flow: probe verifies firmware API availability, sets 32-bit DMA mask, registers the shash algorithm, stores driver context, and allocates coherent update and final buffers. Digest initializes firmware SHA, chunks input into a 4 KiB coherent update buffer, flushes icache for each copied chunk, issues update calls, issues final into the final buffer, copies digest out, and zeroes final buffer. Remove frees coherent buffers and unregisters the shash.

State and persistence: global DMA addresses and buffers `update_dma_addr`, `final_dma_addr`, `ubuf`, and `fbuf` persist for the device lifetime. A global spinlock serializes firmware hardware use. Per-transform fallback state persists in the shash context. No disk state exists.

Dependencies and integration points: depends on firmware SHA API, DMA coherent allocation, crypto shash internals, SHA3 constants, fallback shash allocation, and platform driver matching by name `"zynqmp-sha3-384"`.

Risks and test signals: `zynqmp_sha_init_tfm()` compares `crypto_shash_descsize(hash)` with `crypto_shash_statesize(tfm_ctx->fbk_tfm)` before assigning `tfm_ctx->fbk_tfm = fallback_tfm`, so it appears to read an uninitialized pointer; this is a high-priority review/test target. Digest uses `flush_icache_range()` rather than standard DMA sync on coherent memory, which may be architecture-sensitive. Only digest is hardware accelerated; streaming paths are fallback. Test signals include `tcrypt`/crypto selftests for sha3-384 digest, init/update/final state export/import, fallback allocation failure, probe allocation unwind, concurrent digest serialization, empty input, multi-4K input, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/cxl/Kconfig

Purpose: top-level configuration menu for Compute Express Link support, including bus core, PCI/memory devices, ACPI platform discovery, persistent memory, regions, RAS, ATL, and optional EDAC/features.

Important APIs, types, and functions: `menuconfig CXL_BUS` enables the subsystem and selects firmware/PCI DOE support. Key options are `CXL_PCI`, `CXL_MEM_RAW_COMMANDS`, `CXL_ACPI`, `CXL_PMEM`, `CXL_MEM`, `CXL_FEATURES`, EDAC feature toggles, internal `CXL_PORT`, `CXL_SUSPEND`, `CXL_REGION`, `CXL_REGION_INVALIDATION_TEST`, `CXL_MCE`, `CXL_RAS`, and `CXL_ATL`.

Control flow: Kconfig dependencies determine which CXL source files compile and which stubs in headers are active. `CXL_ACPI` defaults to `CXL_BUS` and selects `CXL_PORT`; `CXL_REGION` defaults to enabled with sparsemem; `CXL_ATL` is enabled only with region support, ACPI PRMT, and AMD_NB.

State and persistence: no runtime state. It controls kernel configuration state and available module/built-in features.

Dependencies and integration points: integrates with PCI, ACPI, LIBNVDIMM, sparsemem, FWCTL, EDAC, tracing/RAS, x86 MCE, and platform firmware features. These options gate the Makefile and `core.h` APIs used by ACPI/CDAT/ATL files.

Risks and test signals: configuration combinations are the risk, especially built-in ordering, optional region/RAS/features stubs, and EDAC dependencies. Test signals include allyesconfig/allmodconfig, CXL_BUS without CXL_REGION, CXL_ACPI as module, CXL_ATL dependency satisfaction, and production kernels keeping `CXL_REGION_INVALIDATION_TEST` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cxl/Makefile

Purpose: top-level Kbuild orchestration for CXL driver objects and modules.

Important APIs, types, and functions: always descends into `core/`, then builds `cxl_port.o`, `cxl_acpi.o`, `cxl_pmem.o`, `cxl_mem.o`, and `cxl_pci.o` according to config. Object aliases map modules to `port.o`, `acpi.o`, `pmem.o security.o`, `mem.o`, and `pci.o`.

Control flow: no runtime logic, but comments document built-in link order constraints: core first, port before platform root drivers, mem/pmem before endpoint drivers, and PCI last to mirror hardware enumeration.

State and persistence: no runtime state.

Dependencies and integration points: integrates with Kbuild and Kconfig symbols from `drivers/cxl/Kconfig`. Link order affects CXL bus availability during early platform and PCI discovery.

Risks and test signals: reordering can break built-in boot discovery, especially ACPI root ports and endpoint attach timing. Test signals include built-in boot with ACPI CEDT, modular load ordering, softdeps, and immediate memdev/port enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/acpi.c

Purpose: ACPI platform driver for CXL root discovery. It parses CEDT tables, creates CXL root ports and root decoders, registers host bridge downstream/upstream ports, reflects CXL fixed windows in iomem resources, wires QoS class lookup, and triggers bus rescans.

Important APIs, types, and functions: `cxl_do_xormap_calc()` applies XOR interleave maps and is exported for `cxl_translate`. `cxl_parse_cxims()` parses CXIMS XOR map entries. `cxl_acpi_cfmws_verify()` and `__cxl_parse_cfmws()` validate CFMWS windows and create root decoders. `cxl_acpi_evaluate_qtg_dsm()` / `cxl_acpi_qos_class()` query ACPI QTG IDs. `add_host_bridge_dport()` and `add_host_bridge_uport()` discover ACPI0016 host bridges from CHBS entries. `add_cxl_resources()`, `remove_cxl_resources()`, and `pair_cxl_resource()` manage iomem resource reflection. `cxl_acpi_probe()` orchestrates the full root setup.

Control flow: probe sets a root lock class, allocates a private CXL resource tree, creates a CXL root, installs QoS and optional PRM address-translation ops, scans ACPI host bridges as root dports, registers cleanup for resources, parses all CFMWS windows into root decoders, inserts public CXL iomem resources with overlap trimming, pairs root decoders to public resources, rescans host bridges as upstream CXL ports, optionally creates a root nvdimm bridge for PMEM windows, and calls `cxl_bus_rescan()`. Module init is `subsys_initcall_sync()` so CXL windows are available before consumers such as dax/hmem.

State and persistence: root topology state is devm-managed under the platform device. Root decoders hold HPA ranges, interleave targets, granularity, flags, optional XOR map platform data, cache size, QoS class, and public resource pointer. A private resource tree tracks CXL windows and public resource pairing for cleanup.

Dependencies and integration points: depends on ACPI CEDT/CFMWS/CHBS/CXIMS parsing, ACPI0017 and ACPI0016 device model, PCI root discovery, CXL core port/decoder APIs, HMAT extended cache data, ACPI QTG _DSM, iomem resource APIs, PMEM bridge support, and PRM translation setup from `atl.c`.

Risks and test signals: malformed firmware tables are a central risk; most single-window parse failures are logged but do not fail driver load. XOR interleave requires matching CXIMS or decoder creation fails. Resource expansion/trimming must preserve System RAM conflicts correctly. Mixed CHBS versions disable eRCD support. Test signals include CEDT parsing for modulo and XOR windows, invalid alignment/length, CHBS CXL 1.1 vs 2.0, RCH and VH host bridge paths, QTG _DSM package validation, overlapping CXL/System RAM resources, PMEM bridge creation, and boot ordering with built-in CXL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/Makefile

Purpose: Kbuild rules for the CXL core library/module.

Important APIs, types, and functions: builds `cxl_core.o` under `CONFIG_CXL_BUS` and `suspend.o` under `CONFIG_CXL_SUSPEND`. `cxl_core-y` includes port, pmem, regs, memdev, mbox, pci, hdm, pmu, cdat, optional trace, region, MCE, features, EDAC, RAS, RCH RAS, and ATL objects. `ccflags-y` adds the parent CXL include path and trace include settings.

Control flow: no runtime logic. Object composition determines which core services and exported symbols are available.

State and persistence: no runtime state.

Dependencies and integration points: integrates with the top-level CXL Makefile and Kconfig feature gates. `cdat.o` is always part of core when CXL_BUS is enabled; `atl.o` is conditional on `CONFIG_CXL_ATL`.

Risks and test signals: optional object combinations must match declarations/stubs in `core.h`. Trace include path flags are sensitive to build location. Test signals are build coverage across CONFIG_CXL_REGION/RAS/FEATURES/ATL permutations and module namespace export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/atl.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/atl.c

Purpose: AMD PRM-backed CXL address translation support. It installs a root operation that translates endpoint DPA/HPA ranges into system physical address ranges for normalized addressing platforms.

Important APIs, types, and functions: `prm_cxl_dpa_spa()` calls an ACPI PRM handler identified by `prm_cxl_dpa_spa_guid` with PCI segment/bus/devfn and DPA, returning SPA or `ULLONG_MAX`. `cxl_prm_setup_root()` is the `translation_setup_root` callback that validates endpoint/root assumptions, translates range endpoints, derives interleave ways/granularity, and marks decoders locked/normalized. `cxl_setup_prm_address_translation()` probes PRM support and installs the callback on a CXL root.

Control flow: ACPI root probe calls `cxl_setup_prm_address_translation()`. That verifies the host matches ACPI CXL root driver data and that the PRM handler is supported. Later, region/root setup invokes `cxl_prm_setup_root()` for endpoint decoder contexts. The callback only handles normalized addressing where HPA start equals endpoint DPA start and endpoint interleave is passthrough, translates start/end through PRM, aligns the resulting SPA range to 256 MiB, checks contiguity, probes offsets to determine interleave granularity up to 16 MiB, sets lock/normalized flags, and updates the region context.

State and persistence: no persistent local state. It updates `struct cxl_region_context` and `struct cxl_decoder` flags during setup. The PRM handler and platform firmware provide translation data.

Dependencies and integration points: depends on ACPI PRMT, PCI device identity, CXL core region/decoder structures, `cxl_memdev` endpoint relationships, and CXL root ops installed from `acpi.c`.

Risks and test signals: PRM failures return `-ENXIO` and leave translation unavailable. The granularity detection assumes probing `base + gran` reveals interleave transition behavior. The function locks decoders because the current kernel cannot reprogram normalized-addressing endpoint setups. Test signals include PRM unsupported vs supported platforms, non-PCI endpoints, non-passthrough endpoints, failed start/end translation, non-contiguous SPA ranges, multi-way/granularity derivation, and decoder flag updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/atl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/cdat.c -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/cdat.c

Purpose: parses CXL CDAT performance tables and calculates endpoint, switch, and region access coordinates, QoS classes, and shared upstream bandwidth for CXL memory regions.

Important APIs, types, and functions: `struct dsmas_entry` holds DPA range, DSMAS handle, CDAT/combined coordinates, entries, and QoS class. `cdat_dsmas_handler()`, `cdat_dslbis_handler()`, and `cdat_sslbis_handler()` parse DSMAS, DSLBIS, and SSLBIS subtables. `cxl_endpoint_parse_cdat()` parses endpoint CDAT, combines endpoint coordinates, maps QTG/QoS class, updates memdev partition perf, and calls `cxl_memdev_update_perf()`. `cxl_switch_parse_cdat()` parses switch SSLBIS into dport coordinates. `cxl_coordinates_combine()` combines path coordinates by adding latency and taking minimum nonzero bandwidth. Region helpers gather endpoint/switch/root-port/host-bridge bandwidth and update `cxl_region` coordinates.

Control flow: endpoint CDAT parsing builds an xarray of DSMAS entries by handle, fills per-entry CDAT latency/bandwidth from DSLBIS, retrieves endpoint PCI/performance coordinates, asks the CXL root for a QoS class, writes matching partition performance data, verifies QoS class against reachable root decoders, and publishes updates. Switch parsing scans SSLBIS entries for the downstream port id or wildcard and sets dport coordinates. Region bandwidth update walks from endpoints upward: gather endpoint bandwidth under upstream devices, iteratively fold switch levels until root ports, aggregate root-port and host-bridge levels, then update region read/write bandwidth. Region latency calculation separately accumulates worst latency and total bandwidth from endpoint partition perf.

State and persistence: parsed CDAT state is transient xarray data during parsing, then persisted in `cxlds->part[i].perf`, dport `coord`, and region `coord` fields. Invalid or unmatched QoS data is reset to `CXL_QOS_CLASS_INVALID`. No disk state exists.

Dependencies and integration points: depends on ACPI CDAT parser helpers, HMAT coordinate units, xarray, CXL root QoS ops from `acpi.c`, endpoint memdev partition state, CXL region/decoder locks (`cxl_rwsem.dpa` and `.region`), PCI bandwidth helpers, switch dport bandwidth helpers, and CXL namespace exports.

Risks and test signals: firmware table validation and unit normalization are critical; invalid lengths, missing DSMAS/DSLBIS, zero/overflow values, and unsupported data types should degrade cleanly. Shared upstream bandwidth logic rejects asymmetric topologies and restricted CXL devices. `cxl_qos_class_verify()` hides QoS if no root decoder/host bridge match exists, which can surprise userspace but prevents stale classes. Test signals include CDAT malformed table fuzzing, multiple DSMAS handles and partitions, QTG lookup success/failure, switch SSLBIS wildcard and specific port matching, direct-attached vs switched regions, asymmetric hierarchy, DPA range containment failure, and lockdep for required DPA lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/cdat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/core.h -->
# sources/distributed-fs/ceph-client/drivers/cxl/core/core.h

Purpose: private CXL core header declaring shared internal APIs, types, conditional stubs, locks, and device type/attribute exports used across CXL core and platform drivers.

Important APIs, types, and functions: declares CXL nvdimm/pmu types and base attributes; `enum cxl_detach_mode`; `struct cxl_region_context` for endpoint translation setup; region APIs and macros gated by `CONFIG_CXL_REGION`; mailbox query/send APIs; DPA allocation/free helpers; RCRB helpers and PCI capability masks; global `struct cxl_rwsem cxl_rwsem`; memdev/mbox init; poison/RAS/feature APIs; PCI latency/bandwidth and switch dport bandwidth helpers; `port_to_host()` and `dport_to_host()` host-device helpers; HDM decode and possible-dport APIs; and `cxl_rcd_component_reg_phys()`.

Control flow: the header itself has no runtime flow, but conditional inline stubs define no-op behavior when `CONFIG_CXL_REGION` or `CONFIG_CXL_RAS` is disabled. Helper functions derive host devices based on whether a port is root, first-level, or nested.

State and persistence: declares the global CXL rwsems that serialize region HPA/interleave changes and DPA-space changes. Other state is owned by implementation files and devices.

Dependencies and integration points: includes CXL mailbox definitions and Linux rwsem. It is included by CXL core files such as CDAT/ATL and by drivers needing internal CXL APIs. Namespace exports in implementation files correspond to declarations here.

Risks and test signals: stale declarations or stubs can hide missing feature wiring in disabled configs. Locking comments on `cxl_rwsem.region` and `.dpa` define important invariants for region/DPA operations. Test signals include compile coverage with region/RAS/features disabled, lockdep assertions in CDAT/region paths, host helper behavior for root and nested ports, and namespace/export consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cxl/core/core.h -->
