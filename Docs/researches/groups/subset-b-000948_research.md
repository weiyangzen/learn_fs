# subset-b-000948 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_drv.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_drv.c

## Purpose
This file is the PCI/DRM entry point for the HabanaLabs accelerator driver. It declares module metadata and parameters, binds supported PCI IDs, registers the DRM accel driver, allocates per-device `struct hl_device` instances, and handles PCI probe/remove, power management, PCI error recovery, and reset notifications. It is the integration layer that turns a PCI function into a DRM compute accel node plus a control character interface.

## Important APIs, Types, And Functions
The core exported entry points are `hl_device_open()` for the compute DRM node and `hl_device_open_ctrl()` for the control node. `hl_drm_ioctls` binds user ioctls to `hl_info_ioctl`, `hl_cb_ioctl`, `hl_cs_ioctl`, `hl_wait_ioctl`, `hl_mem_ioctl`, and `hl_debug_ioctl`. `hl_fops` delegates open/release/ioctl/mmap to DRM and HabanaLabs hooks. `get_asic_type()` maps PCI device and revision IDs to `enum hl_asic_type`, while `is_asic_secured()` tags secured Gaudi variants. Device construction flows through `create_hdev()`, `copy_kernel_module_params_to_device()`, `set_driver_behavior_per_device()`, `fixup_device_params()`, and `allocate_device_id()`. Lifecycle hooks are `hl_pci_probe()`, `hl_pci_remove()`, `hl_init()`, and `hl_exit()`.

## Control Flow
Module load allocates a char-device major with `alloc_chrdev_region()` and registers `hl_pci_driver`. Probe creates the DRM-backed `hl_device`, stores it with `pci_set_drvdata()`, then calls `hl_device_init()`. Removal calls `hl_device_fini()`, clears PCI drvdata, and removes the device ID from the global IDR. Compute open allocates `hl_fpriv`, initializes context and mmap memory managers, checks device operational state, scrub state, release state, and single active compute-context ownership, then creates a context and links it into `hdev->fpriv_list`. Control open resolves the minor through `hl_devs_idr` and only requires the control device to be operational.

## State And Persistence
Persistent in-kernel state includes module parameters (`timeout_locked`, `reset_on_lockup`, `memory_scrub`, `boot_error_status_mask`), global major number, global device IDR, per-device open counters and timestamps, and per-file private context/memory manager state. The file initializes reset behavior defaults, timeout defaults, firmware component masks, heartbeat settings, and ASIC-specific `reset_upon_device_release` behavior.

## Dependencies And Integration Points
The file depends on PCI, DRM accel, DRM ioctl/fops, tracepoints, the driver-wide `habanalabs.h`, and ASIC callback tables. It integrates with context management, debugfs, memory manager initialization, device activity reporting, reset and suspend/resume paths, PCI advanced error recovery, and the lower-level ioctl/mmap implementation.

## Risks
Open paths are tightly coupled to reset and release state; missed locking around `fpriv_list_lock` or global IDR use could expose partially initialized private data. Timeout defaults differ by ASIC, so regressions can produce premature lockup resets. Error recovery handlers assume valid `pci_get_drvdata()` and ASIC callbacks; null or half-torn-down device state during surprise removal is a key risk. The control node bypasses full compute context setup, so only explicitly supported control ioctls should be reachable there.

## Test Signals
Useful signals include module load/unload, PCI probe/remove on supported IDs, compute open rejection during reset/scrub/active-context states, control-node open by minor, DRM ioctl table registration, suspend/resume, PCI AER paths, and fault injection around `hl_device_init()` failure to verify IDR and char-device cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_ioctl.c

## Purpose
This file implements common user ioctl dispatch for device information, debug configuration, and the control-device ioctl path. It translates UAPI `hl_info_args` and `hl_debug_args` requests into driver state reads, firmware CPUCP messages, ASIC callbacks, eventfd registration, security attestation retrieval, and generic firmware passthrough requests.

## Important APIs, Types, And Functions
`hl_info_ioctl()` is the DRM compute-node entry point and `hl_ioctl_control()` is the control-node entry point. `_hl_info_ioctl()` is the central opcode dispatcher. `hl_info_ioctl_control()` rejects eventfd operations on the control node. `hl_debug_ioctl()` gates coresight debug operations behind operational device state and debug mode. `_hl_ioctl()` is a small DRM-like ioctl marshaler for the control file, using a stack buffer for small payloads and heap allocation for larger UAPI structures.

