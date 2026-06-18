# subset-b-001007 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_control.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_control.c

Purpose: implements the QAIC management/control plane over the `QAIC_CONTROL` MHI channel. It converts UAPI `qaic_manage_msg` transaction arrays into the device wire protocol, sends them with sequence numbers and optional CRC, waits for paired responses, and applies local side effects for DBC activation, deactivation, DMA-continuation, and user teardown.

Important APIs and types: exported entry points are `qaic_manage_ioctl`, `get_cntl_version`, `qaic_mhi_ul_xfer_cb`, `qaic_mhi_dl_xfer_cb`, `qaic_control_open`, `qaic_control_close`, `qaic_release_usr`, and `wake_all_cntl`. Key internal types are `wire_msg`, `wire_trans_*`, `wrapper_msg`, `wrapper_list`, `xfer_queue_elem`, `dma_xfer`, and `ioctl_resources`.

Control flow: encode helpers validate user transaction lengths and translate passthrough, DMA, activate, deactivate, and status transactions. `qaic_manage_msg_xfer` builds wrappers, fills message header fields, queues one RX buffer and chained TX buffers through MHI, and blocks until `resp_worker` matches the response sequence. Large DMA payloads use `QAIC_TRANS_DMA_XFER_CONT` loops until the device acknowledges the transferred byte count. Decode helpers copy response transactions back to userspace and commit local state such as saving activated DBC queues or releasing deactivated DBCs.

State and persistence: persistent kernel state lives in `qaic_device` and `dma_bridge_chan`: control sequence numbers, queued control waits, CRC policy, lost RX buffer flag, DBC coherent queues, DBC ownership, and DBC sysfs state. The file does not persist state across module unload or device reset.

Dependencies and integration: depends on MHI, PCI DMA mapping, user page pinning, DRM file private data, SRCU locks from `qaic.h`, and QAIC UAPI transaction layouts. It is opened by the main MHI control probe in `qaic_drv.c` and drives datapath DBC ownership used by `qaic_data.c`.

Risks and test signals: high-risk areas are wrapper lifetime across async MHI callbacks, lost RX buffer handling after TX queue failure, DMA page pin cleanup, CRC negotiation, timeout cleanup, and late deactivate responses after a userspace waiter disappeared. Test with malformed transaction lengths/counts, CRC-on/off firmware, DMA-continuation larger than 64 KiB wire messages, user signal interruption, activate/deactivate races, module removal during waits, and MHI TX/RX fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_data.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_data.c

Purpose: implements the QAIC datapath ioctls and DBC ring processing. It allocates/imports DRM GEM BOs, maps them for device DMA, converts userspace slice descriptions into DBC request elements, submits BOs to request FIFOs, handles completions from response FIFOs, and exposes wait/performance/detach operations.

Important APIs and types: exported functions include `get_dbc_req_elem_size`, `get_dbc_rsp_elem_size`, `qaic_create_bo_ioctl`, `qaic_mmap_bo_ioctl`, `qaic_gem_prime_import`, `qaic_attach_slice_bo_ioctl`, `qaic_execute_bo_ioctl`, `qaic_partial_execute_bo_ioctl`, `qaic_wait_bo_ioctl`, `qaic_perf_stats_bo_ioctl`, `qaic_detach_slice_bo_ioctl`, IRQ handlers, and DBC lifecycle helpers. Internal hardware formats are `dbc_req` and `dbc_rsp`; object state is `qaic_bo` and `bo_slice`.

Control flow: BO creation builds a private GEM object and SG table; PRIME import delays DMA mapping until slicing. Attach validates DBC ownership, semaphore fields, doorbell alignment, offsets, direction, and queue capacity, then maps the BO and pre-encodes one or more `dbc_req` entries per slice. Execute copies encoded requests into the circular request FIFO under `req_lock`, assigns request IDs under `xfer_lock`, writes the tail register to commit, and records timing data. The threaded IRQ drains response FIFO entries, matches request IDs to queued BOs, counts slice completions, syncs DMA for CPU, completes waiters, and releases GEM refs. Polling mode simulates interrupts by repeatedly checking response FIFO state.

