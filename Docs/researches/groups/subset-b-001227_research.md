# subset-b-001227 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm.c

## Purpose
`qm.c` is the shared HiSilicon accelerator Queue Manager implementation. It is a PCI-facing kernel module that allocates queue-pair memory, programs SQC/CQC/EQC/AEQC contexts through the QM mailbox, rings hardware doorbells, handles completion/error interrupts, exposes optional UACCE SVA queues to user space, supports SR-IOV queue partitioning and per-function QoS, and provides reset, AER, runtime PM, and algorithm-registration helpers for accelerator-specific drivers such as SEC2.

## Important APIs, types, and functions
- Exported queue and lifecycle APIs include `hisi_qm_init()`, `hisi_qm_uninit()`, `hisi_qm_start()`, `hisi_qm_stop()`, `hisi_qm_alloc_qps_node()`, `hisi_qm_free_qps()`, and `hisi_qp_send()`.
- Exported mailbox/capability helpers include `hisi_qm_wait_mb_ready()`, `hisi_qm_mb()`, `hisi_qm_mb_read()`, `qm_set_and_get_xqc()`, `hisi_qm_get_hw_info()`, `hisi_qm_get_cap_value()`, and `hisi_qm_set_algs()`.
- Error and reset integration is exported through `hisi_qm_dev_err_init()`, `hisi_qm_dev_err_uninit()`, `hisi_qm_dev_err_detected()`, `hisi_qm_dev_slot_reset()`, `hisi_qm_reset_prepare()`, `hisi_qm_reset_done()`, and `hisi_qm_dev_shutdown()`.
- SR-IOV and PM helpers include `hisi_qm_sriov_enable()`, `hisi_qm_sriov_disable()`, `hisi_qm_sriov_configure()`, `hisi_qm_pm_init()`, `hisi_qm_pm_uninit()`, `hisi_qm_suspend()`, and `hisi_qm_resume()`.
- Internal key types include `struct qm_mailbox`, `struct qm_doorbell`, `struct hisi_qm_hw_ops`, `struct hisi_qm_resource`, and `struct qm_hw_err`. Hardware context layouts for CQE/EQE/AEQE/SQC/CQC/EQC/AEQC come from `qm_common.h`.

## Control flow
Initialization starts in `hisi_qm_init()`: PCI memory is enabled, BARs are mapped, hardware version and capability tables are read, MSI vectors are allocated, interrupts are registered, PF-only memory reset and doorbell timeout setup run, optional UACCE state is allocated, coherent DMA for EQ/AEQ/SQC/CQC and per-QP SQ/CQ buffers is allocated, workqueues are initialized, command interrupts are enabled, and migration region selection is set. `hisi_qm_start()` then writes VFT for PFs, configures EQ/AEQ contexts, sends SQC/CQC base-table mailbox commands, initializes prefetch, enables EQ/AEQ interrupts, and marks the QM ready.

Kernel clients allocate queues with `hisi_qm_alloc_qps_node()`, which sorts available QMs by NUMA distance and attempts to create/start all requested QPs on one device. `hisi_qp_send()` checks QM/QP state, copies an SQE into the per-QP coherent SQ ring, records the caller message pointer, rings the SQ doorbell, advances the tail, and increments the in-flight count. EQ interrupts call `qm_get_complete_eqe_num()`, queue per-QP work items, and `qm_work_process()` either calls an event callback or polls CQEs with `qm_poll_req_cb()`. CQ polling invokes the accelerator request callback, updates CQ head/phase, rings CQ doorbells, and decrements `used`.

Stop/reset flow is deliberately staged. `hisi_qm_stop()` first stops request submission, optionally marks user queues as stopped through the device status page, drains the whole QM or each QP, disables EQ/AEQ interrupts, clears PF VFT assignment, and invalidates reset-affected queues. Soft reset/AER uses `qm_controller_reset_prepare()`, `qm_soft_reset()`, and `qm_controller_reset_done()` to stop PF/VFs, disable MSI/MSE, call ACPI reset, reinitialize hardware and error reporting, reset device memory, restart kernel QPs, and notify VFs. FLR paths split the same logic into `hisi_qm_reset_prepare()` and `hisi_qm_reset_done()`.