Information helpers include `hw_ip_info()`, `device_status_info()`, `hw_events_info()`, `dram_usage_info()`, `hw_idle()`, `device_utilization()`, `get_clk_rate()`, `pci_counters_info()`, `clk_throttle_info()`, `cs_counters_info()`, `sync_manager_info()`, `sec_attest_info()`, `dev_info_signed()`, and captured-error readers for page faults, RAZWI, undefined opcode, hardware, firmware, and engine errors.

## Control Flow
The dispatcher first validates padding. A whitelist of opcodes is served even while the device is disabled or resetting, covering static hardware info, status, reset count, event counters, CS counters, open stats, captured errors, event retrieval/unregistration, and DRAM usage. Other opcodes require `hl_device_operational()`. Most handlers validate output pointer and return size, populate a stack or allocated response structure, then `copy_to_user()` a bounded minimum of user size and kernel structure size. Firmware-backed queries build CPUCP requests or call firmware helpers. Debug operations validate debug mode for coresight ops, copy optional input/output buffers, and call `asic_funcs->debug_coresight()`.

## State And Persistence
The file reads and sometimes clears per-file notifier event masks. It owns registration and unregistration of `hpriv->notifier_event.eventfd`. It observes persistent counters in `hdev->aggregated_cs_counters`, per-context CS counters, reset counters, throttling timestamps, open counters, and captured error snapshots. Security attestation and signed info are transient firmware responses copied to userspace.

## Dependencies And Integration Points
Dependencies include UAPI DRM HabanaLabs structs, Linux `copy_to_user`/`copy_from_user`, eventfd, firmware CPUCP helpers, `asic_funcs`, the device reset/status model, and captured error state populated elsewhere. The control ioctl path integrates with `habanalabs_drv.c` control-file open and exposes only `DRM_IOCTL_HL_INFO`.

## Risks
The code is UAPI-facing, so size, pointer, and padding validation are critical. Several handlers return partial structures based on user size; incompatible UAPI evolution could leak incomplete semantics. `send_fw_generic_request()` limits buffers to 1 MiB but must keep allocation/free sizes consistent. Eventfd registration allows only one eventfd per file, and missing unregister/release handling elsewhere would leak references. Debug coresight operations are privileged by mode rather than by capability in this file, so debug-mode transitions must be correct.

## Test Signals
Test info opcodes in disabled/reset and operational states, malformed padding, null and undersized return buffers, control-node rejection of eventfd ops, eventfd double register/unregister, security attestation copy paths, firmware generic request size limits, and debug ioctl behavior when `hdev->in_debug` is false versus true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.c

## Purpose
This file implements the optional HLDIO NVMe direct-I/O path for moving file data directly from storage into HabanaLabs device P2P memory. It is explicitly constrained to specialized kernels and topology: P2PDMA support, page-aligned reads, non-sparse files, `O_DIRECT`, compatible block devices, and typically no useful IOMMU involvement.

## Important APIs, Types, And Functions
`hl_device_supports_nvme()` reports ASIC capability. `hl_dio_ssd2hl()` is the synchronous public SSD-to-device entry point. `hl_p2p_region_init()` publishes and allocates PCI P2P memory and builds a `struct page *` array. `hl_p2p_region_fini_all()` tears down all regions. `hl_dio_start()` allocates per-CPU inflight counters and enables I/O; `hl_dio_stop()` disables new I/O, waits for inflight operations to drain, and frees counters.

Internal helpers include `hl_dio_fd_register()` for validating and retaining the user file, `hl_dio_get_iopath()` and `hl_dio_put_iopath()` for io-enabled plus context-ref accounting, `hl_dio_va2page()` for MMU VA-to-PA-to-P2P-page lookup, and `hl_direct_io()` for constructing a `bio_vec` iterator and invoking `read_iter()`.

## Control Flow
`hl_dio_ssd2hl()` allocates an I/O descriptor, registers the file descriptor, fills read parameters, runs `hl_direct_io()`, returns the number of bytes read, unregisters the fd, and frees the descriptor. `hl_direct_io()` validates page alignment, increments the inflight path and context reference, allocates a `bio_vec` array sized by page count, converts each device VA page to a P2P `struct page`, builds an `iov_iter_bvec()`, calls the file's `read_iter()`, then releases the vector and I/O path. P2P region initialization calls `pci_p2pdma_add_resource()`, `pci_alloc_p2pmem()`, and `virt_to_page()` for each page.