State and persistence: persistent in-memory state includes DBC coherent request/response queues, ring head/tail registers, BO slicing metadata, DMA mappings, per-BO completions, queued transfer lists, request IDs, and profiling timestamps. Reset and DBC release empty queues, complete waiters, detach BOs, and free coherent memory.

Dependencies and integration: uses DRM GEM/PRIME, DMA mapping, SG helpers, SRCU channel locks, PCI MMIO registers, QAIC UAPI slice/execute structs, sysfs DBC state, and SSR helpers. `qaic_control.c` activates DBCs; `qaic_drv.c` creates DBCs and IRQs.

Risks and test signals: important risks are SG slicing math, request FIFO wraparound, partial-execute last-entry rewriting, BO refcount balance, DMA sync direction, completion ordering for multi-slice BOs, SSR blocking via `ssr_dbc`, and races between execute/wait/detach/release. Test zero-size and page-aligned BOs, imported dma-bufs, invalid semaphores, ring-full paths, shared single-MSI mode, polling mode, PCI read returning `U32_MAX`, concurrent users, and reset while BOs are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.c

Purpose: provides QAIC debugfs visibility and the `QAIC_LOGGING` MHI bootlog receiver. It creates per-device debugfs files for firmware boot logs and per-DBC FIFO state.

Important APIs and types: public functions are `qaic_debugfs_init`, `qaic_bootlog_register`, and `qaic_bootlog_unregister`. Internal types are `bootlog_msg` for MHI receive buffers and work items, and `bootlog_page` for page-backed log storage.

Control flow: `qaic_debugfs_init` creates `bootlog` plus `dbcNNN/fifo_size` and `dbcNNN/queued` files. The bootlog MHI probe allocates an ordered workqueue, resets the log page list, prepares the channel, and queues a fixed pool of receive buffers. On each downlink completion, the callback null-terminates the string and queues work; `bootlog_log` appends it to page storage and requeues the buffer.

State and persistence: boot logs are kept in memory as devm-managed pages linked from `qdev->bootlog`, protected by `bootlog_mutex`. They survive while the device object survives but are reset when the logging channel probes again.

Dependencies and integration: uses debugfs, seq_file, MHI, devm page allocation, `qaic_data_get_fifo_info`, and `qaic_device` fields initialized by `qaic_drv.c`. Registration is conditional through `qaic_debugfs.h` and called from module init.