## State and persistence behavior
The driver persists runtime state only in kernel memory and hardware registers. `struct hisi_qm` owns capability bits, queue counts, queue arrays, coherent DMA regions, idr allocation state, interrupt/workqueue state, debug counters, QoS factors, and error-isolation state. Queue state is split between software fields (`qp_status`, `qp_in_used`, `ref_count`, `is_resetting`) and hardware contexts programmed through mailbox commands. UACCE queues map MMIO and DUS coherent memory into user processes; reset paths use the last words of DUS as stop flags for user queues. Error isolation keeps an in-memory one-hour list of AER timestamps and can move UACCE state to isolated when a threshold is exceeded. Runtime PM uses autosuspend but no on-disk persistence.

## Dependencies and integration points
The file depends on PCI/MSI, ACPI reset methods, DMA coherent allocation, IDR, workqueues, runtime PM, debugfs, UACCE, Linux crypto accelerator framework contracts in `linux/hisi_acc_qm.h`, and hardware-specific error callbacks supplied through `qm->err_ini`. It integrates with accelerator-specific drivers by exporting queue allocation, send, lifecycle, error, and algorithm registration helpers. It integrates with user space through UACCE queue mmap/ioctl operations (`UACCE_CMD_QM_SET_QP_CTX`, `UACCE_CMD_QM_SET_QP_INFO`) and debugfs `alg_qos`.

## Risks and edge cases
Major risk areas are reset races with in-flight `hisi_qp_send()` calls, mailbox timeouts, user-space doorbells arriving during reset, hardware-version differences in doorbell, IFC, MSI, VFT, and capability behavior, and partial SR-IOV rollback when VFT programming fails. Reset failure isolates SVA devices, but failed queue drain can still force callbacks through `qp_stop_fail_cb()`. QoS parsing depends on BDF matching and divisor calculations; zero or out-of-range values are rejected. UACCE mappings require strict size checks, and DUS status words are shared with user visible memory. Hardware error masking must avoid losing non-fatal/critical errors while preventing interrupt storms.

## Test signals
Useful signals include successful probe/init/start/stop paths for PF and VF, queue allocation/send/completion under load, mailbox timeout and malformed command injection, EQ/AEQ overflow behavior, SR-IOV enable/disable with assigned and unassigned VFs, FLR and AER reset recovery, runtime suspend/resume, UACCE mmap/ioctl coverage, debugfs `alg_qos` read/write on PF and VF, and fault-injection around DMA allocation, MSI vector allocation, VFT programming, ACPI reset failure, and device error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm_common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm_common.h

## Purpose
`qm_common.h` defines the shared hardware queue context and event entry layouts consumed by `qm.c` and HiSilicon accelerator drivers. It is a compact ABI-like header for CQE/EQE/AEQE and SQC/CQC/EQC/AEQC memory images plus declarations for common QM helpers.

## Important APIs, types, and functions
The primary types are `struct qm_cqe`, `struct qm_eqe`, `struct qm_aeqe`, `struct qm_sqc`, `struct qm_cqc`, `struct qm_eqc`, and `struct qm_aeqc`. They use little-endian fields because the structures are copied directly to or from DMA buffers and mailbox-programmed hardware contexts. Declared helpers are `qm_set_and_get_xqc()`, `hisi_qm_show_last_dfx_regs()`, and `hisi_qm_set_algqos_init()`.

## Control flow
The header has no executable control flow. Its structures are populated in `qm.c` during queue startup (`qm_sq_ctx_cfg()`, `qm_cq_ctx_cfg()`, `qm_eq_ctx_cfg()`, `qm_aeq_ctx_cfg()`), read during queue-drain checks, and interpreted by interrupt/completion paths.

## State and persistence behavior
Instances of these structures live in coherent DMA regions owned by `struct hisi_qm` and per-QP buffers. Hardware updates CQE/EQE/AEQE content, while the driver writes SQC/CQC/EQC/AEQC content. There is no file or cross-boot persistence.

## Dependencies and integration points
The header depends on Linux endian types and `struct hisi_qm` from the public HiSilicon accelerator QM API. It is included by `qm.c`; sibling accelerator drivers can include it when they need direct xQC or DFX helper access.