## State And Persistence
HLDIO state lives in `hdev->hldio`: P2P regions, number of regions, per-CPU inflight I/O counters, and an `io_enabled` flag. Each synchronous I/O temporarily holds a file reference and context reference. Region objects persist from device setup until teardown.

## Dependencies And Integration Points
The file depends on block-device file operations, PCI P2PDMA, HabanaLabs MMU translation, context refcounting, and the HLDIO declarations in `hldio.h`. It integrates with device initialization/teardown via `hl_dio_start()` and `hl_dio_stop()`, and with memory/MMU by requiring device virtual addresses to resolve into configured P2P regions.

## Risks
`iov_iter_bvec(&io->iter, io->type, io->bv, 1, io->len_bytes)` passes `1` segment even though `npages` vectors were allocated; that is a correctness signal worth reviewing because multi-page reads may expose only the first vector. Allocation with `vzalloc()` in the I/O path is expensive. `io_enabled` is read without a lock and relies on ordering around per-CPU counters. Sparse-file and topology checks are minimal. `hl_dio_va2page()` fails if the virtual range spans outside initialized P2P regions.

## Test Signals
Exercise aligned and unaligned reads, non-`O_DIRECT` fd rejection, sparse-file rejection, no `read_iter`, devices without P2PDMA support, multi-page transfers, stop-while-I/O-inflight behavior, failed VA translations, and P2P region partial initialization cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.h

## Purpose
This header defines the public interface and state structures for optional HabanaLabs direct storage I/O. It also provides no-op or `-EOPNOTSUPP` stubs when `CONFIG_HL_HLDIO` is disabled, allowing the rest of the driver to compile without conditional call-site clutter.

## Important APIs, Types, And Functions
When enabled, `struct hl_p2p_region` describes a PCI P2P memory aperture with page array, allocated P2P memory pointer, device physical address, BAR offset, size, and BAR number. `struct hl_dio_stats` defines counters for total, successful, and failed operations plus bytes and last read length, although the implementation read in `hldio.c` does not update these counters. `struct hl_dio` stores the region array, per-CPU inflight counter, region count, and enabled flag.

Declared functions include `hl_dio_ssd2hl()`, `hl_p2p_region_fini_all()`, `hl_p2p_region_init()`, `hl_dio_start()`, `hl_dio_stop()`, `hl_hldio_init()`, `hl_hldio_fini()`, `hl_hldio_ioctl()`, debugfs hooks, and `hl_device_supports_nvme()`.

## Control Flow
The header itself has no runtime flow, but it determines build-time flow. With `CONFIG_HL_HLDIO`, callers link against real HLDIO functions. Without it, direct I/O calls fail cleanly while init/fini/debugfs hooks become harmless inline stubs. The polling macro `hl_poll_timeout_condition()` loops until a condition, timeout, and optional sleep cadence are satisfied, using `mb()` for ordering and `usleep_range()` for waiting.

## State And Persistence
The persisted state shape is `struct hl_dio` embedded in `struct hl_device`. The header also defines the P2P region metadata lifetime expected by initialization and teardown code. The `io_enabled` field is an `u8`, not an atomic or bitop, so synchronization expectations are implicit in callers.

## Dependencies And Integration Points
The header depends on Linux file, seq_file, ktime, delay, kernel, and errno types, plus forward declarations for HabanaLabs device/context structures. It integrates with optional debugfs and with any ioctl layer that exposes HLDIO operations.

## Risks
The disabled stubs must match enabled function signatures; mismatches would create build-only failures depending on Kconfig. The polling macro evaluates `cond` more than once and should only be used with side-effect-free conditions. `struct hl_dio_stats` can mislead users if exposed without implementation updates. The header comment says the feature must not be built under `COMPILE_TEST`, so Kconfig boundaries matter.

## Test Signals
Build both with and without `CONFIG_HL_HLDIO`, validate stub return codes, compile debugfs-enabled and disabled configurations, and test timeout macro callers with already-true, eventually-true, and never-true conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hldio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hw_queue.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hw_queue.c

