# subset-b-001226 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hifn_795x.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hifn_795x.c

## Purpose
This file is a complete PCI driver for HIFN 7955/7956 crypto accelerator chips. It exposes asynchronous Linux Crypto API skcipher implementations for AES, DES, and 3DES in ECB/CBC modes, optionally registers the chip RNG as an `hwrng`, and owns all device bring-up, DMA descriptor ring handling, IRQ/tasklet completion, and teardown.

## Important APIs, Types, and Functions
Key private types are `struct hifn_device`, `struct hifn_dma`, `struct hifn_desc`, `struct hifn_context`, `struct hifn_request_context`, and `struct hifn_crypto_alg`. `struct hifn_dma` contains command, source, destination, and result descriptor rings plus command/result bounce buffers. `struct hifn_device` stores PCI BAR mappings, coherent descriptor memory, ring-associated skcipher requests in `sa[]`, the `crypto_queue`, tasklet, watchdog work item, RNG state, and counters such as `started`, `active`, `success`, and `reset`.

Core hardware helpers are `hifn_read_0/1()`, `hifn_write_0/1()`, `hifn_reset_dma()`, `hifn_init_dma()`, `hifn_init_pll()`, `hifn_init_registers()`, `hifn_init_pubrng()`, and `hifn_enable_crypto()`. Request setup flows through `hifn_setup_crypto_req()`, `hifn_handle_req()`, `hifn_setup_session()`, `hifn_setup_dma()`, `hifn_setup_cmd_desc()`, `hifn_setup_src_desc()`, `hifn_setup_dst_desc()`, and `hifn_setup_res_desc()`. Completion flows through `hifn_interrupt()`, `hifn_tasklet_callback()`, `hifn_clear_rings()`, `hifn_process_ready()`, and `hifn_complete_sa()`.

The registered skcipher templates are `cbc(des3_ede)`, `ecb(des3_ede)`, `cbc(des)`, `ecb(des)`, `ecb(aes)`, and `cbc(aes)`. Module entry is `hifn_init()`/`hifn_fini()`, PCI binding is `hifn_probe()`/`hifn_remove()`, and the module parameter `hifn_pll_ref` selects `ext` or `pci` reference clock plus optional MHz value.

## Control Flow
Module initialization validates `hifn_pll_ref`, then registers the PCI driver. Probe enables the PCI function, sets 32-bit DMA, requests BARs, maps three BARs, allocates coherent `struct hifn_dma`, initializes the tasklet and crypto queue, requests the shared IRQ, starts the device, optionally registers the RNG, registers all skcipher algorithms, and starts a one-second delayed watchdog.

Device start resets DMA, performs the HIFN unlock/signature sequence, resets the processing unit, initializes descriptor rings and hardware registers, initializes the PLL, and enables public/RNG units. A skcipher request sets operation/type/mode in `hifn_request_context`, queues or directly prepares the DMA transaction, and returns `-EINPROGRESS` on successful hardware submission. Source and destination scatterlist entries are converted to DMA descriptors; destination entries with unsupported alignment are redirected through temporary page-backed scatterlist cache entries and copied back on completion.

The interrupt handler acknowledges DMA/engine/public-key bits, handles overflow and abort status, toggles command-wait interrupts, and schedules the tasklet. The tasklet scans result/source/command/destination rings for descriptors whose valid bit has been cleared by hardware, completes associated skcipher requests, releases `sa[]` entries, and drains the software crypto queue while ring space remains. The delayed work item disables idle rings and acts as a watchdog; if submitted requests stop making progress for repeated ticks, it completes visible stuck requests with `-ENODEV`, resets DMA, restarts hardware, and schedules the tasklet.

## State and Persistence Behavior
There is no filesystem persistence. Persistent-for-module state includes global `hifn_dev_number`, `hifn_pll_ref`, registered crypto algorithms, and optional hwrng registration. Per-device runtime state lives in `struct hifn_device`, coherent descriptor memory, BAR registers, the software queue, ring indices (`cmdi/srci/dsti/resi`, usage counts, and cleanup cursors), `sa[]` request pointers keyed by result slot, and watchdog counters. Per-transform state stores key material in `struct hifn_context`; request-local state stores IV metadata and temporary walk pages.

