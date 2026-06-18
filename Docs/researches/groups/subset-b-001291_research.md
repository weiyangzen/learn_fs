# subset-b-001291 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/stratix10-rsu.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/stratix10-rsu.c

Intel/Altera Stratix10 Remote System Update client driver. It exposes RSU firmware state and control through sysfs attributes on a `stratix10-rsu` platform device created by the Stratix10 service-layer driver. The driver depends on `linux/firmware/intel/stratix10-svc-client.h` for both synchronous and asynchronous secure-service transactions, and on SMCCC result layouts returned by SDM firmware.

Important state lives in `struct stratix10_rsu_priv`: the service channel/client, a completion and mutex for synchronous callbacks, cached RSU status fields, DCMF version/status words, retry limits, and SPT addresses. The sysfs group exports read-only boot/error/version fields plus DCMF, retry, and SPT details; `reboot_image` sends `COMMAND_RSU_UPDATE`, and `notify` sends `COMMAND_RSU_NOTIFY` then refreshes `COMMAND_RSU_STATUS`.

Control flow starts in `stratix10_rsu_probe()`: allocate and initialize cached invalid values, request the `SVC_CLIENT_RSU` channel, register as an async client, then query initial RSU status, DCMF version/status, max retry, and SPT table. `rsu_send_msg()` serializes classic service calls with `priv->lock`, installs the callback, sends through `stratix10_svc_send()`, waits for completion, calls `stratix10_svc_done()`, and returns timeout/interruption errors. `rsu_send_async_msg()` retries `stratix10_svc_async_send()`, waits for interrupt completion, polls the transaction, decodes callback data, and always calls `stratix10_svc_async_done()`.

Persistence is firmware-backed. Sysfs reads return cached values from the most recent probe or notify/status query, not live firmware reads on every access. State-changing writes are persisted by SDM firmware and may affect next boot image selection or RSU bookkeeping. The kernel-side cache is lost on driver unbind/reprobe.

Integration points are the `stratix10-svc` provider, SDM RSU command ABI, Linux sysfs attribute groups, and the generated child platform device name `stratix10-rsu`. Risks include partial probe cleanup: several later query failures free the channel but do not remove the async client on every path. `remove()` frees only the channel, so async-client lifetime is asymmetric. Callback payloads assume firmware returns valid `kaddr1/kaddr2` layouts, and several show functions still use `sprintf()`. Test signals include sysfs attribute presence, status refresh after writing `notify`, timeout handling when SDM is unavailable, unsupported-firmware warnings, and probe/remove tests that detect leaked async clients or double-free channel cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/stratix10-rsu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/stratix10-svc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/stratix10-svc.c

Stratix10/Agilex secure-service layer. It provides the shared-memory allocator, per-client service channels, synchronous SMC/HVC command dispatch, and newer asynchronous SDM mailbox transactions used by RSU and other firmware clients. Exported APIs include `stratix10_svc_request_channel_byname()`, `stratix10_svc_free_channel()`, `stratix10_svc_send()`, `stratix10_svc_done()`, `stratix10_svc_allocate_memory()`, `stratix10_svc_free_memory()`, `stratix10_svc_add_async_client()`, `stratix10_svc_remove_async_client()`, `stratix10_svc_async_send()`, `stratix10_svc_async_poll()`, and `stratix10_svc_async_done()`.

Core types divide responsibilities. `stratix10_svc_controller` owns the device, channels, genpool, global SDM mutex, SMC/HVC invoke function, and async controller. `stratix10_svc_chan` owns a client pointer, FIFO, spinlocks, optional worker kthread, and optional async channel. `stratix10_svc_data_mem` tracks allocated shared-memory buffers in a global list protected by `svc_mem_lock`. Async state is held in `stratix10_async_ctrl`, `stratix10_async_chan`, and `stratix10_svc_async_handler`, using IDA pools and a hash table keyed by client/job transaction IDs.

Probe flow reads the DT `method` property to select SMC or HVC, asks secure firmware for shared-memory bounds, remaps the page-aligned range write-combined, creates a best-fit genpool, initializes async support after checking ATF service version, allocates four FIFOs for FPGA/RSU/FCS/HWMON channels, publishes the controller in `svc_ctrl`, creates the `stratix10-rsu` child, and populates child firmware nodes. Module init finds the firmware node and populates a matching platform device before registering the driver.