## Purpose
This file owns kernel-side hardware queue management and command submission scheduling. It allocates queue rings, tracks producer/consumer indices, reserves completion queue capacity, emits buffer descriptors, initializes sync stream SOB/monitor resources, schedules signal/wait/collective/staged command submissions, and resets queue state after device reset.

## Important APIs, Types, And Functions
Externally used functions include `hl_hw_queue_add_ptr()`, `hl_hw_queue_update_ci()`, `hl_hw_queue_submit_bd()`, `hl_hw_queue_send_cb_no_cmpl()`, `hl_hw_queue_encaps_sig_set_sob_info()`, `hl_hw_queue_schedule_cs()`, `hl_hw_queue_inc_ci_kernel()`, `hl_hw_queues_create()`, `hl_hw_queues_destroy()`, and `hl_hw_queue_reset()`. Internal scheduling is split by queue type: `ext_queue_schedule_job()`, `int_queue_schedule_job()`, and `hw_queue_schedule_job()`. Sanity checks are similarly split across external, internal, and hardware queues.

## Control Flow
Queue creation allocates `hdev->kernel_queues`, copies ASIC queue properties, initializes each queue by type, and assigns sync stream resources. Scheduling locks the ASIC hardware queues, verifies device operational state, checks queue and CQ capacity for every queue used by the CS, initializes signal/wait or collective wait payloads, runs ASIC `pre_schedule_cs()`, mirrors the CS into `shadow_cs_queue` and `cs_mirror_list`, schedules TDR for the first timed CS, and emits each job descriptor to the appropriate queue. Error paths unwind CQ reservations before releasing the hardware queue lock.

## State And Persistence
Queue state includes `pi`, atomic `ci`, DMA ring memory, optional shadow queues, CQ producer reservation, sync-stream SOB objects, monitor IDs, collective monitor allocation, staged CS lists, and mirrored command submissions. Reset zeros PI/CI and reinitializes sync-stream SOB refcounts. External queue completion maps back through shadow queue entries populated during scheduling.

## Dependencies And Integration Points
The file depends on ASIC callbacks for queue locks, doorbells, PQE writes, end-of-CB packet generation, signal/wait CB generation, SOB addresses, collective wait setup, and pre-schedule hooks. It integrates with CS parsing, fences, TDR work, completion queues in `irq.c`, MMU/CB allocation semantics, and device reset state.

## Risks
CQ reservation must be exactly unwound on every failure path or submissions will deadlock on phantom full CQs. PI/CI wrap logic depends on queue lengths being powers of two or matching helper assumptions. Signal/wait setup handles SOB refcounts under both hardware queue lock and completion lock; missed ordering can race with completion or reset. Staged CS validation relies on mirror-list consistency. Internal queue memory is owned by ASIC callbacks and intentionally not freed here.

## Test Signals
Stress queue-full and CQ-full returns, non-completion CS CI updates, mixed queue-type submissions, signal and wait CS completion races, encapsulated signal handles, staged CS ordering errors, TDR scheduling for first entry, queue reset during hard and soft resets, and initialization failure after some queues are ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hw_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hwmon.c

## Purpose
This file exposes HabanaLabs firmware-provided sensors through the Linux hwmon subsystem. It builds dynamic channel descriptions from CPUCP sensor metadata, adapts firmware flag/attribute numbering across kernel and firmware enum versions, and implements read/write operations by sending CPUCP sensor packets.

## Important APIs, Types, And Functions
`hl_build_hwmon_channel_info()` consumes an array of `struct cpucp_sensor` and creates `hwmon_channel_info` structures. `hl_hwmon_init()`, `hl_hwmon_fini()`, and `hl_hwmon_release_resources()` manage hwmon registration and allocated channel metadata. The hwmon callbacks are `hl_is_visible()`, `hl_read()`, and `hl_write()`. Firmware access helpers include `hl_get_temperature()`, `hl_set_temperature()`, `hl_get_voltage()`, `hl_set_voltage()`, `hl_get_current()`, `hl_set_current()`, `hl_get_fan_speed()`, `hl_get_pwm_info()`, `hl_set_pwm_info()`, `hl_get_power()`, and `hl_set_power()`.