## Dependencies and Integration Points
The driver depends on PCI, MMIO, Linux DMA mapping, scatterlists, tasklets, delayed work, the skcipher crypto API, DES key verification helpers, and optional `hwrng`. It integrates with module/device tables through `MODULE_DEVICE_TABLE(pci, hifn_pci_tbl)`, registers algorithms with `crypto_register_skcipher()`, and exposes RNG data through `hwrng_register()` when configured.

## Risks and Edge Cases
DMA source/destination mappings are created per request but this file does not visibly call `dma_unmap_page()` for the per-page mappings after completion; the research signal is a potential DMA mapping lifetime/leak concern unless the platform treats this path specially. Misaligned destination handling is fragile: one branch logs a message and calls `BUG()` if a temporary page cannot cover the required aligned chunk. `hifn_setkey()` uses `verify_skcipher_des_key()` even for AES templates, so key validation behavior should be checked against the kernel version represented by this tree. Several ring fields are `volatile` and are manipulated from IRQ, tasklet, workqueue, and request contexts; lock coverage is partial and should be stress-tested. The watchdog reset path force-completes requests and restarts hardware, which is useful for liveness but can mask underlying ring-accounting bugs.

## Test Signals
Useful tests include module load/unload against supported PCI IDs, skcipher known-answer tests for all registered modes and key sizes, asynchronous queue saturation around `HIFN_QUEUE_LENGTH`, scatterlists with misaligned destination offsets/lengths, forced IRQ overflow/abort paths, watchdog reset behavior under a hung device, RNG read interval behavior, and probe/remove error unwinding with fault injection for BAR mapping, coherent allocation, IRQ request, RNG registration, and algorithm registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hifn_795x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the HiSilicon crypto accelerator family: SEC, SEC2, the shared QM queue-manager module, ZIP, HPRE, and TRNG. It is the dependency and feature-selection gate that decides which driver subdirectories and shared objects become buildable.

## Important APIs, Types, and Functions
This is declarative Kconfig, so the important symbols are `CRYPTO_DEV_HISI_SEC`, `CRYPTO_DEV_HISI_SEC2`, `CRYPTO_DEV_HISI_QM`, `CRYPTO_DEV_HISI_ZIP`, `CRYPTO_DEV_HISI_HPRE`, and `CRYPTO_DEV_HISI_TRNG`. HPRE selects `CRYPTO_DEV_HISI_QM`, `CRYPTO_DH`, `CRYPTO_RSA`, and `CRYPTO_ECDH`; SEC2 selects QM plus skcipher, AEAD, authenc, HMAC, hash, and SM4 support.

## Control Flow
There is no runtime control flow. At configuration time, selecting a public accelerator symbol pulls in the crypto algorithms and shared dependencies it needs. Hidden symbol `CRYPTO_DEV_HISI_QM` is selected by users such as SEC2, ZIP, and HPRE instead of being directly user-facing.

## State and Persistence Behavior
The file persists build configuration state through kernel `.config` symbols. It does not create runtime state. Tristate choices determine whether drivers are built-in, modules, or absent.

## Dependencies and Integration Points
The symbols constrain builds to ARM64 or compile-test cases, PCI MSI where PCI queue-manager devices are used, ACPI for modern HiSilicon PCI accelerators, and optional UACCE compatibility through `depends on UACCE || UACCE=n`. The Makefile in the same directory consumes these symbols to include subdirectories and objects.

## Risks and Edge Cases
Misconfigured dependencies here can produce build failures or runtime-inaccessible hardware support. The `UACCE || UACCE=n` pattern prevents incompatible modular combinations and should remain aligned with the queue-manager implementation. HPRE help text mentions RSA and DH but the driver also registers ECDH when supported, so user-facing text may lag actual functionality.

## Test Signals
Build matrix signals are `allyesconfig`/`allmodconfig`, ARM64 native configs, `COMPILE_TEST && 64BIT`, configurations with and without UACCE, and verifying that enabling HPRE selects QM and required asymmetric crypto algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Makefile