Synchronous commands use `stratix10_svc_send()` to translate client payload pointers into secure physical addresses, enqueue a `stratix10_svc_data`, and lazily start `svc_normal_to_secure_thread()` on CPU 0. That thread drains the FIFO, serializes SDM access with `sdm_lock`, maps command enums to Intel SIP SMC IDs, calls secure firmware, and converts results into client callbacks. Busy FPGA config paths enter polling helpers for buffer claim or completion status. `stratix10_svc_done()` stops the worker thread after a client request completes.

Asynchronous commands require `stratix10_svc_add_async_client()`. `stratix10_svc_async_send()` allocates a job ID, composes a transaction ID, inserts the handler in the hash before issuing the SMC 1.2 call, and removes it on busy/rejected/error. `stratix10_svc_async_poll()` issues `INTEL_SIP_SMC_ASYNC_POLL`, prepares command-specific response data, and returns `-EAGAIN` while in progress. `stratix10_svc_async_done()` removes the handler and frees the job ID. Interrupt-driven completion is left to the caller's callback/polling logic.

Persistence is in secure firmware and the reserved shared-memory pool. Linux keeps transient channel ownership, FIFO contents, memory allocation records, and async transaction state. Dependencies include ARM SMCCC, DT firmware nodes, platform devices, genalloc, kfifo, IDA, hash tables, kthreads, and Intel SIP command headers.

Risks are concentrated in concurrency and cleanup. `svc_data_mem` is global across controllers; `stratix10_svc_free_memory()` falls through to `list_del(&svc_data_mem)` if no match, which is unsafe for the list head. `stratix10_svc_add_async_client()` appears to reuse the common async channel when `use_unique_clientid` is true and a common refcount exists, which is surprising naming and should be validated against callers. Probe error paths call `stratix10_svc_async_exit()` even if async init failed. `svc_thread_cmd_data_claim()` has a loop condition that can continue while timeout wait returns nonzero and deserves stress testing. Test signals include DT method validation, shared-memory sizing/alignment failures, FIFO saturation returning `-ENOBUFS`, synchronous callback completion, async busy/retry handling, remove-time transaction cleanup, and KASAN/lockdep coverage for memory-list and channel-lifetime paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/stratix10-svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/sysfb.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/sysfb.c

Generic system framebuffer device creator. It turns firmware-populated `sysfb_primary_display.screen` data into a platform device for either `simple-framebuffer` or a legacy framebuffer driver. The code runs as a `device_initcall()` after PCI enough for EFI quirks and parent-device detection.

Public APIs are `sysfb_disable()` and `sysfb_handles_screen_info()`. `sysfb_disable()` serializes against init with `disable_lock`, unregisters the platform device when the caller is global or matches the detected parent, and permanently suppresses registration. `sysfb_handles_screen_info()` reports whether `screen_info_video_type()` sees a supported video type.

`sysfb_init()` applies screen-info fixups, honors the global disabled flag, applies EFI quirks, resolves an optional PCI parent via `screen_info_pci_dev()`, then asks `sysfb_parse_mode()` whether the mode can become `simple-framebuffer`. If simplefb creation fails or is unsupported, it selects a legacy platform-device name from the video type, attaches the full `sysfb_display_info` as platform data, applies EFI fwnode data, and registers the device.

State is minimal: static `pd` records the registered platform device, while `disabled` gates future registration. Firmware framebuffer metadata remains in global `screen_info`; this file does not own video memory. Dependencies include PCI, platform devices, `screen_info`, `sysfb` helpers, and simplefb platform data.

Risks include parent reference handling: `sysfb_parent_dev()` returns a referenced PCI device, and `sysfb_init()` unconditionally calls `put_device(parent)` on the common exit path, so null-parent paths rely on `put_device(NULL)` being harmless. Registration uses device id 0 by design, which requires other firmware parsers to avoid conflicts. Test signals include boot logs for simplefb versus legacy fallback, `sysfb_disable()` from native DRM drivers, PCI memory-disabled parent rejection, EFI quirk behavior, and absence of duplicate platform framebuffer devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/sysfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c

Simple-framebuffer helper for `sysfb.c`. It validates firmware `screen_info`, translates recognized VESA/EFI packed RGB modes into `simplefb_platform_data`, computes an accessible framebuffer memory resource, and registers a `simple-framebuffer` platform device.