## Risks and edge cases
Because these structures mirror hardware layouts, field order, size, alignment, and endian conversions are critical. Expanding or reordering fields would silently corrupt mailbox/DMA context programming. Callers must also use the matching `QM_MB_CMD_*` command so `qm_set_and_get_xqc()` copies the correct structure size.

## Test signals
Build coverage catches missing declarations, but meaningful validation comes from queue bring-up, xQC dump/set mailbox tests, completion interrupt tests, and reset/drain tests that compare SQC and CQC tails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/qm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/Makefile

## Purpose
This Makefile builds the legacy HiSilicon SEC platform crypto driver when `CONFIG_CRYPTO_DEV_HISI_SEC` is enabled.

## Important APIs, types, and functions
It declares `hisi_sec.o` as the module object and links it from `sec_algs.o` and `sec_drv.o`. There are no C APIs in the Makefile itself.

## Control flow
Kbuild includes the module only when the config symbol is selected. `sec_drv.o` supplies platform probe/remove and queue/device plumbing; `sec_algs.o` supplies crypto algorithm registration and request handling.

## State and persistence behavior
The file has no runtime state. It controls object composition at build time only.

## Dependencies and integration points
It depends on the kernel Kbuild system and the `CONFIG_CRYPTO_DEV_HISI_SEC` Kconfig option. It integrates the platform device driver and crypto algorithm implementation into one loadable/built-in unit.

## Risks and edge cases
If either object is removed or renamed without updating this file, the module will fail to link. Building only this legacy driver does not include the newer SEC2 QM-backed implementation.