Risks and test signals: validate bootlog strings with short/empty transfers, page rollover, logging channel removal while work is queued, debugfs reads during reset, and `queued` behavior when MMIO reads return `U32_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.h

Purpose: declares the QAIC debugfs and bootlog integration points while compiling them out cleanly when `CONFIG_DEBUG_FS` is disabled.

Important APIs and types: when debugfs is enabled it declares `qaic_bootlog_register`, `qaic_bootlog_unregister`, and `qaic_debugfs_init`. When disabled it provides inline no-op versions returning success or doing nothing.

Control flow: this header is consumed by `qaic_drv.c` and `qaic_debugfs.c`. The no-op branch lets module init and DRM device registration use the same call sites regardless of debugfs configuration.

State and persistence: the header owns no state. It controls whether runtime bootlog/debugfs state from `qaic_debugfs.c` exists.

Dependencies and integration: includes DRM file declarations and relies on `struct qaic_drm_device` being visible through prior includes. It is part of the QAIC module surface, not UAPI.

Risks and test signals: build both `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`, ensuring callers do not accidentally depend on debugfs-only side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_drv.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_drv.c

Purpose: main Qualcomm QAIC PCI/DRM accel driver. It creates the device model, registers DRM ioctls, manages users, probes PCI resources and MSI vectors, registers the MHI controller and MHI service drivers, handles reset/remove/power-management, and coordinates online/offline state.

Important APIs and types: module entry points are `qaic_init` and `qaic_exit`; major callbacks include `qaic_open`, `qaic_postclose`, `qaic_pci_probe/remove/shutdown`, PCI error reset hooks, PM suspend/resume, and `qaic_mhi_probe`. It defines `qaic_device_config`, `qaic_accel_driver`, the QAIC ioctl table, and PCI IDs for AIC080/AIC100/AIC200.

Control flow: PCI probe allocates `qaic_device`/`qaic_drm_device`, initializes locks/workqueues/DBCs/SSR, maps MHI and DBC BARs, sets DMA masks, configures per-DBC IRQs or single-MSI fallback, registers the DRM accel node, and registers an MHI controller. When `QAIC_CONTROL` appears, `qaic_mhi_probe` opens the control channel, negotiates protocol version, marks the device online, and emits a uevent. Removal/reset notifies users, wakes control and DBC waiters, cleans SSR and DBC state, frees MHI, and unregisters DRM.

State and persistence: central state is `qaic_device`: PCI BARs, MHI controller/channels, DBC array, workqueues, bootlog/RAS/SSR/timesync channels, SRCU locks, and `dev_state`. User state is per DRM fd with an IDA handle and SRCU-protected pointer to the DRM device.

Dependencies and integration: integrates DRM accel/GEM, PCI, MHI controller support, sysfs/debugfs, RAS, SSR, Sahara firmware loader, timesync, and datapath/control files. The global `datapath_polling` module parameter changes IRQ behavior.

Risks and test signals: cover probe unwind, protocol-version mismatch, single-MSI fallback, open/close while device goes offline, PCI reset during in-flight DMA, suspend refusal when datapath busy, module exit with link-up cleanup, and optional service registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.c

Purpose: implements the QAIC reliability, availability, and serviceability receiver on the `QAIC_STATUS` MHI channel. It decodes firmware-pushed error records, prints human-readable syndromes, maintains error counters, exposes those counters through sysfs, and triggers a device reset for fatal uncorrectable errors.

Important APIs and types: public functions are `qaic_ras_register` and `qaic_ras_unregister`. Core types include packed `ras_data` plus syndrome structs for SoC memory, PCIe, DDR, system bus, NSP memory, and thermal sensors.

Control flow: probe prepares the MHI channel, queues one receive buffer, adds `ce_count`, `ue_count`, and `ue_nonfatal_count` sysfs attributes, and stores `qdev`. The DL callback converts little-endian fields in place, validates magic/version/type/length/source/type, logs source-specific syndrome details, increments saturated counters, invokes `mhi_soc_reset` on fatal UE, then requeues the buffer.

State and persistence: counters are stored in `qdev` and persist until device removal or reset of the structure. Incoming messages are transient MHI buffers.

Dependencies and integration: uses MHI, PCI device logging, sysfs device groups, and the MHI controller reset path. It is registered from `qaic_drv.c` module init.

Risks and test signals: malformed firmware messages must be dropped without reusing corrupt data; source-specific endian conversion must match firmware layout; fatal UE reset must not race removal. Test all error sources, invalid threshold values, saturated counters, MHI requeue failure, sysfs add/remove, and fatal reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.h -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.h

Purpose: small internal header exposing QAIC RAS MHI driver registration to the main QAIC module.

Important APIs and types: declares `qaic_ras_register` and `qaic_ras_unregister`; it defines no structures.

Control flow: `qaic_drv.c` calls the register function during module init and unregisters during module exit. The implementation handles all channel probe/remove work.

State and persistence: none in the header. Runtime state is held by `qaic_ras.c` in `qaic_device` counters and MHI buffers.

Dependencies and integration: used inside the QAIC driver only; not a userspace ABI.

Risks and test signals: ensure declaration stays synchronized with implementation and module init unwind calls unregister only after successful registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.c

Purpose: implements QAIC subsystem-restart handling on the `QAIC_SSR` MHI channel. It tracks DBC reset state, acknowledges firmware SSR events, downloads per-DBC crashdump tables and memory chunks, publishes completed dumps through `dev_coredumpv`, and resets the SoC if dump collection becomes inconsistent.

Important APIs and types: exported functions are `qaic_ssr_init`, `qaic_ssr_register`, `qaic_ssr_unregister`, and `qaic_clean_up_ssr`. Main wire types are `ssr_event`, `ssr_debug_transfer_info`, `ssr_memory_read`, `ssr_memory_read_rsp`, and done/response variants. Runtime state is `ssr_resp`, `ssr_crashdump`, and `ssr_dump_info`.

Control flow: probe prepares the channel and queues a small command receive buffer. `ssr_worker` handles `SSR_EVENT` state transitions, `DEBUG_TRANSFER_INFO` negotiation, and transfer-done responses. Crashdump collection first allocates a table buffer from firmware-provided address/length, reads the table through repeated `MEMORY_READ` commands, allocates a metadata+table+dump image, then walks each table entry chunk by chunk. Completion sends `DEBUG_TRANSFER_DONE`; a successful done response publishes the dump.

State and persistence: `qdev->ssr_dbc` marks the DBC blocked by SSR; `qdev->ssr_mhi_buf` is one preallocated crashdump transfer buffer. DBC sysfs states move through before/after shutdown and power-up. Completed dumps are handed to devcoredump; temporary buffers are freed or devm-managed.

Dependencies and integration: calls `qaic_dbc_enter_ssr`, `qaic_dbc_exit_ssr`, `release_dbc`, `set_dbc_state`, MHI queueing, DRM managed allocation, and devcoredump.

Risks and test signals: key risks are trusting firmware lengths, freeing the reusable memory-read request at the correct time, handling AFTER_POWER_UP while a dump is active, and reset escalation on protocol errors. Test table length validation, chunk boundaries, MHI UL/DL failures, concurrent event ordering, devcoredump ownership, and device reset cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.h -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.h

Purpose: declares the QAIC subsystem-restart interface used by the main driver and datapath cleanup paths.

Important APIs and types: forward-declares `struct drm_device` and `struct qaic_device`, and declares `qaic_ssr_register`, `qaic_ssr_unregister`, `qaic_clean_up_ssr`, and `qaic_ssr_init`.

Control flow: `qaic_drv.c` initializes per-device SSR storage during device creation, registers the MHI driver at module init, unregisters at exit, and calls cleanup during reset/remove.

State and persistence: the header has no state; implementation state is stored in `qaic_device`.

Dependencies and integration: bridges the main QAIC driver to `qaic_ssr.c` without exposing wire protocol structures.

Risks and test signals: compile-check users with incomplete struct declarations and validate init/register/unregister ordering in probe failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_sysfs.c

Purpose: exposes per-DBC state under the DRM accel device sysfs hierarchy. It creates one read-only attribute per DBC showing the numeric current `enum dbc_states` value and emits uevents when state changes.

Important APIs and types: exported functions are `qaic_sysfs_init`, `qaic_sysfs_remove`, and `set_dbc_state`. The file uses a small attribute wrapper containing a `device_attribute`, DBC id, and `qaic_drm_device` pointer.

Control flow: init allocates a DRM-managed attribute array sized to `qdev->num_dbc`, names entries `dbcN_state`, initializes sysfs attributes, and calls `sysfs_create_file`. Remove deletes each created file and frees the array. `dbc_state_show` resolves the DRM minor back to `qaic_device` and prints the numeric state. `set_dbc_state` bounds-checks the DBC and enum, skips unchanged values, updates state, and emits a `KOBJ_CHANGE` uevent with `DBC_ID` and `DBC_STATE`.

State and persistence: the authoritative state is `qdev->dbc[i].state`; sysfs attribute storage hangs from `qddev->sysfs_attrs`. State lasts for the DRM device lifetime and is reset by driver state transitions.

Dependencies and integration: uses sysfs, DRM managed allocation, DRM minor drvdata, and kobject uevents. It is used by `qaic_drv.c`, `qaic_control.c`, and `qaic_ssr.c` to surface activation, deactivation, and SSR transitions.

Risks and test signals: test partial sysfs creation unwind, removal during reads, invalid DBC ids, invalid states, and state transitions through activation, deactivation, SSR, and device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.c

Purpose: implements QAIC host/device time synchronization over two MHI services: periodic `QAIC_TIMESYNC_PERIODIC` and boot-time/on-demand `QAIC_TIMESYNC`.

Important APIs and types: public functions are `qaic_timesync_init`, `qaic_timesync_deinit`, and `qaic_mqts_ch_stop_timer`. Internal protocol types include `qts_hdr`, `qts_timeval`, `qts_host_time_sync_msg_data`, `mqts_dev`, and `qts_resp`.

Control flow: the periodic probe allocates an `mqts_dev`, prepares the MHI channel, stores the QTimer MMIO address, and starts a timer. Each timer callback reads host real time and the device QTimer, computes a UTC offset in seconds/useconds, queues a sync message, and reschedules itself. The boot-time service queues response buffers; received device commands are handled in a workqueue, which requeues RX first, then sends current host time or logs ACKs.

State and persistence: periodic state includes one sync buffer, an atomic in-use flag, a timer, and channel/device pointers. Boot-time state is per-response work item. State is freed on channel remove, and suspend stops the periodic timer through `qaic_mqts_ch_stop_timer`.

Dependencies and integration: depends on MHI, `ktime_get_real*`, QTimer MMIO in `bar_mhi`, `qaic_device` workqueues, and module registration from `qaic_drv.c`.

Risks and test signals: test readq and 32-bit fallback QTimer reads, `mhi_queue_buf` `-EAGAIN`, timer deletion during suspend/remove, malformed boot responses, repeated ACK/command cycles, and registration unwind when the second MHI driver registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.h -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.h

Purpose: declares the internal QAIC timesync service interface.

Important APIs and types: includes MHI declarations and exposes `qaic_timesync_init`, `qaic_timesync_deinit`, and `qaic_mqts_ch_stop_timer`.

Control flow: the main driver registers/de-registers both timesync MHI drivers through this API and calls the stop helper from suspend to quiesce the periodic timer.

State and persistence: none in the header. Runtime state is allocated per MHI channel by `qaic_timesync.c`.

Dependencies and integration: intentionally small coupling point between `qaic_drv.c` and the timesync implementation.

Risks and test signals: build coverage should ensure suspend code handles absent `mqts_ch` safely and init/deinit ordering remains paired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_timesync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.c -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.c

Purpose: implements the Qualcomm Sahara firmware/image transfer and memory-debug protocol over `QAIC_SAHARA` MHI. It serves requested boot images from firmware files and collects Sahara memory dumps into devcoredump records.

Important APIs and types: public functions are `sahara_register` and `sahara_unregister`. Core types are `sahara_packet`, `sahara_debug_table_entry64`, `sahara_dump_table_entry`, `sahara_memory_dump_meta_v1`, and `sahara_context`. Static image tables map AIC100/AIC200 image IDs to firmware paths.

Control flow: probe selects AIC100 non-streaming or AIC200 streaming behavior, allocates RX/TX buffers, prepares MHI, and queues RX. Firmware commands are processed in workqueues: HELLO replies with supported version, READ_DATA finds and streams firmware chunks, END_OF_IMAGE releases active firmware and may send DONE, and MEMORY_DEBUG64 switches into host-driven memory reads. Dump parsing reads a firmware-provided table, validates lengths and strings, allocates a metadata+table+image buffer, reads each memory region in bounded chunks, and publishes it with `dev_coredumpv`.

State and persistence: `sahara_context` tracks active firmware, pending read offsets, dump table/device addresses, memdump buffer ownership, streaming mode, and RX sizes. State is per MHI device and removed with the channel.

Dependencies and integration: uses Linux firmware loader, MHI queueing, workqueues, overflow helpers, vmalloc, and devcoredump. It is registered from QAIC module init.

Risks and test signals: test missing optional firmware, image-id conflicts, overlong READ_DATA, streaming continuation, table overflow protection, EOI-as-error during memory read, RX requeue failures, and remove while dump or firmware work is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.h -->
# sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.h

Purpose: declares the Sahara MHI service registration hooks for the QAIC module.

Important APIs and types: exposes `sahara_register` and `sahara_unregister`; no data structures are exported.

Control flow: `qaic_drv.c` registers the Sahara MHI driver during module init after the control MHI driver, and unregisters during module exit.

State and persistence: no header-owned state. Runtime protocol state is per MHI channel in `sahara.c`.

Dependencies and integration: internal QAIC-only header used to keep the firmware loader service separate from the main driver.

Risks and test signals: verify init unwind unregisters earlier services correctly if Sahara registration fails, and compile coverage catches signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/Kconfig

Purpose: defines the build-time configuration for the Rockchip NPU DRM accel driver.

Important APIs and types: declares `CONFIG_DRM_ACCEL_ROCKET` as a tristate option titled "Rocket (support for Rockchip NPUs)".

Control flow: selecting the option enables compilation of the `rocket` module. It depends on DRM accel support, ARM64 Rockchip or compile-test, Rockchip IOMMU or compile-test, and MMU; it selects DRM scheduler and GEM shmem helper support.

State and persistence: no runtime state. It controls whether the source files are built into the kernel or module.

Dependencies and integration: points users to `include/uapi/drm/rocket_accel.h` and the Mesa3D Rocket userspace driver. The hardware target is RK3588/RKNN/RKNPU-class NPUs.

Risks and test signals: build-test with native Rockchip configs and `COMPILE_TEST`, ensuring all selected helper dependencies are sufficient and module naming matches `rocket`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/Makefile -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/Makefile

Purpose: wires the Rocket driver object list into Kbuild.

Important APIs and types: builds `rocket.o` when `CONFIG_DRM_ACCEL_ROCKET` is enabled and composes it from `rocket_core.o`, `rocket_device.o`, `rocket_drv.o`, `rocket_gem.o`, and `rocket_job.o`.

Control flow: Kbuild links these objects into one module or built-in object. There are no conditional sub-objects beyond the top-level config gate.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with source files and Kconfig. The order places core/device/driver/GEM/job objects in one module.

Risks and test signals: compile the module after adding/removing source files and check `modinfo rocket` to confirm the expected module composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.c -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.c

Purpose: initializes and tears down one physical Rockchip NPU core.

Important APIs and types: exports `rocket_core_init`, `rocket_core_fini`, and `rocket_core_reset`, operating on `struct rocket_core` from `rocket_core.h`.

Control flow: init obtains two resets (`srst_a`, `srst_h`), four clocks, maps `pc`, `cna`, and `core` register resources, sets DMA segment size and 40-bit coherent mask, gets the IOMMU group, initializes job scheduling/IRQ state, enables runtime PM with a 50 ms autosuspend delay, briefly resumes the device to read/version-log hardware, then autosuspends. Fini disables runtime PM, drops the IOMMU group, and finalizes job scheduling. Reset asserts/deasserts resets with a 10 us delay.

State and persistence: core state includes MMIO pointers, clocks, reset controls, IOMMU group, runtime PM state, and scheduler state initialized through `rocket_job_init`.

Dependencies and integration: used by platform probe/remove in `rocket_drv.c`; depends on reset, clock, IOMMU, PM runtime, and register macros.

Risks and test signals: validate resource names in device tree, PM balance on init failure, IOMMU group lifetime, version register access after resume, and reset behavior during scheduler timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.h -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.h

Purpose: defines the per-core Rocket hardware abstraction and MMIO helper macros.

Important APIs and types: `struct rocket_core` stores device pointers, index, IRQ, register bases, clocks, resets, IOMMU group, job lock, in-flight job, fence state, reset workqueue, DRM scheduler, fence context, and sequence numbers. Macros wrap PC/CNA/CORE register reads/writes using generated offsets.

Control flow: callers use the macros when submitting, interrupting, and resetting jobs. Lifecycle functions are declared for core init/fini/reset.

State and persistence: the struct is persistent per detected NPU core and is owned by `rocket_device`.

Dependencies and integration: includes DRM scheduler, Linux clock/reset/io primitives, mutex types, and `rocket_registers.h`.

Risks and test signals: check offset arithmetic for CNA/CORE base-relative registers, lock ordering around `in_flight_job`, and scheduler/fence field initialization before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.c -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.c

Purpose: creates and unregisters the single DRM accel facade device used by all Rocket NPU cores.

Important APIs and types: exports `rocket_device_init` and `rocket_device_fini`.

Control flow: init allocates a managed DRM device embedding `struct rocket_device`, stores it as drvdata on the facade platform device, counts available `rockchip,rk3588-rknn-core` DT nodes, allocates the core array, configures 40-bit DMA and max segment size, initializes `sched_lock`, and registers the DRM device. Fini warns if cores remain and unregisters DRM.

State and persistence: persistent state is the `rocket_device` with DRM device, scheduler lock, core array, and core count. It lasts from first core probe until last core removal.

Dependencies and integration: called from `rocket_drv.c` when the first core probes; uses OF node scanning, DRM managed allocation, DMA API, and platform device drvdata.

Risks and test signals: test zero available cores, partial core probe failure, DRM registration failure, core hot-unplug ordering, and consistency between counted DT nodes and actual probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.h -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.h

Purpose: declares the Rocket DRM facade device container.

Important APIs and types: `struct rocket_device` embeds `struct drm_device`, a scheduler mutex, a dynamic array of `rocket_core`, and a core count. It declares init/fini and `to_rocket_device`.

Control flow: driver open, GEM, and job code convert DRM devices to `rocket_device` through the macro to access cores and scheduling state.

State and persistence: one instance exists for the facade DRM device while at least one NPU core is present.

Dependencies and integration: includes DRM device, IOMMU/platform declarations, and `rocket_core.h`.

Risks and test signals: ensure container conversion remains valid with `devm_drm_dev_alloc`, and verify users cannot open the facade before cores are initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.c -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.c

Purpose: main Rocket DRM accel/platform driver. It registers a facade DRM platform device, probes individual RK3588 NPU core devices, manages per-file IOMMU domains and sched entities, exposes ioctls, and implements runtime PM for clocks.

Important APIs and types: module entry points are `rocket_register` and `rocket_unregister`; file callbacks are `rocket_open` and `rocket_postclose`; platform callbacks are `rocket_probe` and `rocket_remove`; PM callbacks are `rocket_device_runtime_resume/suspend`. It also implements `rocket_iommu_domain_get/put`.

Control flow: module init creates a simple `rknn` platform device and registers the real OF platform driver. First core probe creates the DRM facade; each core gets an index and runs `rocket_core_init`. Open creates a per-file IOMMU paging domain, initializes an aperture-wide `drm_mm`, and opens a sched entity over all cores. Close destroys scheduler, DRM MM, domain, and module ref. Runtime resume enables core clocks; suspend refuses if the scheduler reports non-idle.

State and persistence: global `drm_dev` and `rdev` represent the facade. Per-file state is `rocket_file_priv`: device pointer, IOMMU domain, virtual address allocator, mutex, and scheduler entity.

Dependencies and integration: uses DRM accel/GEM/ioctl helpers, IOMMU, OF platform matching, PM runtime, `rocket_device`, `rocket_core`, `rocket_gem`, and `rocket_job`.

Risks and test signals: test multi-core probe/remove, module ref balance, open before first core, IOMMU domain allocation failure, PM suspend with in-flight jobs, and ioctl dispatch for all UAPI commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.h -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.h

Purpose: shares Rocket driver-private per-file and IOMMU domain structures across GEM and job code.

Important APIs and types: defines `struct rocket_iommu_domain` with an IOMMU domain and kref, and `struct rocket_file_priv` with `rocket_device`, domain, `drm_mm`, `mm_lock`, and DRM scheduler entity. Declares `rocket_pm_ops`, `rocket_iommu_domain_get`, and `rocket_iommu_domain_put`.

Control flow: open initializes `rocket_file_priv`; GEM creation uses its domain and allocator; job submission takes domain references; close drops everything after jobs are destroyed.

State and persistence: per-file state persists for a DRM fd. IOMMU domains are refcounted across BOs and jobs.

Dependencies and integration: includes DRM MM and scheduler helpers plus `rocket_device.h`.

Risks and test signals: validate kref balance between file, BOs, and jobs; check `drm_mm` teardown only after BO cleanup; compile-check PM ops export users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.c -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.c

Purpose: implements Rocket BO allocation, IOMMU mapping, cache ownership ioctls, and GEM object destruction.

Important APIs and types: exports `rocket_gem_create_object`, `rocket_ioctl_create_bo`, `rocket_ioctl_prep_bo`, and `rocket_ioctl_fini_bo`. Uses `rocket_gem_object` from `rocket_gem.h` and shmem GEM helpers.

Control flow: create BO allocates a shmem GEM object, attaches per-file state/domain, creates a GEM handle, obtains the SG table, allocates an IOVA range from the per-file `drm_mm`, maps the SG table into the per-file IOMMU domain with read/write permissions, and returns mmap offset plus NPU DMA address. Free unmaps IOMMU, removes the MM node, drops the domain ref, and frees shmem. Prep waits for write fences then syncs the SG table for CPU; fini syncs for device.

State and persistence: each BO stores driver private pointer, IOMMU domain ref, MM node, mapped size, and offset. Mapping persists for the GEM handle lifetime.

Dependencies and integration: uses DRM shmem GEM, DMA reservation fences, IOMMU mapping, per-file `drm_mm`, and Rocket UAPI structs.

Risks and test signals: test map failures after handle creation, partial IOMMU mappings, size alignment, cache sync before/after CPU access, BO free with outstanding page pins, and reserved-field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.h -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.h

Purpose: declares Rocket GEM object state and GEM ioctl entry points.

Important APIs and types: `struct rocket_gem_object` embeds `drm_gem_shmem_object` and stores owner file private data, IOMMU domain, DRM MM node, mapped size, and offset. It declares create/prep/fini ioctl functions and `to_rocket_bo`.

Control flow: `rocket_drv.c` installs `rocket_gem_create_object` in the DRM driver; `rocket_gem.c` uses the container helper to manage BO state.

State and persistence: fields persist per BO until GEM free, while the IOMMU domain ref can outlive the file's base reference through BO ownership.

Dependencies and integration: depends on DRM shmem helpers and `rocket_file_priv` declarations from `rocket_drv.h`.

Risks and test signals: ensure object embedding matches shmem helper expectations, and check that all paths initialize `driver_priv`, `domain`, and `mm` before free can run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.c -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.c

Purpose: implements Rocket job submission, DRM scheduler integration, hardware programming, interrupt completion, timeout reset, and per-file scheduler entity setup.

Important APIs and types: exports `rocket_ioctl_submit`, `rocket_job_init`, `rocket_job_fini`, `rocket_job_open`, `rocket_job_close`, and `rocket_job_is_idle`. Internal helpers manage `rocket_job`, `rocket_task`, custom completion fences, object reservation dependencies, and register programming.

Control flow: submit copies an array of UAPI jobs and task descriptors, looks up input/output BOs, takes an IOMMU domain ref, arms a DRM scheduler job, imports implicit dependencies, reserves output fences, and pushes to the sched entity. Scheduler `run_job` creates a hardware fence, resumes the selected core, attaches the job's IOMMU domain to the core group, stores `in_flight_job`, and writes PC/CNA/CORE registers with the current task's command buffer. IRQ handling masks/clears interrupts; the threaded handler either submits the next task in the same job or detaches IOMMU, signals the fence, autosuspends, and clears in-flight state. Timeout stops the scheduler, balances PM, detaches IOMMU, resets hardware, and restarts scheduling.

State and persistence: per-core scheduler, reset workqueue, fence context/seqno, in-flight job, and PM/IOMMU attachment are persistent. Per-job state owns BO refs, fences, task arrays, domain refs, and task progress.

Dependencies and integration: uses DRM scheduler, dma-fence, GEM reservation locks, IOMMU group attach/detach, PM runtime, Rocket register macros, IRQs, and UAPI structs.

Risks and test signals: high-risk paths include ignored errors in multi-job submit loop, PM/IOMMU cleanup when `pm_runtime_get_sync` or attach fails, reset while a job is in flight, output fence publication, scheduler entity core list allocation, and IRQ status error bits. Test multi-task jobs, multi-core scheduling, timeout reset, implicit sync, invalid user pointers, empty jobs, and remove during active scheduler work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.h -->
# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.h

Purpose: declares Rocket job/task structures and scheduler-facing functions.

Important APIs and types: `struct rocket_task` stores command-buffer DMA address and register-command count. `struct rocket_job` embeds `drm_sched_job`, tracks input/output BO arrays, task array/progress, scheduler and hardware fences, IOMMU domain, parent device, and refcount. Declares submit and scheduler lifecycle APIs.

Control flow: UAPI submit data is copied into `rocket_job`; scheduler code advances `next_task_idx`; IRQ code signals `done_fence`; cleanup releases all refs through `kref`.

State and persistence: job objects live from ioctl submission until scheduler and hardware references are dropped. Per-file scheduler entity setup is declared here but stored in `rocket_file_priv`.

Dependencies and integration: includes DRM driver/scheduler headers plus Rocket core and driver-private state.

Risks and test signals: verify refcount ownership between ioctl, scheduler free, and IRQ completion; ensure task_count and BO arrays are validated before hardware submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_job.h -->