`sysfb_parse_mode()` accepts only `VIDEO_TYPE_VLFB` and `VIDEO_TYPE_EFI`, rejects transparent formats, and matches bits-per-pixel plus RGB bitfield sizes/offsets against `SIMPLEFB_FORMATS`. On success it fills format, width, height, and stride. `sysfb_create_simplefb()` builds a 64-bit base when `VIDEO_CAPABILITY_64BIT_BASE` is set, rejects inaccessible/truncated bases, uses `height * stride` rather than the full advertised VRAM, verifies it fits in firmware-reported VRAM, page-aligns the mapping length, creates the `BOOTFB` memory resource, attaches EFI fwnode data, platform data, and registers the device.

State is not persistent beyond the platform device and its resource/platform data. Dependencies include `screen_info`, simplefb format definitions, platform-device resource APIs, page alignment, and `sysfb_set_efifb_fwnode()`.

Risks include integer overflow if `height * stride` exceeds 32 bits before assignment to `u32 length`, although firmware modes are typically bounded. The `res.end <= res.start` guard catches some wrap cases after page alignment. Test signals include known EFI/VESA formats, 64-bit framebuffer base handling, advertised-VRAM-too-small rejection, resource bounds in `/proc/iomem`, and simpledrm/simplefb binding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/sysfb_simplefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/Kconfig

Kconfig menu for Tegra firmware support. It defines `TEGRA_IVC`, the Inter-VM Communication protocol library, and `TEGRA_BPMP`, the Boot and Power Management Processor firmware driver.

`TEGRA_IVC` is a bool visible under `COMPILE_TEST` and depends on `ARCH_TEGRA`. `TEGRA_BPMP` depends on `ARCH_TEGRA`, `TEGRA_HSP_MBOX`, and little-endian CPU support, and selects `TEGRA_IVC`. The help text identifies BPMP as the firmware processor handling clocks, DVFS, thermal, and power management through HSP notifications plus IVC transport.

Integration is entirely build-time: these symbols control compilation of `ivc.o`, `tegra-bpmp.o`, and SoC-specific BPMP implementations through the sibling Makefile. Risks are mostly configuration coverage: `TEGRA_BPMP` is unavailable on big-endian builds and requires HSP mailbox support, so dependent clock/reset/power-domain consumers must tolerate probe deferral or missing BPMP. Test signals include randconfig coverage for `COMPILE_TEST`, dependency resolution on each Tegra SoC, and build checks that `select TEGRA_IVC` supplies transport symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/Makefile

Build recipe for Tegra firmware drivers. It composes `tegra-bpmp.o` from `bpmp.o` plus SoC-specific transport files and optional debugfs support, and builds `ivc.o` when `CONFIG_TEGRA_IVC` is enabled.

`bpmp-tegra210.o` is included for Tegra210. `bpmp-tegra186.o` is reused for Tegra186, Tegra194, Tegra234, and Tegra264 because those generations share the HSP mailbox plus IVC transport model. `bpmp-debugfs.o` is conditional on `CONFIG_DEBUG_FS`. `obj-$(CONFIG_TEGRA_BPMP)` emits the composite BPMP object; `obj-$(CONFIG_TEGRA_IVC)` emits the transport library.

The file has no runtime state. Integration risks are link-coverage related: SoC data in `bpmp.c` references `tegra186_bpmp_ops` or `tegra210_bpmp_ops` only under matching `IS_ENABLED()` guards, so Makefile conditions must stay aligned with those guards. Test signals are allmodconfig/randconfig builds across Tegra SoC symbols and DEBUG_FS enabled/disabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-debugfs.c

Debugfs mirror for Tegra BPMP firmware debug nodes. It supports two firmware ABIs: in-band `MRQ_DEBUG` open/read/write/close operations and shared-memory `MRQ_DEBUGFS` operations. `tegra_bpmp_init_debugfs()` creates `/sys/kernel/debug/bpmp/debug` and populates files/directories from firmware if either ABI is supported.

Helpers `seqbuf_*()` parse firmware directory listings made of attributes/depth/name records. `get_filename()` maps a Linux debugfs dentry path back to the BPMP-relative path by subtracting the mirror root path. In-band helpers open a firmware path, transfer data chunks under global `bpmp_debug_lock`, validate read lengths, and close the firmware fd. Shared-memory helpers allocate coherent DMA buffers for names/data, pass 32-bit DMA addresses in MRQ payloads, and use firmware dumpdir/read/write commands.

