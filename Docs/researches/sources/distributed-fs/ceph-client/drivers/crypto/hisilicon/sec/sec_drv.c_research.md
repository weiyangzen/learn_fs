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