## Test signals
Build tests with `CONFIG_CRYPTO_DEV_HISI_SEC=y` and `=m` should produce `hisi_sec` and resolve symbols between `sec_algs.o` and `sec_drv.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_algs.c

## Purpose
`sec_algs.c` registers and implements asynchronous skcipher algorithms for the legacy HiSilicon SEC platform accelerator. It maps Linux crypto requests into SEC block descriptors, splits large requests to the hardware limit, maps scatterlists to hardware SGL chains, handles IV chaining, queues descriptors through `sec_drv.c`, and completes requests back to the crypto API.

## Important APIs, types, and functions
The public functions for the rest of the driver are `sec_alg_callback()`, `sec_algs_register()`, and `sec_algs_unregister()`. Internal setup is centered on `sec_c_alg_cfgs`, `sec_alg_skcipher_init_template()`, `sec_alg_skcipher_setkey*()` variants, `sec_alg_alloc_and_calc_split_sizes()`, `sec_map_and_split_sg()`, `sec_alg_alloc_and_fill_el()`, `sec_send_request()`, `sec_skcipher_alg_callback()`, and `sec_alg_skcipher_crypto()`. The registered `skcipher_alg` table covers AES ECB/CBC/CTR/XTS, DES ECB/CBC, and 3DES ECB/CBC.

## Control flow
Algorithm registration is reference-counted by `active_devs` under `algs_lock`; only the first SEC device registers the skcipher table, and the last unregister removes it. Per transform, init allocates a hardware queue with `sec_queue_alloc_start_safe()` and optionally a software FIFO for chaining modes. Setkey verifies AES/DES/3DES/XTS keys, allocates coherent key memory, stores the key, and prepares a descriptor template.

For each encrypt/decrypt request, `sec_alg_skcipher_crypto()` computes 32 MiB split sizes, DMA maps source and optional destination scatterlists, uses `sg_split()` for per-descriptor segments, maps the IV if required, allocates `sec_request_el` descriptors with hardware SGL chains, and then atomically either queues all elements or backlogs the request. `sec_send_request()` sends directly when hardware/software queues are empty enough for ordering, otherwise it places elements in the queue FIFO. Completion enters through `sec_alg_callback()` and `sec_skcipher_alg_callback()`, checks error bits, updates CBC/CTR IV state, drains a software queued element or backlog item when possible, frees completed element resources, unmaps DMA on final element, and calls `skcipher_request_complete()`.

## State and persistence behavior
Per-transform state lives in `struct sec_alg_tfm_ctx`: selected cipher algorithm, coherent key buffer/DMA address, descriptor template, assigned `sec_queue`, mutex, auth buffer placeholder, and backlog list. Per-request state lives in `struct sec_request` and a list of `struct sec_request_el` subrequests. Coherent key and DMA mappings are explicitly freed on transform exit or completion. There is no persistent state outside runtime memory and hardware queues.

## Dependencies and integration points
The file depends on the Linux crypto skcipher API, AES/DES/XTS key validation helpers, DMA mapping, scatterlist splitting, DMA pools from `sec_drv.c`, and queue functions declared in `sec_drv.h`. It integrates upward with the crypto API via `crypto_register_skciphers()` and downward with hardware via `sec_queue_send()` and completion callbacks.

## Risks and edge cases
The code must preserve request atomicity: partial hardware queueing cannot be safely unwound, so it checks capacity before sending all elements. Chaining modes depend on serialized completion and software FIFO behavior; incorrect queue-empty checks can break CBC/CTR IV sequencing. DMA mapping and split-array cleanup has many error paths. A notable edge is `entry_sum_in_sgl = count % SEC_MAX_SGE_NUM`, which becomes zero for exact multiples and must match hardware expectations. DES ECB is explicitly noted as lacking known test vectors. Backlog completion uses `-EINPROGRESS` notification once a request leaves backlog.

## Test signals
Use crypto selftests and `tcrypt`/AF_ALG coverage for AES ECB/CBC/CTR/XTS, DES, and 3DES in in-place and split source/destination modes; request sizes below, at, and above 32 MiB; scatterlists requiring multiple hardware SGLs; backlog behavior with queue pressure; IV update checks for CBC decrypt/encrypt and CTR; DMA mapping fault injection; and unload/reload with multiple SEC devices to validate algorithm reference counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.c

## Purpose
`sec_drv.c` is the platform-device and hardware-queue driver for legacy HiSilicon SEC units on Hip06/Hip07. It maps MMIO regions, enables clocks and reset, configures SEC/SAA hardware, allocates per-queue DMA rings, services queue interrupts, manages a global pool of SEC devices/queues, and calls `sec_algs.c` to expose crypto algorithms.

## Important APIs, types, and functions
Externally used queue APIs are `sec_queue_send()`, `sec_queue_can_enqueue()`, `sec_queue_stop_release()`, `sec_queue_alloc_start_safe()`, and `sec_queue_empty()`. Platform lifecycle is handled by `sec_probe()` and `sec_remove()` through `module_platform_driver(sec_driver)`. Hardware helpers cover clock/reset (`sec_clk_en()`, `sec_clk_dis()`, `sec_reset_whole_module()`), common SEC configuration (`sec_hw_init()`, `sec_hw_exit()`), queue configuration (`sec_queue_config()`, `sec_queue_hw_init()`), IRQ handling (`sec_isr_handle_th()`, `sec_isr_handle()`), and global device selection (`sec_device_get()`).

## Control flow
Probe sets a 64-bit DMA mask, allocates `struct sec_dev_info`, creates a DMA pool for hardware SGLs, maps SEC common/SAA regions, enables clocks, resets the module, initializes SEC hardware, configures all 16 queues, requests threaded IRQs, registers crypto algorithms, and publishes the device in the global `sec_devices` array. Queue configuration allocates command, completion/out-of-order, and debug rings as coherent DMA, maps the queue MMIO window, writes ring base addresses/depth/reorder/interrupt registers, and leaves IRQs disabled until a queue is started.

At runtime, `sec_queue_alloc_start_safe()` selects the least busy SEC instance, marks a queue in use, starts it, and returns it to an algorithm transform. `sec_queue_send()` copies a prepared descriptor into the command ring under a mutex, stores the software callback context in `shadow[]`, advances the hardware write pointer after a write barrier, and increments `used`. Interrupt top half disables flow IRQs; threaded handler reads out-of-order completion entries, marks completed descriptor IDs in a bitmap, then replays callbacks in expected ring order so crypto requests see ordered completion. Queue release stops interrupts/hardware and returns the queue to the pool.

## State and persistence behavior
Global in-memory state is `sec_devices[SEC_MAX_DEVICES]`, protected by `sec_id_lock`. Each `struct sec_dev_info` stores MMIO bases, queue array, queue use count, DMA pool, and enabled SAA count. Each `struct sec_queue` stores ring DMA addresses, MMIO base, IRQ, in-use flag, expected completion index, out-of-order bitmap, optional software FIFO, and `shadow[]` callback contexts. No persistent disk state is used.

## Dependencies and integration points
The file depends on platform devices, ACPI/OF matching (`HISI02C1`, `hisilicon,hip06-sec`, `hisilicon,hip07-sec`), DMA coherent APIs, DMA pools, IOMMU domain checks, IRQ threading, MMIO helpers, and the local algorithm API in `sec_drv.h`. It integrates with `sec_algs.c` by providing queue allocation/send/completion and registering/unregistering algorithms during platform probe/remove.

## Risks and edge cases
The probe unwind path must release only queues that were fully initialized; the loop uses `i`/`j` cleanup and can be sensitive to failures after IRQ setup. Completion handling assumes hardware out-of-order IDs index the command ring and that the bitmap plus `expected` pointer restores strict order. Queue stop terminates in-flight transactions when a transform exits. Device selection ignores NUMA and CPU locality. IOMMU paging reduces usable SAA count and changes cache/stream ID setup, so both translated and untranslated paths need coverage. The code also relies on relaxed MMIO ordering plus explicit barriers around queue write pointer updates.

## Test signals
Probe/remove tests through ACPI and device tree matching, queue allocation exhaustion across multiple devices, descriptor send/full-ring behavior, out-of-order completion replay, IRQ disable/enable behavior, IOMMU and non-IOMMU initialization, clock/reset timeout fault injection, DMA allocation failure, and crypto selftests through `sec_algs.c` are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.h

## Purpose
`sec_drv.h` is the shared private header for the legacy HiSilicon SEC driver. It defines SEC hardware descriptor bitfields, queue/ring/device structures, algorithm transform/request state, hardware SGL formats, constants, and cross-file function prototypes used by `sec_algs.c` and `sec_drv.c`.

## Important APIs, types, and functions
The central hardware type is `struct sec_bd_info`, a 16-word block descriptor with extensive bit masks for cipher/auth mode, key sizes, granularity, DMA addresses, and completion/error flags. Queue and device types include `struct sec_queue_ring_cmd`, `struct sec_queue_ring_cq`, `struct sec_queue_ring_db`, `struct sec_queue`, `struct sec_dev_info`, `struct sec_hw_sge`, and `struct sec_hw_sgl`. Crypto state types include `enum sec_cipher_alg`, `struct sec_alg_tfm_ctx`, `struct sec_request`, and `struct sec_request_el`. Prototypes expose queue operations and algorithm registration callbacks between the two C files.

## Control flow
The header has no executable logic, but it encodes the control contract: algorithms build `sec_bd_info` and `sec_request_el` objects, submit them through `sec_queue_send()`, and receive completions through `sec_alg_callback()`. The driver uses queue/device definitions to allocate rings, map queue registers, maintain ordered completion, and free resources.

## State and persistence behavior
All state described by the header is runtime state. Keys live in coherent DMA memory attached to transform contexts; requests own DMA mappings and hardware SGL chains; queues own coherent rings and completion shadow pointers; devices own MMIO bases and DMA pools. There is no durable persistence.

## Dependencies and integration points
The header depends on Linux crypto API types, `kfifo`, scatterlists through users of the structures, DMA addresses, mutex/spinlock/list primitives, and hardware register definitions in the C files. It is the integration boundary between the platform queue driver and crypto algorithm implementation.

## Risks and edge cases
Descriptor bitfield definitions must match hardware documentation exactly. Duplicated `SEC_MAX_SGE_NUM` definition is benign but increases maintenance risk. Large structures combine hardware ABI fields and software-only pointers, so users must not DMA-map the wrong structure type. Request splitting and IV chaining rely on the semantics documented in comments for `struct sec_request` and `struct sec_queue`.

## Test signals
Compile coverage of both C files, descriptor field validation through successful encryption/decryption, SGL chain tests with more than 64 entries, queue pressure/backlog tests, and completion/error flag tests are the most relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec/sec_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/Makefile

## Purpose
This Makefile builds the newer QM-backed HiSilicon SEC2 crypto driver when `CONFIG_CRYPTO_DEV_HISI_SEC2` is enabled.

## Important APIs, types, and functions
It declares `hisi_sec2.o` and links it from `sec_main.o` and `sec_crypto.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild selects these objects only when the SEC2 config symbol is enabled. `sec_main.o` is expected to own device/QM integration while `sec_crypto.o` owns algorithm request processing using the structures declared in `sec.h`.