Control flow for reads goes through `bpmp_debug_show()` for in-band files or `debugfs_show()` for shared-memory files; writes go through `bpmp_debug_store()` or `debugfs_store()`. Directory population is recursive: `bpmp_populate_debugfs_inband()` reads each directory path and descends, while `bpmp_populate_debugfs_shmem()` dumps a flattened tree and `bpmp_populate_dir()` reconstructs hierarchy by depth.

State is mostly firmware-owned. Linux keeps only debugfs dentries and temporary buffers; in-band open file descriptors are opened and closed per operation. Dependencies include debugfs, coherent DMA allocation with `GFP_DMA32`, BPMP MRQ transport, BPMP ABI debug structures, `seq_file`, and user-copy helpers.

Risks include trusting firmware-supplied directory metadata, path lengths, and file lengths. Shared-memory requests cast DMA addresses to `u32`, so the `GFP_DMA32` constraint is essential. In `mrq_debug_write()`, the close return overwrites an earlier write error, unlike read paths that preserve the original error. Debugfs lifetime cleanup is only explicit on initialization failure; normal driver removal is not implemented in the BPMP core. Test signals include probing both ABI variants, nested directory population, oversize filename/data rejection, malformed depth/listing handling, user read/write propagation to firmware, and DMA address range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-private.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-private.h

Private operations contract between the Tegra BPMP core and SoC-specific transport implementations. `struct tegra_bpmp_ops` abstracts channel initialization/deinitialization, request/response readiness checks, request/response acknowledgements, free-channel checks, post operations, doorbell ringing, and optional resume handling.

The file declares `tegra186_bpmp_ops` and `tegra210_bpmp_ops`, letting `bpmp.c` select the correct implementation from SoC match data while keeping transfer and MRQ logic transport-agnostic. The operations take either `struct tegra_bpmp *` or `struct tegra_bpmp_channel *`, matching the public BPMP structures from `soc/tegra/bpmp.h`.

There is no runtime state here, but ABI stability matters inside the driver directory: every SoC implementation must provide semantics expected by `bpmp.c`, especially that post/ack/free/readiness operations are safe under the core locks and that `resume()` restores channel synchronization after noirq resume. Test signals include build coverage for each SoC guard, transfer tests through both op tables, and suspend/resume tests for SoCs with a resume callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra186.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra186.c

Tegra186-and-newer BPMP transport implementation. It uses HSP mailbox notifications plus Tegra IVC queues in SRAM or reserved DRAM to implement the private BPMP operation table consumed by `bpmp.c`.

`struct tegra186_bpmp` stores the parent BPMP pointer, TX/RX shared-memory backing with optional genpools, physical addresses, and a mailbox client/channel. Readiness and free checks are direct wrappers around `tegra_ivc_read_get_next_frame()` and `tegra_ivc_write_get_next_frame()`, setting `channel->ib` or `channel->ob`. Ack/post operations advance IVC read/write counters. `tegra186_bpmp_ring_doorbell()` sends an HSP mailbox message and marks TX done.

Channel setup first tries a reserved-memory region: first 4 KiB for TX and second 4 KiB for RX. If no reserved memory exists, it allocates two `"shmem"` genpool regions. Each BPMP channel gets a one-frame IVC queue using `MSG_MIN_SZ` aligned to 64 bytes and offset by channel index. Init requests the HSP mailbox, resets all channels through the IVC state machine, and installs the mailbox RX callback that calls `tegra_bpmp_handle_rx()`.

State persists in shared memory and BPMP firmware; Linux stores mapped queue pointers, genpool allocations, channel completions, and mailbox handle. Resume resets IVC channels to reestablish synchronization after suspend. Dependencies include `tegra_ivc`, mailbox client API, reserved-memory parsing, genalloc SRAM pools, BPMP ABI message sizing, and the private op contract.

Risks include hard-coded 4 KiB TX/RX windows: channel count, frame size, and ABI changes must continue to fit. `tegra186_bpmp_channel_reset()` busy-waits until `tegra_ivc_notified()` succeeds, so broken firmware synchronization can spin. DRAM init maps the full reserved region for TX and uses an offset pointer for RX, while size validation only requires at least 8 KiB. Test signals include reserved-memory and SRAM fallback probe paths, HSP mailbox request failure, IVC reset convergence, suspend/resume transfer recovery, and MRQ traffic on all threaded channel indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra186.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra210.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra210.c

Tegra210 BPMP transport implementation. Unlike Tegra186+, it retrieves channel buffers from BPMP atomics registers and uses an arbitration semaphore register block plus legacy interrupt controller retriggering for doorbells.