## Control Flow
Sensor construction first counts CPUCP sensors per hwmon type, allocates one config array per active type, adjusts flags for enum compatibility, allocates channel descriptors, and stores them in `hdev->hl_chip_info->info`. Registration installs `hl_hwmon_ops` and calls `hwmon_device_register_with_info()` using the firmware card name. Reads and writes reject non-operational devices, translate hwmon attributes to CPUCP attributes, and send a CPUCP packet via `asic_funcs->send_cpu_message()`. Visibility is static by type and attribute, marking sensor values read-only, offsets/PWM read-write, and reset-history write-only.

## State And Persistence
Persistent state is the allocated channel-info tree in `hdev->hl_chip_info->info`, the registered `hdev->hwmon_dev`, and `hdev->hwmon_initialized`. Sensor values themselves are not cached here; they are fetched from firmware per read. Compatibility behavior depends on `fw_app_cpu_boot_dev_sts0` feature bits and compile-time hwmon enum availability.

## Dependencies And Integration Points
The file depends on Linux hwmon APIs, PCI device naming, CPUCP packet layout, ASIC firmware messaging, and fixed ASIC properties. It integrates with firmware boot metadata, driver init/fini, and user-facing sysfs sensor files.

## Risks
Enum compatibility is subtle: incorrect flag shifting or attribute fixup hides sensors or sends wrong CPUCP requests. `hl_write()` ignores return values from some setter calls and returns `0`, which can hide firmware write failures. Resource ownership is split between build, init, fini, and release paths; double-free or leak risks exist if init fails after channel construction. Sensor metadata from firmware is trusted up to `CPUCP_MAX_SENSORS` with type bounds checking.

## Test Signals
Test modern and legacy firmware enum mappings, invalid sensor types, zero-sensor devices, read/write behavior while device is resetting, sysfs mode bits, CPUCP `-EAGAIN` logging suppression, registration failure cleanup, and release of all allocated channel config arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/irq.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/irq.c

## Purpose
This file handles completion queue interrupts, event queue interrupts, user interrupts, decoder abnormal interrupts, and queue object initialization/reset. It bridges hardware-written CQ/EQ entries into driver workqueues, command-submission completion, timestamp delivery, wait fences, and reset/error handling.

## Important APIs, Types, And Functions
`hl_irq_handler_cq()` drains completion queue entries. `hl_irq_handler_eq()` drains event queue entries and queues `irq_handle_eqe()` work. `hl_irq_user_interrupt_handler()` handles CQ and decoder user interrupts, while `hl_irq_user_interrupt_thread_handler()` handles TPC and unexpected interrupts. `hl_irq_eq_error_interrupt_thread_handler()` triggers hard reset on EQ error. Queue lifecycle APIs are `hl_cq_init()`, `hl_cq_fini()`, `hl_cq_reset()`, `hl_eq_init()`, `hl_eq_fini()`, `hl_eq_reset()`, and `hl_eq_dump()`.

## Control Flow
CQ handling loops while the ready bit is set, uses `dma_rmb()`, extracts shadow index fields, and either finishes an entire CS or a single job depending on completion mode. It clears the ready bit, advances CI, and returns a CQ free slot. EQ handling validates optional event indices, copies each EQ entry into a small work item, queues it to `hdev->eq_wq`, clears ready, advances CI, and notifies firmware/hardware of the new EQ CI. User CQ interrupts first complete wait-list fences and then process timestamp registration lists; object refcount drops are deferred to `ts_free_obj_wq` because they can sleep.

## State And Persistence
The file updates queue CI/free-slot state, event queue CI and previous index, CS/job completion timestamps, wait fence completions, timestamp buffers, and free-node pools for timestamp registration cleanup. It allocates DMA memory for CQs and CPU-accessible DMA pool memory for EQs. Reset clears queue memory as well as indices to prevent stale ready entries from being replayed.

## Dependencies And Integration Points
It depends on queue shadow state populated by `hw_queue.c`, CS/job work items, ASIC event handlers, workqueues, MMU mmap buffer refcounting, CB refcounting, reset logic, and user interrupt registration state. It also integrates with firmware EQ CI update callbacks and decoder work.

## Risks
Interrupt context constraints are significant: timestamp cleanup has to avoid sleeping under spinlocks and IRQ context. CQ shadow indices must match live queue shadow entries; stale entries after reset would schedule invalid work, so reset zeroing is important. Event index checking can break out and leave entries pending if firmware index state diverges. Allocation failure in EQ work item creation silently drops handling after clearing the event. User timestamp free-node pool exhaustion falls back to GFP_ATOMIC dynamic allocation, which can fail.