## State and persistence behavior
The file has build-time state only. It does not create runtime storage.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_CRYPTO_DEV_HISI_SEC2`. It integrates the SEC2 driver with the shared HiSilicon QM code built elsewhere in the hisilicon crypto tree.

## Risks and edge cases
Object names must stay aligned with source files. Enabling SEC2 without the shared QM support it depends on would fail at link or runtime through unresolved symbols or missing device support.

## Test signals
Build with `CONFIG_CRYPTO_DEV_HISI_SEC2=y` and `=m`; verify `hisi_sec2` links against `sec_main.o`, `sec_crypto.o`, and shared QM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec.h

## Purpose
`sec2/sec.h` is the private shared header for the newer HiSilicon SEC2 crypto driver. It defines per-request buffers, hardware SGL layout, skcipher/AEAD request state, per-QP resource state, transform context, debug counters, capability table enums, and exported helper prototypes that connect SEC2 crypto code to the shared QM driver.

## Important APIs, types, and functions
Important structures include `struct sec_alg_res`, `struct sec_hw_sge`, `struct sec_hw_sgl`, `struct sec_src_dst_buf`, `struct sec_request_buf`, `struct sec_cipher_req`, `struct sec_aead_req`, `struct sec_req`, `struct sec_req_op`, `struct sec_auth_ctx`, `struct sec_cipher_ctx`, `struct sec_qp_ctx`, `struct sec_ctx`, `struct sec_debug`, and `struct sec_dev`. Capability enums `sec_cap_type` and `sec_cap_table_type` map SEC/QM capability table slots. Helper prototypes are `sec_destroy_qps()`, `sec_create_qps()`, and `sec_get_alg_bitmap()`.

## Control flow
The header defines the operation vector `struct sec_req_op`: request processing maps buffers, fills a SEC SQE, sends it to a QM queue pair, unmaps buffers, and invokes completion callbacks. `struct sec_ctx` chooses queues by separate encrypt/decrypt cyclic counters and stores algorithm type, fallback state, pbuf support, and cipher/auth contexts. `struct sec_qp_ctx` tracks one QM queue pair, request ID allocation, request list, per-queue DMA resources, and SGL pools.

## State and persistence behavior
All state is runtime-only. Per-QP state tracks `hisi_qp`, IDR request IDs, send head, request array, SGL pools, and DMA buffers. Per-transform state tracks keys, IV sizes, fallback crypto transforms, algorithm support flags, and selected request operations. `struct sec_debug` contains atomic counters for send/receive/busy/error/invalid/done statistics. No on-disk persistence exists.

## Dependencies and integration points
The header depends on `linux/hisi_acc_qm.h` for QM queue types and on `sec_crypto.h` for SEC SQE formats. It also depends on Linux crypto skcipher/AEAD/shash types, IDR, spinlocks, atomics, and DMA addresses. It integrates SEC2 with the shared QM implementation in `qm.c`; `struct sec_dev` embeds `struct hisi_qm`.

## Risks and edge cases
Alignment of `struct sec_hw_sgl` is fixed at 64 bytes and must remain hardware-compatible. The union in `struct sec_request_buf` overlays SGL buffers with a 512-byte pbuf, so `use_pbuf` decisions must be correct. The request IDR/list must be protected by the documented locks to prevent completion/use-after-free races. Fallback flags mean behavior can diverge between hardware and software paths. Capability bitmap enums must match hardware tables used by SEC2 main code.

## Test signals
Build coverage with SEC2 enabled, skcipher and AEAD crypto selftests, hardware and fallback path tests, pbuf and SGL path tests, request ID exhaustion, completion error counters, queue creation/destruction, capability bitmap decoding, and reset/stop interaction through embedded `hisi_qm` are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec.h -->