`struct tegra210_bpmp` stores the mapped atomics and arb-sema regions and cached TX IRQ data. Channel state is encoded as two-bit fields per channel: `SL_SIGL`, `SL_QUED`, `MA_FREE`, and `MA_ACKD`. Readiness/free predicates compare the semaphore state to the expected value. Post/ack operations write masks to semaphore set/clear offsets to move ownership between master and firmware. Doorbell ringing calls `irq_retrigger()` on the TX IRQ chip.

Init maps two platform resources, initializes the TX, RX, and threaded channels by asking BPMP for each channel base address through the atomics trigger/result registers, maps each 0x80-byte channel window, records IRQ data for `"tx"`, and registers an IRQ handler for `"rx"` that invokes `tegra_bpmp_handle_rx()`. It exports `tegra210_bpmp_ops` without deinit/resume callbacks.

State is MMIO-backed in BPMP channel windows and arb-sema registers. Linux stores only mappings, completions, and IRQ data. Dependencies include platform resources, IRQ chip retrigger support, raw MMIO accessors, and the private BPMP op table.

Risks include reliance on `irq_retrigger`; platforms whose TX IRQ chip lacks it cannot ring BPMP. Channel base addresses returned by firmware are trusted and mapped fixed-size. Raw MMIO access is used for semaphore state and requires correct hardware ordering assumptions. Test signals include DT resource/IRQ names, channel address retrieval per index, semaphore state transitions during transfers, RX interrupt delivery, and behavior on IRQ chips without retrigger support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp-tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp.c

Tegra BPMP core driver and exported firmware API. It lets other kernel drivers acquire a BPMP handle from device tree, send MRQ messages, register handlers for firmware-initiated MRQs, and initialize child clock/reset/power/debug providers.

Exports include `tegra_bpmp_get_with_id()`, `tegra_bpmp_get()`, `tegra_bpmp_put()`, `tegra_bpmp_transfer_atomic()`, `tegra_bpmp_transfer()`, `tegra_bpmp_mrq_return()`, `tegra_bpmp_request_mrq()`, `tegra_bpmp_free_mrq()`, `tegra_bpmp_mrq_is_supported()`, and `tegra_bpmp_handle_rx()`. The core delegates channel mechanics through `tegra_bpmp_ops` selected by SoC match data.

Transfer control flow has two lanes. Atomic transfers require IRQs disabled, use the dedicated TX channel under `atomic_tx_lock`, ring the doorbell, busy-wait for response readiness, then read and ack the response. Sleepable transfers allocate a threaded channel via semaphore and bitmaps, write with `MSG_ACK | MSG_RING`, ring the doorbell, wait on the channel completion, then read/ack and release the channel. Incoming RX checks the CPU RX channel for firmware MRQs, dispatches registered handlers, then scans busy threaded channels and completes any with ready responses.

Probe allocates the BPMP object, locks, threaded-channel bitmaps, TX/RX/threaded channel structures, calls the SoC transport `init()`, registers a ping MRQ handler, performs an atomic ping, queries the firmware tag with new `MRQ_QUERY_FW_TAG` or old DMA-based `MRQ_QUERY_TAG`, populates child devices, and initializes clock, reset, powergate, and debugfs providers when DT cells or firmware support exist. Suspend marks the BPMP unavailable; resume clears the flag and calls the transport resume op when present. Transfers during suspend require `TEGRA_BPMP_MESSAGE_RESET` to trigger channel reset.

State spans Linux and firmware. Firmware owns service implementation and hardware power/clock state; Linux owns channel allocation bitmaps, completions, MRQ handler list, `suspended`, debugfs dentry pointer, and child provider state. Dependencies include BPMP ABI structs, `soc/tegra/bpmp.h`, IVC helpers, mailbox transports, OF phandles, child platform population, and Tegra clock/reset/powergate helpers.

Risks include error paths after `tegra_bpmp_transfer()` rings the doorbell: if ring or wait fails, the threaded channel allocation can remain set because cleanup happens in `tegra_bpmp_channel_read()`. MRQ handler invocation occurs while holding `bpmp->lock`, so handlers that reenter lock-sensitive paths can deadlock. There is no platform remove path to undo debugfs or child providers. Test signals include atomic ping latency, firmware tag query fallback, concurrent threaded transfers, timeout recovery and channel bitmap release, incoming MRQ ping response, phandle get/put reference behavior, and suspend/resume reset-message behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/bpmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/ivc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/tegra/ivc.c