## Test Signals
Exercise CQ per-CS and per-job completion modes, disabled-device interrupts, stale CQ/EQ entries after reset, EQ index mismatch, EQ work allocation failure, timestamp registration cleanup, wait-list completions, TPC reset interrupt, EQ error hard reset, and queue init/fini/reset memory clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory.c

## Purpose
This file implements the main HabanaLabs memory UAPI backend: device DRAM allocation/free, host userptr pinning and DMA mapping, device virtual-address reservation, MMU map/unmap, hardware block mmap handles, dma-buf export for device memory, timestamp-buffer allocation, and VM lifecycle for devices and contexts.

## Important APIs, Types, And Functions
The primary ioctl entry is `hl_mem_ioctl()`. Allocation and free flow through `alloc_device_memory()` and `free_device_memory()`. Host memory flow uses `hl_pin_host_memory()`, `hl_unpin_host_memory()`, `dma_map_host_va()`, and `dma_unmap_host_va()`. VA management uses `get_va_block()`, `add_va_block_locked()`, `merge_va_blocks_locked()`, `hl_reserve_va_block()`, and `hl_unreserve_va_block()`. Mapping uses `init_phys_pg_pack_from_userptr()`, `map_phys_pg_pack()`, `unmap_phys_pg_pack()`, `map_device_va()`, and `unmap_device_va()`. Export uses `export_dmabuf_from_addr()` and `habanalabs_dmabuf_ops`. Lifecycle APIs are `hl_vm_init()`, `hl_vm_fini()`, `hl_vm_ctx_init()`, `hl_vm_ctx_fini()`, `hl_hw_block_mem_init()`, and `hl_hw_block_mem_fini()`.

## Control Flow
`hl_mem_ioctl()` rejects non-operational devices, then dispatches allocation, free, map, unmap, block mapping, dma-buf export, and timestamp allocation. Device allocation rounds size to the selected page size, allocates from a gen_pool either contiguously or page-by-page, stores a physical page pack in an IDR, and updates per-context/global DRAM accounting. Mapping either pins host memory and derives a physical page pack or looks up a device allocation handle, reserves a VA block with alignment and hint rules, maps each page through the MMU under `hdev->mmu_lock`, invalidates/prefetches MMU caches, and records the mapping in `ctx->mem_hash`. Unmap removes the hash node, unmaps pages, invalidates caches, returns the VA block, and releases userptr or mapping counts.

## State And Persistence
Persistent state includes the device DRAM gen_pool, physical page pack IDR, DRAM usage counters, context VA free lists for host/host-huge/DRAM ranges, context memory hash, userptr page/SG tables, dma-buf export counts, hardware block mmap list, and timestamp mmap buffers. Context teardown forcibly unmaps leaked mappings and frees page packs owned by the context.

## Dependencies And Integration Points
The file depends on MMU operations, gen_pool, IDR, scatter-gather and DMA APIs, get_user_pages, dma-buf, PCI P2P distance checks, DRM UAPI structs, debugfs hooks, timestamp interrupt registration, and `memory_mgr.c` for mappable timestamp buffer handles. It integrates with `irq.c` timestamp cleanup and with driver context lifecycle.

## Risks
This is high-risk UAPI and lifetime code. VA free-list splitting/merging must stay exact or future mappings overlap/leak. Error paths must decrement `mapping_cnt`, free page packs, unmap DMA, and return VA blocks consistently. Exported dma-bufs pin hash nodes via `export_cnt`, preventing unmap; missed release would block cleanup. Userptr long-term pins and DMA mappings can fail partially. Non-VM DRAM accounting trusts userspace sizes. Integer overflow checks exist for userptr pinning and export bounds, but all size/offset arithmetic remains sensitive.

## Test Signals
Test allocation with default and user page sizes, contiguous and non-contiguous DRAM, map/unmap with hints and forced hints, huge-page userptr optimization, MMU map failure unwind, context teardown with leaked mappings, dma-buf export/unmap/release, P2P-disabled attachments, timestamp buffer mmap/free, non-VM accounting, and fault injection at each allocation and IDR step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory_mgr.c