## Purpose
This Makefile maps HiSilicon crypto Kconfig symbols to built objects and subdirectories. It builds shared queue-manager support and routes accelerator-specific drivers to `hpre/`, `sec/`, `sec2/`, `zip/`, and `trng/`.

## Important APIs, Types, and Functions
There are no C APIs. The important build targets are `obj-$(CONFIG_CRYPTO_DEV_HISI_HPRE) += hpre/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_SEC) += sec/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_SEC2) += sec2/`, `obj-$(CONFIG_CRYPTO_DEV_HISI_QM) += hisi_qm.o`, `obj-$(CONFIG_CRYPTO_DEV_HISI_ZIP) += zip/`, and `obj-$(CONFIG_CRYPTO_DEV_HISI_TRNG) += trng/`. The composite `hisi_qm-objs` is `qm.o sgl.o debugfs.o`.

## Control Flow
Kernel build logic expands each `obj-y` or `obj-m` based on the corresponding Kconfig symbol. When `CRYPTO_DEV_HISI_QM` is enabled, the shared `hisi_qm` module/object includes queue management, scatter-gather-list support, and debugfs support.

## State and Persistence Behavior
No runtime state is maintained. The file persists build composition rules in source control and affects module boundaries.

## Dependencies and Integration Points
This file is coupled to `Kconfig` and to object names in the HiSilicon crypto tree. HPRE has its own subdirectory Makefile that composes `hisi_hpre.o` from `hpre_main.o` and `hpre_crypto.o`.

## Risks and Edge Cases
If a source file is renamed or a Kconfig symbol changes, this Makefile is a build-break point. Because `hisi_qm-objs` includes `debugfs.o`, debugfs support is built whenever QM is built; feature assumptions must match the C code's config guards.

## Test Signals
Build with individual HiSilicon symbols enabled as modules and built-ins, verify `hisi_qm.o` composition, and verify that HPRE builds pull both the parent directory support and the `hpre/` subdirectory objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/debugfs.c

## Purpose
This file implements shared debugfs and diagnostics support for HiSilicon accelerator queue-manager (`hisi_qm`) devices. It exposes queue-manager registers, live status, device usage, command-driven queue/context dumps, per-device counters, and register-difference snapshots used by accelerator-specific drivers such as HPRE.

## Important APIs, Types, and Functions
The exported functions are `hisi_qm_regs_dump()`, `hisi_qm_regs_debugfs_init()`, `hisi_qm_regs_debugfs_uninit()`, `hisi_qm_acc_diff_regs_dump()`, `hisi_qm_show_last_dfx_regs()`, `hisi_qm_debug_init()`, and `hisi_qm_debug_regs_clear()`. Internal debugfs file operations include `qm_cmd_fops`, `qm_debug_fops`, `qm_regs_fops`, `qm_usage_fops`, `qm_diff_regs_fops`, `qm_state_fops`, and `qm_status_fops`.

Command dump support is table-driven through `struct qm_cmd_dump_item`, with commands for `sqc`, `cqc`, `eqc`, `aeqc`, `sq`, `cq`, `eq`, and `aeq`. Register-difference support uses `struct dfx_diff_registers` arrays, initialized by `dfx_regs_init()` and freed by `dfx_regs_uninit()`.

## Control Flow
`hisi_qm_debug_init()` creates the `qm` debugfs directory under an accelerator-provided root, adds PF-only state/current selector files, adds `regs`, `cmd`, `status`, device state/timeout controls, atomic counter files, optional `diff_regs`, optional `dev_usage`, and optional algorithm QoS debugfs. Reads of register files call `hisi_qm_regs_dump()` under `hisi_qm_get_dfx_access()` to avoid racing reset/suspend. Writes to selector files parse small numeric buffers and update current PF/VF or queue selection registers under per-file locks.

The command write path copies at most `QM_DBG_WRITE_LEN` bytes from userspace, strips a trailing newline, takes DFX access, rejects work while QM is stopped, parses the first token, and dispatches to dump functions. SQC/CQC dumps prefer mailbox hardware context reads and fall back to software cached contexts under `qps_lock`. SQ/CQ/EQ/AEQ dumps read queue memory directly after validating queue and element IDs. Sensitive DMA address fields are masked before printing SQC/CQC/SQE data.