Tegra IVC ring-buffer protocol library. It implements a two-endpoint shared-memory queue with cache-line-separated ownership, explicit DMA sync for non-coherent peers, frame read/write helpers, and a reset state machine. BPMP uses it as the transport framing layer on Tegra186+.

The shared header has TX-owned count/state and RX-owned count fields, each padded/aligned to 64 bytes. Exported APIs are `tegra_ivc_read_get_next_frame()`, `tegra_ivc_read_advance()`, `tegra_ivc_write_get_next_frame()`, `tegra_ivc_write_advance()`, `tegra_ivc_reset()`, `tegra_ivc_notified()`, `tegra_ivc_align()`, `tegra_ivc_total_queue_size()`, `tegra_ivc_init()`, and `tegra_ivc_cleanup()`.

Read flow verifies the local TX state is established, checks whether RX appears non-empty, invalidates remote-owned counters/frame data if needed, returns an `iosys_map` for the current frame, and advances RX count when consumed. Write flow verifies channel state and space, returns the next TX frame map, flushes frame data, advances TX count, and notifies only on empty-to-non-empty transitions. Reset flow writes `SYNC`, reacts to peer `SYNC`/`ACK` in `tegra_ivc_notified()`, clears counters with memory barriers, and eventually reaches `ESTABLISHED`.

State is entirely in shared memory plus local cached positions. `tegra_ivc_init()` validates alignment, non-overlap, frame-size limits, maps coherent DMA if a peer device is supplied, and records callback/data. Dependencies include `iosys_map`, DMA sync APIs, memory barriers, alignment helpers, and a caller-supplied notify callback.

Risks include security-sensitive counter arithmetic: `tegra_ivc_empty()` deliberately treats over-full remote counters as empty to avoid denial-of-service behavior. Parameter overlap checks account only for `frame_size * num_frames`, while the full queue includes the header; callers should pass separated regions sized by `tegra_ivc_total_queue_size()`. `iosys_map_get_vaddr()` rejects I/O memory for DMA mapping, so peer-DMA mode is for normal memory maps. Test signals include reset handshakes for all state transitions, full/empty boundary behavior, malicious over-full counters, DMA sync on non-coherent peers, alignment rejection, and wraparound at the last frame.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/tegra/ivc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/thead,th1520-aon.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/thead,th1520-aon.c

T-HEAD TH1520 Always-On firmware RPC helper library. It wraps the `"aon"` mailbox channel, serializes request/ack transactions, maps firmware error codes to Linux errno values, and exports a power-resource update helper.

`struct th1520_aon_chan` owns the mailbox channel/client, last common ack, completion, and `transaction_lock`. `th1520_aon_init()` allocates this object, configures a blocking mailbox client with `MAX_TX_TIMEOUT`, installs `th1520_aon_rx_callback()`, requests the named mailbox, and initializes synchronization. `th1520_aon_deinit()` frees the mailbox and object.

`th1520_aon_call_rpc()` is the generic transaction path. It locks out concurrent RPCs, reinitializes completion, stamps protocol version/service/message flags into the request header, sends over mailbox, waits up to three seconds for the RX callback, then converts the firmware ack error code through `th1520_aon_to_linux_errno()`. The RX callback validates that the returned header size matches `th1520_aon_rpc_ack_common` before copying and completing. `th1520_aon_power_update()` builds a packed set-resource-power-mode request with big-endian resource and mode fields and calls the generic RPC path.

State is transient except for the mailbox handle and last ack buffer. Firmware owns actual power state and RPC semantics. Dependencies include the TH1520 AON firmware header macros/types, mailbox client/controller APIs, completions, mutexes, and exported symbols for consumers such as power-domain drivers.

Risks include strict ack-size validation: unexpected future ack formats will be ignored and cause caller timeout. The error map returns `-EEXIST` for `LIGHT_AON_ERR_NOTFOUND`, which is semantically suspicious and should be checked against firmware ABI expectations. `th1520_aon_call_rpc()` returns `th1520_aon_to_linux_errno(ret)` even when `mbox_send_message()` fails, so negative Linux errors outside the firmware enum collapse to `-EIO`; preserving transport errors would aid diagnostics. Test signals include mailbox channel lookup failure, send timeout, malformed ack size, firmware error-code mapping, serialized concurrent callers, and power on/off payload endianness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/thead,th1520-aon.c -->