## Purpose
This file provides a small unified mmap buffer manager used for driver-owned buffers that are exposed to userspace by handle. It abstracts allocation, IDR handle assignment, kref lifetime, single-mmap enforcement, VMA close handling, and final manager cleanup. In this subset it is directly used by timestamp-buffer allocation in `memory.c`.

## Important APIs, Types, And Functions
Public functions are `hl_mmap_mem_buf_alloc()`, `hl_mmap_mem_buf_get()`, `hl_mmap_mem_buf_put()`, `hl_mmap_mem_buf_put_handle()`, `hl_mem_mgr_mmap()`, `hl_mem_mgr_init()`, `hl_mem_mgr_fini()`, and `hl_mem_mgr_idr_destroy()`. Behavior is provided by `struct hl_mmap_mem_buf_behavior`, with `alloc`, `mmap`, `release`, `topic`, and `mem_id` fields. The manager stores buffers in `mmg->handles` under `mmg->lock`.

## Control Flow
Allocation creates a buffer descriptor, allocates an IDR ID, builds a page-shifted handle that includes the behavior memory type, initializes the kref, and calls the behavior allocation callback. `hl_mem_mgr_mmap()` decodes the handle from `vma->vm_pgoff`, takes a buffer reference, validates exact mmap size and user access, enforces one active mmap using `atomic_cmpxchg`, installs VMA ops/private data, and delegates to behavior `mmap`. VMA close subtracts the closed VMA size from `real_mapped_size` and drops the buffer reference only when the whole mapped extent is closed. `hl_mem_mgr_fini()` iterates live handles and tries to put them, returning optional busy stats.

## State And Persistence
Persistent per-file state includes the IDR of handles, spinlock, and each buffer's kref, handle, behavior pointer, mmap flag, mappable size, real mapped size, and behavior-private data. Handles are page-shifted so they can travel through `vm_pgoff`. Busy buffer stats distinguish CB, timestamp, and other memory IDs during teardown.

## Dependencies And Integration Points
The file depends on Linux IDR, kref, VMA operations, access checks, and behavior callbacks from higher-level users. It integrates with file-private setup in `habanalabs_drv.c`, timestamp buffers in `memory.c`, and interrupt timestamp cleanup in `irq.c` through `hl_mmap_mem_buf_put()`.

## Risks
There are two put paths: direct buffer put can run in interrupt context, while put-by-handle may destroy outside the spinlock. Misusing the interrupt-safe assumptions in behavior release callbacks could sleep in atomic context. `real_mapped_size` is updated without an explicit lock in VMA close, relying on VMA lifecycle serialization. IDR destruction while non-empty is only reported as critical; callers must ensure cleanup order.

## Test Signals
Test handle lookup failures, allocation callback failure, mmap size mismatch, double mmap rejection, partial VMA close, final close ref drop, busy stats on leaked buffers, put-by-handle destruction, and manager destruction with an intentionally non-empty IDR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/Makefile

## Purpose
This Makefile fragment declares the common MMU object files that make up the HabanaLabs MMU implementation. It is not a standalone build script; it contributes `HL_COMMON_MMU_FILES` to the parent driver build.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build variable is `HL_COMMON_MMU_FILES`, listing `common/mmu/mmu.o`, `common/mmu/mmu_v1.o`, `common/mmu/mmu_v2.o`, and `common/mmu/mmu_v2_hr.o`.

## Control Flow
Build flow is declarative. Parent Kbuild logic includes this variable to compile/link the generic MMU layer plus versioned MMU backends. The line continuation keeps the object list as one variable assignment.

## State And Persistence
No runtime state is stored here. The persistent effect is build composition: changing the object list changes which MMU implementations are linked into the driver.

## Dependencies And Integration Points
The file integrates with the parent HabanaLabs Kbuild files and the MMU call sites used heavily by `memory.c`, `hldio.c`, and context initialization. The object names imply shared MMU code, v1, v2, and v2 high-radix support.

## Risks
Omitting an object can cause link failures or runtime lack of support for an ASIC MMU generation. Adding an object without parent Kconfig/source support can break builds. The path prefix must match the parent build directory expectations.

## Test Signals
Run kernel/module builds for ASIC configurations requiring MMU v1, v2, and v2 HR, and verify parent Makefiles include `HL_COMMON_MMU_FILES` exactly once without duplicate object linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/mmu/Makefile -->