Register snapshot initialization captures baseline QM and accelerator register regions for later diff output. Last-register support snapshots selected QM registers and can print changes during reset/error handling.

## State and Persistence Behavior
There is no disk persistence. Runtime state is stored in `qm->debug`, including debugfs dentries, current selected queue/function count, `qm_diff_regs`, `acc_diff_regs`, and `qm_last_words`. Atomic counters in `struct qm_dfx` are exposed through debugfs and can be reset by writing zero. Hardware state is affected by writes to current selector registers and read-clear enable registers.

## Dependencies and Integration Points
This file depends on the shared queue-manager definitions in `<linux/hisi_acc_qm.h>` and `qm_common.h`, Linux debugfs, seq_file, mailbox helpers such as `qm_set_and_get_xqc()`, reset/suspend gating through `hisi_qm_get_dfx_access()`, and accelerator-specific register ranges supplied to `hisi_qm_regs_debugfs_init()`. HPRE calls these exports for common register dumps and diff snapshots.

## Risks and Edge Cases
Debugfs write paths are privileged by permissions but still user-triggered; bounds and token validation are therefore important. Some dump paths read queue memory after validating against current `qm->qp_num` and queue depths, but queue lifetime depends on `qps_lock` coverage and DFX access. `qm_status_read()` indexes `qm_s[]` using `atomic_read(&qm->status.flags)` and assumes only expected status values. Register-difference baselines can become stale across reset unless refreshed by the accelerator lifecycle. Read-clear controls can alter hardware counters and should not be treated as passive observation.

## Test Signals
Test debugfs creation for PF and VF devices, command parser handling of valid commands, extra tokens, oversized writes, invalid queue IDs, and newline-terminated writes. Exercise reset/suspend paths where `hisi_qm_get_dfx_access()` returns errors or `-EAGAIN`. Validate that SQC/CQC/SQE dumps mask address fields, diff registers report only changed values, read-clear counter reset works, and `hisi_qm_debug_regs_clear()` clears current selectors and read-clear counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/Makefile

## Purpose
This Makefile defines the HPRE driver object composition. When `CONFIG_CRYPTO_DEV_HISI_HPRE` is enabled, it builds the module/object `hisi_hpre.o` from the device-management file `hpre_main.o` and the crypto algorithm implementation file `hpre_crypto.o`.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build rule is `obj-$(CONFIG_CRYPTO_DEV_HISI_HPRE) += hisi_hpre.o`, with `hisi_hpre-objs = hpre_main.o hpre_crypto.o`.

## Control Flow
Kernel build logic links `hpre_main.o` and `hpre_crypto.o` into one HPRE driver unit. This allows `hpre_main.c` to provide PCI/QM lifecycle and `hpre_crypto.c` to register crypto algorithms using symbols declared in `hpre.h`.

## State and Persistence Behavior
No runtime state exists in the Makefile. It persists the module boundary for HPRE.

## Dependencies and Integration Points
The parent HiSilicon Makefile descends into this directory when `CRYPTO_DEV_HISI_HPRE` is enabled. The composed object depends on the shared QM object built from the parent directory.

## Risks and Edge Cases
Build failures will occur if either object is renamed or if new HPRE source files are added without updating `hisi_hpre-objs`. Since both files link into one module, exported/non-exported symbol visibility between them should remain consistent with `hpre.h`.

## Test Signals
Build HPRE as module and built-in, verify `hisi_hpre.ko` includes both device lifecycle and crypto algorithm symbols, and run compile tests after adding any new HPRE source file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre.h

## Purpose
This header defines the shared HPRE contract between `hpre_main.c` and `hpre_crypto.c`: hardware SQE layout, algorithm IDs, debugfs structures, capability table indexes, the top-level HPRE wrapper around `struct hisi_qm`, and cross-file function declarations.

## Important APIs, Types, and Functions
Important constants include `HPRE_SQE_SIZE`, `HPRE_PF_DEF_Q_NUM`, `HPRE_PF_DEF_Q_BASE`, `HPRE_V2_ALG_TYPE`, and `HPRE_V3_ECC_ALG_TYPE`. `enum hpre_alg_type` maps HPRE hardware algorithm opcodes such as non-CRT RSA, CRT RSA, DH, ECC multiply, and Curve25519 multiply. `struct hpre_sqe` is the hardware submission queue entry with `dw0`, task lengths, DMA addresses for key/input/output, and a software tag. `struct hpre` embeds `struct hisi_qm` plus HPRE debug state and status.

The header declares `hpre_create_qp()`, `hpre_algs_register()`, `hpre_algs_unregister()`, and `hpre_check_alg_support()`. Debugfs helper structures include `struct hpre_debugfs_file`, `struct hpre_dfx`, and `struct hpre_debug`.

## Control Flow
There is no executable control flow. The header defines the compile-time interface: device lifecycle code allocates QPs and exposes capabilities, while crypto code creates request contexts, fills `struct hpre_sqe`, and uses algorithm IDs to submit work.

## State and Persistence Behavior
No state is allocated by the header. It defines the shape of runtime state embedded in HPRE devices and request SQEs. Capability table enum values persist the index contract used by `qm->cap_tables.dev_cap_table`.

## Dependencies and Integration Points
The header depends on `<linux/hisi_acc_qm.h>` for queue-manager types and is included by both HPRE implementation files. Its SQE layout must match HPRE hardware and the queue-manager SQE size configured in `hpre_qm_init()`.

## Risks and Edge Cases
Any change to `struct hpre_sqe`, algorithm opcode values, or capability enum ordering can break hardware ABI or table lookups. `HPRE_DEBUGFS_FILE_NUM` relies on enum arithmetic that assumes cluster control files follow the base debug file entries. Unsupported algorithms such as x448 are documented as sharing an opcode family but not currently supported.

## Test Signals
Build tests should catch cross-file prototype drift. Runtime signals are successful SQE submission/completion for RSA, DH, and ECDH, correct capability lookup in `hpre_check_alg_support()`, and debugfs file creation for all clusters within `HPRE_CLUSTERS_NUM_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_crypto.c

## Purpose
This file implements HPRE-backed Linux Crypto API algorithms for RSA (`akcipher`), DH (`kpp`), and ECDH over NIST P-192/P-256/P-384 (`kpp`). It translates crypto requests into HPRE SQEs, manages DMA buffers for keys and operands, handles hardware completions, records debug counters, and falls back to software implementations when hardware or parameters are unavailable.

## Important APIs, Types, and Functions
Private context types are `struct hpre_ctx`, `struct hpre_rsa_ctx`, `struct hpre_dh_ctx`, `struct hpre_ecdh_ctx`, and `struct hpre_asym_request`. `struct hpre_ctx` owns a QP, device pointer, selected key size, algorithm-specific DMA key buffers, fallback transform, curve ID, and high-performance-core flag.

Common request helpers include `hpre_ctx_init()`, `hpre_msg_request_set()`, `hpre_send()`, `hpre_alg_cb()`, `hpre_alg_res_post_hf()`, `hpre_hw_data_init()`, `hpre_prepare_dma_buf()`, `hpre_get_data_dma_addr()`, `hpre_hw_data_clr_all()`, and timeout accounting helpers. RSA entry points are `hpre_rsa_enc()`, `hpre_rsa_dec()`, key parsing helpers, and the `akcipher_alg rsa`. DH entry points are `hpre_dh_set_secret()`, `hpre_dh_generate_public_key()`, `hpre_dh_compute_shared_secret()`, and `kpp_alg dh`. ECDH entry points are curve-specific init functions, `hpre_ecdh_set_secret()`, `hpre_ecdh_compute_value()`, and the `ecdh_curves[]` KPP table.

The exported registration API is `hpre_algs_register()` and `hpre_algs_unregister()`, guarded by `hpre_algs_lock` and reference counted with `hpre_available_devs`.

## Control Flow
On first HPRE device registration, the file conditionally registers RSA, DH, and ECDH algorithms based on the device capability bitmap. Algorithm init allocates software fallback transforms and tries to allocate an HPRE QP through `hpre_create_qp()`. If no QP is available, the transform remains usable in fallback mode.

RSA key setup parses public/private keys, drops leading zeros, validates hardware-supported modulus sizes, allocates coherent DMA buffers in the hardware-required layout, and optionally stores CRT parameters. RSA encrypt/decrypt either call the fallback transform or prepare an SQE with non-CRT/CRT opcode, DMA-map input/output, send it through `hisi_qp_send()`, and complete asynchronously. DH setup validates supported group sizes, formats `xa || p` and optional generator buffers, and uses either `HPRE_ALG_DH` or `HPRE_ALG_DH_G2` for generator-2 mode. ECDH setup validates curve IDs and private key bounds, fills curve parameters from `ecc_get_curve()`, generates a private key through `crypto_stdrng_get_bytes()` when none is provided, and submits ECC multiply operations.

Hardware completions arrive through the QP callback `hpre_alg_cb()`, which recovers the request from `sqe->tag` and dispatches the algorithm-specific callback. Completion callbacks parse hardware status bits, update output lengths, check optional overtime thresholds, unmap/free DMA buffers, copy bounce-buffer results into scatterlists where needed, complete the original crypto request, and increment receive counters.

## State and Persistence Behavior
There is no disk persistence. Per-transform state persists across requests in `struct hpre_ctx`: QP allocation, DMA key material, fallback transforms, key size, curve selection, and mode flags. Per-request state lives in an aligned `struct hpre_asym_request` inside the Crypto API request context and is referenced from hardware via the SQE tag. Device-level state is updated through HPRE debug counters such as send, receive, busy, fail, overtime, and invalid request counts. Sensitive private key buffers are cleared with `memzero_explicit()` before freeing in several paths.

## Dependencies and Integration Points
The file integrates with the Crypto API `akcipher` and `kpp` interfaces, RSA/DH/ECDH key parsers, ECC curve tables, the standard RNG, Linux DMA APIs, scatterwalk helpers, and HiSilicon QM functions (`hpre_create_qp()`, `hisi_qp_send()`, `hisi_qm_free_qps()`). It depends on capability values populated by `hpre_main.c` and on HPRE SQE definitions from `hpre.h`.

## Risks and Edge Cases
DMA setup has many split paths: direct single mapping for suitable scatterlists and coherent bounce buffers for padded or multi-part data. Cleanup correctness depends on sentinel `DMA_MAPPING_ERROR`, `req->src`/`req->dst` flags, and matching sizes. Some cleanup helpers return early after an invalid input DMA address, which can skip output cleanup. ECDH completion compacts x/y coordinates in-place after unmapping and assumes the destination scatterlist is directly addressable by `sg_virt()`. Hardware fallback state is parameter-dependent; tests must confirm transitions between unsupported and supported keys do not leave stale DMA material. `hpre_send()` retries only `-EBUSY` and counts failures differently for busy versus other errors.

## Test Signals
Use Crypto API self-tests and known-answer tests for RSA public/private operations, RSA CRT and non-CRT keys, DH public/shared secret for all supported groups, and ECDH P-192/P-256/P-384. Add negative tests for too-small destination buffers, unsupported RSA sizes, unsupported DH groups, invalid ECDH private keys, missing keys, no-QP fallback, send busy/fail paths, DMA mapping fault injection, and algorithm unregister ordering across multiple devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_main.c

## Purpose
This file is the PCI/QM lifecycle driver for HiSilicon HPRE accelerators. It initializes hardware registers, capabilities, error handling, debugfs, SR-IOV, runtime PM, UACCE registration, and the global HPRE device list used by `hpre_crypto.c` to allocate QPs and register algorithms.

## Important APIs, Types, and Functions
Important public/cross-file functions are `hpre_create_qp()`, `hpre_check_alg_support()`, and `hisi_hpre_get_pf_driver()`. PCI lifecycle functions are `hpre_probe()`, `hpre_remove()`, `hpre_init()`, and `hpre_exit()`. QM/device setup flows through `hpre_qm_init()`, `hpre_pre_store_cap_reg()`, `hpre_probe_init()`, `hpre_pf_probe_init()`, `hpre_set_user_domain_and_cache()`, `hpre_set_cluster()`, `hpre_config_pasid()`, and SVA prefetch open/close helpers.

Diagnostics and debugfs are handled by `hpre_debugfs_init()`, `hpre_ctrl_debug_init()`, `hpre_dfx_debug_init()`, `hpre_cap_regs_show()`, and register dump show functions. Error handling is collected in `hpre_err_ini`, with callbacks such as `hpre_hw_error_enable()`, `hpre_hw_error_disable()`, `hpre_get_err_result()`, `hpre_dev_is_abnormal()`, `hpre_disable_axi_error()`, `hpre_enable_axi_error()`, and last-DFX-register snapshot functions.

## Control Flow
Module initialization initializes the global QM list, creates the top-level `hisi_hpre` debugfs directory, and registers the PCI driver. Probe allocates `struct hpre`, initializes the embedded `hisi_qm`, rejects unsupported hardware revision 1, determines PF/VF type, configures PF queue counts and error callbacks, calls `hisi_qm_init()`, stores capability registers, sets supported algorithm strings, performs PF hardware initialization when needed, starts QM, initializes debugfs, adds the device to the global list, registers algorithms to the crypto subsystem, optionally registers UACCE, optionally enables SR-IOV VFs, and initializes PM.

PF hardware initialization configures user/domain/cache registers, enables RSA/ECC blocks depending on hardware version, initializes read channel and clusters, applies Kunpeng 920 DSM/MSI and FLR workarounds, configures PASID/SVA prefetch, and enables clock gating. Remove reverses the order: PM shutdown, wait for tasks, unregister algorithms, remove from list, disable SR-IOV, remove debugfs, stop QM, clear counters and hardware debug state, close SVA prefetch, uninitialize device error handling, and uninitialize QM.

Error handling reads HPRE interrupt status, logs named hardware error bits, marks multi-bit ECC state, disables repeated reporting for reset-required errors, clears recoverable errors, and re-enables reporting. PCI AER/reset hooks are delegated to shared QM handlers with HPRE-specific callbacks supplied by `hpre_err_ini`.

## State and Persistence Behavior
There is no disk persistence. Module parameters persist for the module lifetime: `uacce_mode`, `pf_q_num`, and `vfs_num`. Global runtime state includes `hpre_debugfs_root` and `hpre_devices`. Per-device state is in `struct hpre`/`struct hisi_qm`, including capability tables, QP counts, function type, error masks, debugfs roots, last-register snapshots, channel names, UACCE state, SR-IOV VF count, and PM state. Hardware state includes cluster enable/init registers, RAS masks, interrupt masks, SVA prefetch state, clock gate state, current debug selector registers, and read-clear counters.

## Dependencies and Integration Points
This file depends on PCI, ACPI DSM, debugfs, runtime PM, UACCE, SR-IOV, topology/NUMA for QP allocation, and the shared HiSilicon QM framework. It exposes algorithms through `hisi_qm_alg_register()` and uses `hpre_algs_register()`/`hpre_algs_unregister()` via `hpre_devices`. It uses common debugfs exports from `debugfs.c` for QM register dumps and diff register support.

## Risks and Edge Cases
Capability table indexes must stay aligned with `hpre.h` and hardware capability layouts; otherwise algorithm registration and cluster counts can be wrong. PF-only operations must not run on VFs, and the code has many PF/VF branches that need coverage. SVA prefetch open/close waits on hardware status and can time out; failed open attempts call close as recovery. Debugfs control files can write hardware selector/read-clear registers and require strict validation. Probe error unwinding crosses QM start, debugfs creation, list insertion, crypto registration, UACCE, and SR-IOV, so ordering bugs can leak registrations. The module-level algorithm registration is shared across devices; concurrency and multi-device remove ordering depend on the QM list and crypto registration reference counting in `hpre_crypto.c`.

## Test Signals
Test PF and VF probe/remove, unsupported revision rejection, capability parsing for v2/v3 hardware, PF queue module parameter validation, UACCE modes, SR-IOV enable/disable, runtime suspend/resume, AER/reset recovery, SVA prefetch timeout handling, debugfs register/control files, algorithm registration based on capability masks, and fault injection at each probe stage to validate unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_main.c -->
