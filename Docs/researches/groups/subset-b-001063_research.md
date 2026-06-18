# Research: subset-b-001063

Grouped research for the requested zram block driver and Bluetooth driver files. Each section is wrapped for the reconciliation splitter and keeps the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.c -->
# Research: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.c

## Purpose

`zram_drv.c` implements the Linux compressed RAM block device. It exposes `/dev/zramN` disks whose logical pages are stored as compressed objects in a `zsmalloc` pool, with optional writeback to a configured backing block device and optional multi-compressor recompression. The file owns the block-device operations, sysfs control plane, per-slot locking, compressor lifecycle, metadata allocation, I/O path, writeback/recompression post-processing, debugfs memory tracking, and module hot-add/hot-remove lifecycle.

## Important APIs, Types, And Functions

The primary runtime object is `struct zram` from `zram_drv.h`; this file manipulates its table, `zs_pool`, compressor array, disk, `dev_lock`, stats, and optional writeback/debugfs fields. Slot state is stored in `struct zram_table_entry` through `handle` and packed flags, with helpers such as `get_slot_handle`, `set_slot_size`, `test_slot_flag`, `set_slot_comp_priority`, and `slot_allocated`.

The I/O entry point is `zram_submit_bio`, installed in `zram_devops`. It dispatches reads to `zram_bio_read`, writes to `zram_bio_write`, and discard/write-zeroes to `zram_bio_discard`. Page-level operations are handled by `zram_read_page`, `zram_write_page`, `read_from_zspool`, `write_same_filled_page`, `write_incompressible_page`, and partial-I/O helpers. `slot_free` is the central cleanup routine for in-memory, same-filled, huge, writeback, and post-processing slots.

The sysfs surface includes `disksize`, `initstate`, `reset`, `compact`, `mem_limit`, `mem_used_max`, `idle`, `comp_algorithm`, `algorithm_params`, stats files, and, when configured, `backing_dev`, `writeback`, `writeback_limit`, `writeback_batch_size`, `compressed_writeback`, `recomp_algorithm`, and `recompress`. Device management uses `zram_add`, `zram_remove`, `hot_add_show`, and `hot_remove_store`.

## Control Flow

Module initialization registers a CPU hotplug state for zcomp streams, registers the `zram-control` class, registers a dynamic block major, creates debugfs root state if enabled, and pre-creates `num_devices` devices with `zram_add`. `zram_add` allocates a `struct zram`, reserves an IDR id under `zram_index_mutex`, builds a `gendisk` with PAGE-sized physical limits, installs sysfs groups, sets the default compressor, and publishes the disk at zero capacity. A device becomes usable when userspace writes `disksize`: `disksize_store` allocates the slot table and zsmalloc pool, creates configured compressors, records `zram->disksize`, and updates block capacity.

Writes call `zram_bvec_write` for each bio segment. Full-page writes compress directly through the primary compressor unless the page is same-filled or too large for the huge class. Same-filled pages store the fill element in the slot handle and set `ZRAM_SAME`; incompressible pages are stored uncompressed in zsmalloc and set `ZRAM_HUGE`; normal pages store compressed bytes and a size. The old slot is freed while holding the slot lock before the new handle and flags are installed. Reads lock the slot, read same-filled/huge/compressed objects from zsmalloc, or unlock and read from the backing device if `ZRAM_WB` is set.

Writeback is driven by `writeback_store`. It parses mode/range arguments, scans eligible slots into post-processing buckets using `ZRAM_PP_SLOT`, allocates a bounded request pool from `wb_batch_size`, reserves backing-device bitmap blocks, reads slot contents into request pages, submits write BIOs, and completes them through `zram_writeback_endio` and `zram_writeback_complete`. Recompression follows a similar scan/select pattern, using secondary compressor priorities and replacing an object only if the new zsmalloc class is smaller and below the optional threshold.

## State And Persistence

Runtime state is memory resident except for optional writeback contents stored on the configured backing block device. The zram metadata table records per-logical-page handles, compressed size, and flags such as `ZRAM_SAME`, `ZRAM_WB`, `ZRAM_HUGE`, `ZRAM_IDLE`, `ZRAM_PP_SLOT`, `ZRAM_INCOMPRESSIBLE`, and compressor priority bits. Stats are atomic and reset by `zram_reset_device`. The backing device is opened exclusively before initialization, tracked by `zram->backing_dev`, `zram->bdev`, a bitmap of reserved PAGE-sized blocks, and writeback counters. Reset closes and forgets backing state; it does not preserve zram contents across reset, device removal, or module unload.

`dev_lock` gates device initialization, reset, sysfs configuration, writeback, and recompression. Per-slot bit locks serialize individual slot mutation and are lockdep-instrumented. The `claim` flag, protected by `disk->open_mutex`, blocks opens during reset/removal. Debugfs `block_state` can expose per-slot state and access time when memory tracking is enabled.

## Dependencies And Integration Points

This file integrates the block layer (`gendisk`, `bio`, queue limits, block stats, swap slot free notifications), zsmalloc, zcomp compressor backends, sysfs, debugfs, CPU hotplug, the firmware/file reading API for dictionaries, and optional backing block-device BIO submission. It relies on `zcomp_cpu_up_prepare` and `zcomp_cpu_dead` from the zcomp implementation and on Kconfig features such as `CONFIG_ZRAM_WRITEBACK`, `CONFIG_ZRAM_MULTI_COMP`, `CONFIG_ZRAM_MEMORY_TRACKING`, and `CONFIG_ZRAM_TRACK_ENTRY_ACTIME`.

## Risks

The highest-risk areas are concurrency and state transitions: writeback intentionally releases slot locks while I/O is in flight and relies on `ZRAM_PP_SLOT` to detect slot replacement or free, so any future changes to `slot_free` or scan logic must preserve that protocol. Partial I/O requires read-modify-write of whole pages and, for backing-device reads, sync workers to avoid block-layer deadlocks. Limit accounting is subtle for non-4K PAGE_SIZE, as shown by the writeback limit rounding. `slot_free` updates several counters depending on flag combinations; incorrect flag ordering can underflow stats or leak backing-device bitmap blocks. Firmware/dictionary loading through `algorithm_params` and backing-device path parsing are privileged sysfs surfaces and should remain initialization-only where intended.

## Test Signals

Useful validation signals include sysfs initialization/reset behavior, `mm_stat`, `io_stat`, `bd_stat`, `debug_stat`, and debugfs `block_state`. Functional tests should cover same-filled writes, incompressible writes, read-after-write, discard/write-zeroes, partial I/O on PAGE_SIZE != logical block size, `mem_limit` failures, compressor parameter rejection after initialization, reset refusal while open, hot-add/hot-remove, writeback modes and ranges, compressed writeback readback, backing-device full conditions, and recompression with secondary algorithms and thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.h -->
# Research: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.h

## Purpose

`zram_drv.h` defines the shared data model, constants, and optional feature fields used by `zram_drv.c` and related zram compressor code. It is intentionally compact because zram maintains one table entry per logical page, so memory overhead in this header directly affects the device footprint.

## Important APIs, Types, And Functions

The file defines page and sector geometry constants: `SECTORS_PER_PAGE`, `ZRAM_LOGICAL_BLOCK_SIZE`, and `ZRAM_SECTOR_PER_LOGICAL_BLOCK`. `ZRAM_FLAG_SHIFT` reserves low bits of the packed flags word for compressed object size and high bits for page flags. `ZRAM_COMP_PRIORITY_MASK` reserves two priority bits for multi-compressor selection.

`enum zram_pageflags` enumerates all per-slot flags: same-filled page, entry lock bit, writeback marker, post-processing marker, huge/incompressible markers, idle marker, and compressor priority bits. `struct zram_table_entry` stores a zsmalloc or backing-device handle and a union containing either the bit lock word or packed attributes, plus a `lockdep_map`. When access-time tracking is enabled, `attr.ac_time` is stored beside flags.

`struct zram_stats` contains atomic counters for compressed bytes, failed reads/writes, free notifications, same/huge page counts, stored pages, max zsmalloc pages, missed slot-free notifications, and optional backing-device reads/writes/count. `struct zram` is the device object: it owns the slot table, zsmalloc pool, compressor instances and parameters, gendisk, device rwsem, memory limit, stats, disk size, configured algorithm names, reset claim flag, and optional writeback/debugfs state.

## Control Flow

This header does not execute code, but it shapes all control flow in `zram_drv.c`. The packed entry layout lets I/O paths lock one slot at a time with a bit lock, inspect flags, and decide whether data is same-filled, compressed in zsmalloc, incompressible in zsmalloc, or written back to a backing block. The compressor arrays are indexed by `ZRAM_PRIMARY_COMP`, `ZRAM_SECONDARY_COMP`, and up to `ZRAM_MAX_COMPS`, with those values changing depending on `CONFIG_ZRAM_MULTI_COMP`.

## State And Persistence

All state described here is runtime state. The only persistent-looking reference is the optional backing device handle in `struct zram`, but the zram metadata that maps slots to backing blocks is in memory and is discarded on reset/removal. The `claim` flag is protected by `disk->open_mutex`; the rest of the mutable device fields are primarily guarded by `dev_lock` and per-slot bit locks.

## Dependencies And Integration Points

The header depends on `linux/rwsem.h`, `linux/zsmalloc.h`, and local `zcomp.h`. It exposes types that integrate with the block layer (`gendisk`, `block_device`), file and backing-device APIs (`struct file`, `struct block_device`), debugfs (`struct dentry`), compressor parameter APIs (`struct zcomp_params`), and atomic stats APIs.

## Risks

The packed flags field is size-sensitive. Adding flags without respecting the `BUILD_BUG_ON` in the implementation can overflow `u32 flags`, and changing `ZRAM_FLAG_SHIFT` affects the maximum storable object size. The union that overlays `__lock` and `attr` is delicate: slot locking helpers must keep using the designated lock bit and avoid corrupting packed attributes. Optional fields under writeback and memory tracking create ABI-dependent structure layouts, so code must keep feature guards consistent between declarations and use sites.

## Test Signals

Build coverage should include configurations with and without `CONFIG_ZRAM_MULTI_COMP`, `CONFIG_ZRAM_WRITEBACK`, `CONFIG_ZRAM_MEMORY_TRACKING`, and `CONFIG_ZRAM_TRACK_ENTRY_ACTIME`. Runtime signals include correct sysfs exposure of optional attributes, valid per-slot debugfs flags, stable stats after resets, and successful compression/recompression with priority bits preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/zram/zram_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/Kconfig

## Purpose

This Kconfig file defines the Bluetooth device-driver configuration menu under `depends on BT`. It controls which transport drivers, vendor helper modules, firmware loaders, and protocol submodules are built into the kernel or as modules. For this subset it provides the build-time contract for `ath3k.c`, `bcm203x.c`, `bfusb.c`, `bluecard_cs.c`, `bpa10x.c`, `bt3c_cs.c`, and `btbcm.c`.

## Important Config Symbols

Vendor helper symbols include `BT_INTEL`, `BT_BCM`, `BT_RTL`, `BT_QCA`, and `BT_MTK`; most are tristate helper libraries and select `FW_LOADER` or `REGMAP` as needed. USB HCI support is controlled by `BT_HCIBTUSB` plus protocol booleans such as `BT_HCIBTUSB_BCM`, `BT_HCIBTUSB_MTK`, and `BT_HCIBTUSB_RTL`. UART HCI support is controlled by `BT_HCIUART` and protocol booleans such as `BT_HCIUART_H4`, `BT_HCIUART_BCSP`, `BT_HCIUART_ATH3K`, `BT_HCIUART_BCM`, `BT_HCIUART_QCA`, and others.

The subset-specific symbols are `BT_HCIBCM203X` for the Broadcom Blutonium firmware loader, `BT_HCIBPA10X` for Digianswer BPA 100/105 USB devices, `BT_HCIBFUSB` for AVM BlueFRITZ! USB, `BT_HCIBT3C` for 3Com PC Card devices, `BT_HCIBLUECARD` for Anycom BlueCard PC Card devices, `BT_ATH3K` for Atheros firmware download, and `BT_BCM` for the Broadcom support helper. PCMCIA drivers require `PCMCIA && HAS_IOPORT`; firmware loaders select `FW_LOADER`; HCI transport dependencies select lower protocol support when needed.

## Control Flow

Kconfig selection determines object inclusion through the Bluetooth Makefile. Enabling a user-facing transport pulls in lower-level helpers via `select`, for example `BT_HCIBTUSB_BCM` selects `BT_BCM`, `BT_HCIBPA10X` depends on `BT_HCIUART` and selects `BT_HCIUART_H4`, and `BT_ATH3K` depends on `BT_HCIBTUSB`. This keeps transport drivers from compiling without their protocol or firmware infrastructure.

## State And Persistence

There is no runtime state. The persistent effect is the kernel configuration: built-in, module, or disabled choices determine which driver probes can happen at boot or module load time and which firmware names can be requested by those drivers.

## Dependencies And Integration Points

The file integrates with USB, MMC, TTY, SERIAL_DEV_BUS, GPIOLIB, ACPI, PCMCIA, HAS_IOPORT, PCI, RPMSG, VIRTIO, firmware loading, and vendor helper libraries. The symbols here must remain aligned with object names in `drivers/bluetooth/Makefile` and with source-level `IS_ENABLED(CONFIG_...)` guards such as those in `btbcm.h`.

## Risks

Incorrect `depends on` or `select` relationships can create build failures in unusual configurations, especially for optional subsystems such as PCMCIA, serial device bus, ACPI, NVMEM, and firmware loading. Because several protocol options are booleans under a tristate parent, build combinations should be checked for built-in versus module linkage. User-facing help text and module names must stay in sync with Makefile targets to avoid confusing configuration.

## Test Signals

Strong signals are `allyesconfig`, `allmodconfig`, targeted minimal configs for each subset driver, and configs with USB disabled, PCMCIA disabled, or FW_LOADER modular. Runtime probe tests should confirm each enabled symbol creates the expected module object and that disabled helper symbols yield the expected inline stubs or absent objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/Makefile

## Purpose

This Makefile maps Bluetooth driver Kconfig symbols to kernel objects and defines composite object membership for shared transports. It is the build-system integration point for all Bluetooth source files in this subset.

## Important APIs, Types, And Functions

The key Makefile API is the kernel build `obj-$(CONFIG_...) += object.o` convention. Subset mappings include `CONFIG_BT_HCIBCM203X += bcm203x.o`, `CONFIG_BT_HCIBPA10X += bpa10x.o`, `CONFIG_BT_HCIBFUSB += bfusb.o`, `CONFIG_BT_HCIBT3C += bt3c_cs.o`, `CONFIG_BT_HCIBLUECARD += bluecard_cs.o`, `CONFIG_BT_ATH3K += ath3k.o`, and `CONFIG_BT_BCM += btbcm.o`. The file also maps the main USB, SDIO, UART, vendor, PCIe, virtio, and NXP Bluetooth transports.

For the composite UART driver, `hci_uart-y` starts with `hci_ldisc.o` and conditionally appends protocol objects based on `CONFIG_BT_HCIUART_*`, then assigns `hci_uart-objs := $(hci_uart-y)`. The Marvell driver similarly adds debugfs support conditionally.

## Control Flow

There is no runtime control flow. At build time, Kconfig values expand the `obj-*` variables and determine which `.o` files become built-in, modular, or omitted. Composite object lists control which protocol implementations are linked into `hci_uart.o`.

## State And Persistence

The persistent state is the compiled kernel or module set. There is no generated runtime state in this file, but mistakes here directly affect module availability and symbol resolution.

## Dependencies And Integration Points

The Makefile must stay synchronized with `Kconfig` symbols, module names mentioned in help text, and source files. It integrates with kbuild and with exported symbols between helper modules and transports, for example transports that call Broadcom helper APIs need `btbcm.o` when `CONFIG_BT_BCM` is selected.

## Risks

The main risks are symbol-object drift and composite linkage mistakes. A Kconfig symbol with no matching `obj-*` line silently produces a nonfunctional option, while an object referenced without proper dependency can fail builds. For helper libraries like `btbcm.o`, built-in/module combinations should be checked so consumers do not reference unavailable exported symbols.

## Test Signals

Build tests should cover the subset symbols as modules and built-ins. `make M=drivers/bluetooth` style builds, `allmodconfig`, and targeted tiny configs are good signals. Module packaging should confirm expected module names: `ath3k`, `bcm203x`, `bfusb`, `bluecard_cs`, `bpa10x`, `bt3c_cs`, and `btbcm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/ath3k.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/ath3k.c

## Purpose

`ath3k.c` is a USB firmware download driver for Atheros AR30xx Bluetooth controllers. It does not register an HCI device itself; instead it prepares supported USB devices by loading firmware, patch, and system configuration files, switching them into normal mode, and causing them to re-enumerate for the main Bluetooth USB HCI driver.

## Important APIs, Types, And Functions

`struct ath3k_version` models the vendor `GETVERSION` response, including ROM/build/RAM versions and reference clock. `ath3k_table` is the USB device table for supported AR3011/AR3012 and OEM variants. `ath3k_blist_tbl` marks AR3012 devices requiring patch and sysconfig loading via `BTUSB_ATH3012`.

Firmware transfer helpers include `ath3k_load_firmware` for the legacy `ath3k-1.fw` image and `ath3k_load_fwfile` for AR3012 `.dfu` files. Vendor control helpers include `ath3k_get_state`, `ath3k_get_version`, `ath3k_set_normal_mode`, and `ath3k_switch_pid`. `ath3k_load_patch` selects `ar3k/AthrBT_0x%08x.dfu` based on ROM version and verifies the patch trailer against ROM/build versions. `ath3k_load_syscfg` selects `ar3k/ramps_0x%08x_<clock>.dfu` based on ROM version and reference clock. `ath3k_probe` orchestrates all of this.

## Control Flow

On USB probe, the driver rejects nonzero interface numbers. If the matched id lacks `driver_info`, it searches the AR3012 blacklist table for a more specific match. AR3012 devices with `bcdDevice > 0x0001` are treated as already handled and return `-ENODEV`, allowing another driver to bind. Older AR3012 devices load patch, load syscfg, set normal mode, and send a vendor PID-switch request. Legacy devices request `ath3k-1.fw`, send the first firmware header bytes through a vendor control request, then stream remaining data over bulk endpoint `0x02` in 4096-byte chunks with a short xHCI compatibility delay.

## State And Persistence

The driver keeps no per-interface runtime state beyond the probe call. State lives in the controller firmware state queried by vendor requests. A successful probe changes device firmware state and likely causes USB re-enumeration. Firmware data is requested, streamed, and released during probe.

## Dependencies And Integration Points

The driver depends on USB core, firmware loader, Bluetooth logging helpers, and unaligned little-endian helpers. It is selected by `CONFIG_BT_ATH3K`, which depends on `BT_HCIBTUSB`, because the prepared controller is expected to be used by the standard btusb transport after firmware loading. It advertises `MODULE_FIRMWARE(ath3k-1.fw)` but AR3012 paths also require versioned files under `ar3k/`.

## Risks

Firmware filename generation and version validation are critical. A missing, stale, or mismatched patch is rejected; a syscfg reference-clock mismatch can prevent device startup. Bulk transfer errors can currently return the USB error, but if a short write reports `err == 0` and `len != size`, callers receive zero from `ath3k_load_firmware`; that pattern deserves attention if changing error handling. The device table is large and OEM-heavy, so ID drift can break only specific laptops. Timing delays around xHCI and normal-mode/PID switch should not be casually removed.

## Test Signals

Signals include USB probe logs, firmware request success/failure messages, successful re-enumeration into btusb, and absence of repeated firmware-download loops. Test old AR3011 firmware, AR3012 patch/syscfg, missing firmware, mismatched patch trailer, and device IDs with `bcdDevice > 0x0001`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/ath3k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bcm203x.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bcm203x.c

## Purpose

`bcm203x.c` is a firmware loader for Broadcom Blutonium BCM2033 USB Bluetooth devices. It loads a mini driver, selects controller memory, streams the main firmware, checks completion, and then exits so the device can operate with its loaded firmware.

## Important APIs, Types, And Functions

`bcm203x_table` matches USB device `0x0a5c:0x2033`. `struct bcm203x_data` stores the USB device, loader state, delayed work, shutdown flag, single URB, transfer buffer, copied firmware bytes, firmware size, and sent offset. State constants cover `BCM203X_LOAD_MINIDRV`, `SELECT_MEMORY`, `CHECK_MEMORY`, `LOAD_FIRMWARE`, `CHECK_FIRMWARE`, `RESET`, and `ERROR`.

`bcm203x_complete` is the URB completion state machine. `bcm203x_work` submits the URB from process context after deliberate small delays. `bcm203x_probe` allocates state, requests `BCM2033-MD.hex` and `BCM2033-FW.bin`, prepares the initial bulk URB, stores interface data, and schedules work. `bcm203x_disconnect` stops work, kills the URB, and frees firmware/buffer state.

## Control Flow

Probe only handles interface 0. It allocates one URB and a buffer sized for the larger of mini-driver size and 4096 bytes, copies mini-driver data into that buffer, fills a bulk URB to OUT endpoint `0x02`, then loads and copies the main firmware into private memory. Completion of the mini-driver bulk write sends `#` to select memory, then schedules work. The subsequent interrupt read from IN endpoint `0x81` expects `#`; if present, firmware chunks of up to 4096 bytes are bulk-written until complete. Then an interrupt read expects `.` to confirm firmware load. Any URB status or unexpected marker moves to error state.

## State And Persistence

The state machine is stored in `data->state`; firmware bytes are copied because the firmware object is released during probe. The driver does not register an HCI device and keeps no persistent host-side state after disconnect. Device firmware state persists in the controller until reset or power loss.

## Dependencies And Integration Points

The driver uses USB bulk and interrupt URBs, the firmware loader, kernel workqueues, and Bluetooth logging. Kconfig selects `FW_LOADER` for `BT_HCIBCM203X`, and the module declares both firmware names.

## Risks

The state machine relies on a single reusable URB and buffer, so completion and disconnect ordering must remain strict. `bcm203x_disconnect` assumes interface data is present and kills the URB after setting shutdown and cancelling work. Any change that releases firmware memory before copying would be invalid because the main firmware is sent asynchronously after probe returns. Error states log failures but do not retry. Endpoint addresses are hard-coded, so this is intentionally specific to the Blutonium loader interface.

## Test Signals

Useful signals are successful requests for both firmware files, expected `#` and `.` handshakes, no URB status errors, clean disconnect during active load, and final device usability by the Bluetooth stack. Negative tests should cover missing mini-driver, missing firmware, short memory-select response, and USB unplug during scheduled work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bcm203x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bfusb.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bfusb.c

## Purpose

`bfusb.c` is the HCI USB transport driver for AVM BlueFRITZ! USB Bluetooth devices. It loads device firmware, registers an HCI device, fragments outgoing HCI frames into the device block format, reassembles incoming block streams, and manages USB bulk URBs.

## Important APIs, Types, And Functions

`struct bfusb_data` stores the HCI device, state bits, USB device and endpoint addresses, bulk packet size, an rwlock, TX queue, RX reassembly skb, and pending/completed URB skb queues. `bfusb_data_scb` stores an URB pointer in skb control data. TX flow is handled by `bfusb_send_frame`, `bfusb_tx_wakeup`, `bfusb_send_bulk`, and `bfusb_tx_complete`. RX flow is handled by `bfusb_rx_submit`, `bfusb_rx_complete`, and `bfusb_recv_block`. Firmware loading is in `bfusb_load_firmware`; USB binding and HCI registration are in `bfusb_probe` and `bfusb_disconnect`.

## Control Flow

Probe checks for at least two endpoints, records endpoint addresses, initializes queues and locks, requests `bfubase.frm`, and calls `bfusb_load_firmware`. Firmware loading switches the device to loading configuration 1, streams firmware blocks over bulk OUT, sends a zero-length bulk request, then switches to running configuration 2 and resets toggles. After firmware load, the driver allocates an HCI device with `HCI_USB` bus, installs callbacks, sets `HCI_QUIRK_BROKEN_LOCAL_COMMANDS`, and registers it.

Opening the HCI device submits two bulk RX URBs. Incoming URBs are parsed as BFUSB blocks with headers, start/continuation/end flags, and payload lengths; valid completed HCI frames are handed to `hci_recv_frame`. Sending prepends the HCI packet type, wraps data into up to 256-byte BFUSB blocks, adds a short terminator block if the resulting transfer is a multiple of bulk max packet size, queues it, and pumps up to two concurrent bulk TX URBs.

## State And Persistence

Runtime state is queue-based and volatile. `pending_tx` limits concurrent TX URBs. `pending_q` and `completed_q` recycle URBs using skb control blocks. `reassembly` holds partially received HCI frames across URB completions. Firmware load changes device configuration but the driver stores no persistent firmware state after probe.

## Dependencies And Integration Points

The driver depends on USB, firmware loader, skbuff APIs, Bluetooth HCI core, and module USB-driver registration. It is enabled by `BT_HCIBFUSB` and declares `bfubase.frm` as required firmware. HCI integration is through `hci_alloc_dev`, `hci_register_dev`, `hci_recv_frame`, stats counters, and callback hooks.

## Risks

The custom block parser is a high-risk area: malformed headers, payload lengths extending past the URB buffer, unexpected start/continuation flags, and missing packet-type handling can corrupt reassembly or leak skbs if changed carelessly. Locking uses an rwlock around queue and URB state; callbacks can run in atomic context. `bfusb_disconnect` assumes `usb_get_intfdata` returns valid data, so probe failure paths must not leave partial interface data. Firmware loading uses fixed configuration numbers and endpoint assumptions.

## Test Signals

Signals include successful firmware load, HCI registration, open/close cycles without URB leaks, TX stats increasing for command/ACL/SCO frames, RX reassembly of split frames, error counters on malformed blocks, clean unplug during active RX/TX, and correct behavior when firmware is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bfusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bluecard_cs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bluecard_cs.c

## Purpose

`bluecard_cs.c` is the PCMCIA HCI driver for Anycom BlueCard Bluetooth cards. It directly programs card I/O registers, manages two transmit and receive windows, controls LEDs and baud rate, parses HCI packets from byte streams, and registers an `HCI_PCCARD` device.

## Important APIs, Types, And Functions

`struct bluecard_info` stores the PCMCIA device, HCI device, spinlock, LED timer, TX queue/state, RX parser state/count/skb, control register shadow, and hardware state bits. Hardware constants define command, interrupt, control, RX control, reset, and LED registers. TX functions include `bluecard_write`, `bluecard_write_wakeup`, and `bluecard_hci_send_frame`. RX and interrupt handling is in `bluecard_read`, `bluecard_receive`, and `bluecard_interrupt`. Lifecycle functions include `bluecard_open`, `bluecard_close`, `bluecard_probe`, `bluecard_config`, and `bluecard_release`.

## Control Flow

Probe allocates `bluecard_info`, enables IRQ configuration, and calls `bluecard_config`. Configuration claims an 8-bit I/O range by probing addresses, requests IRQ, enables the PCMCIA device, and opens the card. `bluecard_open` allocates an HCI device, detects card ID and LED capabilities from register `0x30`, resets and powers the card, enables interrupts, starts RX buffers, marks hardware ready, configures RTS threshold, waits before first traffic, and registers HCI.

The interrupt handler disables card interrupts, reads `REG_INTERRUPT`, handles RX buffer one/two ready bits by reading windows and acknowledging them, handles TX buffer ready bits by setting state flags and waking TX, then re-enables interrupts. RX parsing is a byte-oriented HCI state machine from packet type to header to payload; complete frames are delivered with `hci_recv_frame`. TX prepends packet type, writes up to 15 bytes into the selected hardware buffer, commands the FPGA to send, and toggles buffer selection. Special packet types with high bits encode baud-rate changes and trigger RTS/baud sequencing delays.

## State And Persistence

All state is volatile host/card state. `ctrl_reg` mirrors the card control register so bit updates are coherent. `hw_state` records readiness and LED features. `tx_state` records which hardware buffer is ready and whether TX is active. `rx_state`, `rx_count`, and `rx_skb` persist the HCI parser across interrupts. LED state is timer-driven and changes hardware LED output. Card contents do not persist across close or removal.

## Dependencies And Integration Points

The driver depends on PCMCIA core, ISA-style I/O port access, timers, spinlocks, skbuffs, and Bluetooth HCI core. It is built by `CONFIG_BT_HCIBLUECARD`, which requires `PCMCIA && HAS_IOPORT`. Device matching uses PCMCIA product IDs for BlueCard/LSE variants.

## Risks

This is register-level code with many timing assumptions. The baud-rate path uses blocking delays and special internal packet types, so changing TX queue handling can disturb initialization. The RX parser allocates `HCI_MAX_FRAME_SIZE` skbs and trusts header lengths; malformed hardware bytes can drive error counters and skb frees. Shared IRQ handling must return `IRQ_NONE` only for clearly unrelated interrupts. Cleanup must stop the LED timer and unregister/free HCI exactly once.

## Test Signals

Validation signals include successful PCMCIA I/O/IRQ allocation, HCI registration, card reset/power sequencing, interrupt-driven RX/TX, baud-rate setup on PCCARD-ID devices, LED timer behavior, clean detach, and HCI stats. Negative coverage should include no usable port range, IRQ request failure, card removal during TX/RX, unknown HCI packet type, and partial TX buffer writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bluecard_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bpa10x.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bpa10x.c

## Purpose

`bpa10x.c` is the USB HCI driver for Digianswer/Tektronix BPA 100/105 Bluetooth sniffer devices. It registers a USB-backed HCI device, submits interrupt and bulk RX URBs, sends HCI packets over vendor control or bulk transfers, and supports a diagnostic/sniffer mode command.

## Important APIs, Types, And Functions

`struct bpa10x_data` stores the HCI device, USB device, TX/RX URB anchors, two receive reassembly skbs, and an embedded `struct hci_uart` used with H4 receive parsing helpers. `bpa10x_recv_pkts` declares H4 packet descriptors for ACL, SCO, events, and vendor diagnostic packets. `bpa10x_open`, `bpa10x_close`, `bpa10x_flush`, `bpa10x_setup`, `bpa10x_send_frame`, and `bpa10x_set_diag` are HCI callbacks. USB binding is handled by `bpa10x_probe` and `bpa10x_disconnect`.

## Control Flow

Probe accepts only interface 0, allocates state and an HCI device, initializes USB anchors, attaches HCI callbacks, sets `HCI_QUIRK_RESET_ON_CLOSE`, registers the device, and stores interface data. Opening submits one interrupt RX URB on endpoint `0x81` and one bulk RX URB on endpoint `0x82`. RX completion selects one of two reassembly slots based on pipe type, feeds bytes into `h4_recv_buf`, handles corrupted packets by incrementing `err_rx`, then reanchors and resubmits the URB.

Sending prepends the HCI packet type. Command packets are sent as vendor control requests on endpoint zero with a dynamically allocated setup packet. ACL and SCO packets go over bulk OUT endpoint `0x02`. Completion updates TX stats, frees the setup packet, and frees the skb. Setup sends vendor command `0xfc0e` with request byte `0x07` to read a revision string and stores it as firmware info. Diagnostic mode sends the same opcode with enable state.

## State And Persistence

Runtime state is anchored URBs plus RX reassembly skbs. `tx_anchor` and `rx_anchor` allow close/flush to kill outstanding URBs. No firmware is loaded and no persistent state is stored by the driver; diagnostic mode is a controller runtime setting.

## Dependencies And Integration Points

The driver depends on USB core, Bluetooth HCI core, `hci_uart.h` H4 parsing helpers, and skbuff APIs. Kconfig requires `BT_HCIUART` and USB and selects `BT_HCIUART_H4`, reflecting its use of H4 receive parsing despite being a USB transport.

## Risks

URB lifetime is central. Completion frees skbs and setup packets, while anchors control cancellation; changes must avoid use-after-free during disconnect. RX resubmission occurs from completion context with `GFP_ATOMIC`, so allocation and error paths must stay nonblocking. Command send failure frees setup packets only in the error path; completion handles the successful path. The driver uses fixed endpoint addresses and a vendor command contract specific to these sniffer devices.

## Test Signals

Signals include successful HCI registration, open submitting both RX URBs, revision string logging from setup, command/ACL/SCO TX stats, diagnostic mode toggling while running, clean close/flush/unplug behavior, and corrupted H4 packet error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bpa10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bt3c_cs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bt3c_cs.c

## Purpose

`bt3c_cs.c` is the PCMCIA HCI driver for the 3Com Bluetooth PC Card. It claims PCMCIA I/O resources, loads `BT3CPCC.bin` firmware into the card using a Motorola S-record-like format, registers an `HCI_PCCARD` device, and handles interrupt-driven RX/TX through card registers.

## Important APIs, Types, And Functions

`struct bt3c_info` stores the PCMCIA device, HCI device, spinlock, TX queue/state, RX parser state/count/skb. Low-level I/O helpers `bt3c_address`, `bt3c_put`, `bt3c_io_write`, `bt3c_get`, and `bt3c_read` access card address/data/control registers. TX is handled by `bt3c_write`, `bt3c_write_wakeup`, and `bt3c_hci_send_frame`. RX and IRQ handling are in `bt3c_receive` and `bt3c_interrupt`. Firmware loading is in `bt3c_load_firmware`. PCMCIA configuration uses `bt3c_check_config`, `bt3c_check_config_notpicky`, and `bt3c_config`.

## Control Flow

Probe allocates state, enables IRQ and automatic PCMCIA VPP/IO configuration, and calls `bt3c_config`. Configuration first loops over normal config tuples, then falls back to less picky standard serial-port-like base addresses and finally any free port. It requests IRQ, enables the device, and calls `bt3c_open`. Open allocates an HCI device, installs callbacks, requests `BT3CPCC.bin`, loads firmware, waits one second, then registers HCI.

The firmware loader resets card registers, parses S-record lines, validates checksum, writes S3 records into card memory through address/data ports, boots the controller at address `0x3000`, and clears status/FIFO registers. Interrupts read a status register when the control interrupt bit is set, report antenna state changes, receive available bytes, and wake TX when transmit complete. RX parsing is a byte-oriented HCI packet state machine. TX prepends packet type, queues the skb, and under spinlock writes the frame to FIFO address `0x7080` and length register `0x7005`.

## State And Persistence

State is volatile. Firmware is loaded on open/probe and not preserved by the driver across removal. `tx_state` gates one active send at a time, and `rx_state`/`rx_count`/`rx_skb` preserve packet parser progress across interrupts. The HCI device exists until release/detach, where it is unregistered and freed.

## Dependencies And Integration Points

The driver depends on PCMCIA, I/O port access, firmware loader, spinlocks, skbuffs, and Bluetooth HCI core. It is built by `CONFIG_BT_HCIBT3C`, which selects `FW_LOADER` and requires `PCMCIA && HAS_IOPORT`. The module declares `BT3CPCC.bin`.

## Risks

Firmware parsing is sensitive to record format, sizes, and checksum math. Bad input can abort with `-EFAULT`, `-EINVAL`, or `-EILSEQ`; any parser rewrite should preserve bounds assumptions around `ptr` and `count`. Register addresses and delays are hardware-specific. Interrupt handling shares IRQ lines and must not claim unrelated interrupts. Cleanup must handle failed firmware load without leaving a registered HCI device or enabled PCMCIA function.

## Test Signals

Signals include successful port selection, IRQ request, firmware request and load, HCI registration, command/ACL/SCO transmit stats, RX frame delivery, antenna status logging, and clean detach. Negative tests should cover malformed firmware records, checksum failure, missing firmware, no usable port range, and card removal during interrupt activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/bt3c_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.c

## Purpose

`btbcm.c` is a shared Broadcom Bluetooth helper library used by transport drivers. It validates or programs controller addresses, sends Broadcom vendor commands, loads PatchRAM firmware, reads controller identity and feature data, chooses firmware filenames, and applies Broadcom-specific HCI quirks.

## Important APIs, Types, And Functions

Exported functions include `btbcm_check_bdaddr`, `btbcm_set_bdaddr`, `btbcm_read_pcm_int_params`, `btbcm_write_pcm_int_params`, `btbcm_patchram`, `btbcm_initialize`, `btbcm_finalize`, `btbcm_setup_patchram`, and `btbcm_setup_apple`. Helper functions read local name, local version, verbose config, controller features, and USB product info using synchronous HCI commands. `bcm_uart_subver_table` and `bcm_usb_subver_table` map `lmp_subver` values to firmware hardware names. `btbcm_get_board_name` derives a firmware board suffix from the device-tree root compatible string when OF is enabled.

## Control Flow

`btbcm_setup_patchram` calls `btbcm_initialize`, then `btbcm_finalize`. Initialization resets the controller, reads local version, optionally reads verbose info, features, and name, maps subversion to a hardware name, logs version/build identity, and, if firmware has not already been loaded, builds a prioritized list of up to four firmware names. USB devices add a `-vid-pid` postfix read from vendor command `0xfc5a`; device-tree board names add an additional suffix. The first successfully requested `.hcd` file is sent through `btbcm_patchram`, which starts minidrv mode with command `0xfc2e`, waits, iterates embedded HCI command records from the firmware, sends each synchronously, and waits after launch.

Finalization reruns initialization if firmware was loaded, checks for default/invalid Broadcom addresses, and sets `HCI_QUIRK_STRICT_DUPLICATE_FILTER`. Address checking compares the controller BDADDR against known factory placeholder addresses and tries to set a real address from EFI variable `BDADDR` before marking `HCI_QUIRK_INVALID_BDADDR`. The Apple setup path reads and logs identity information without PatchRAM loading and also sets strict duplicate filtering.

## State And Persistence

The file keeps little module-global state beyond static tables. State is mostly in the controller and in caller-provided `fw_load_done`. Firmware loading changes controller RAM state and usually requires reinitialization. EFI BDADDR is persistent platform state; the driver reads it and writes it into the controller if needed. HCI quirks persist in `struct hci_dev` for the device lifetime.

## Dependencies And Integration Points

The helper depends on HCI core synchronous command APIs, firmware loader, EFI runtime services, DMI, device tree, unaligned access helpers, and Bluetooth address utilities. It exports symbols for USB, UART, SDIO, and platform Broadcom transports selected through `CONFIG_BT_BCM`. DMI entries mark specific Apple systems with broken Read LE Min/Max Tx Power behavior.

## Risks

PatchRAM parsing trusts the firmware as a stream of HCI command headers and payloads but validates remaining size before each command. Filename selection is compatibility-critical; changing order can alter which firmware file wins on systems with board-specific blobs. `btbcm_initialize` returns success even when no firmware is found after logging attempted names, which lets transports continue with ROM firmware; callers must understand that behavior. Address placeholder matching is conservative and should be updated carefully because marking invalid addresses changes user-visible Bluetooth identity behavior.

## Test Signals

Signals include HCI command success for reset/version/vendor reads, expected firmware filename attempts, PatchRAM command progress, reinitialization after patch, BDADDR validation, EFI BDADDR application, and quirks set for duplicate filtering, invalid BDADDR, and Apple DMI transmit-power behavior. Test USB and UART buses because firmware naming tables and USB product postfix handling differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.h

## Purpose

`btbcm.h` is the public header for the Broadcom Bluetooth helper library. It defines vendor command parameter layouts and exposes helper APIs to transport drivers while providing no-op or unsupported inline stubs when `CONFIG_BT_BCM` is disabled.

## Important APIs, Types, And Functions

The header defines Broadcom UART clock constants `BCM_UART_CLOCK_48MHZ` and `BCM_UART_CLOCK_24MHZ`. Packed command parameter structs include `bcm_update_uart_baud_rate`, `bcm_write_uart_clock_setting`, `bcm_set_sleep_mode`, `bcm_set_pcm_int_params`, and `bcm_set_pcm_format_params`. These model vendor command payloads used by Broadcom transports for UART speed/clock, sleep behavior, and PCM/I2S audio interface setup.

When `IS_ENABLED(CONFIG_BT_BCM)` is true, the header declares `btbcm_check_bdaddr`, `btbcm_set_bdaddr`, `btbcm_patchram`, PCM parameter read/write helpers, `btbcm_setup_patchram`, `btbcm_setup_apple`, `btbcm_initialize`, and `btbcm_finalize`. When disabled, inline stubs return `-EOPNOTSUPP` for operations that require the helper module and zero for setup/finalize routines that callers may treat as optional.

## Control Flow

There is no runtime logic beyond inline stubs. The header controls compile-time call behavior: transports can include it unconditionally, and the compiler either binds to exported helper symbols or inlines fallback behavior depending on Kconfig. This reduces preprocessor conditionals in transport drivers.

## State And Persistence

The structs describe transient HCI vendor command payloads. No persistent state is defined here. Callers store any runtime state, such as firmware load completion, HCI quirks, or UART baud settings.

## Dependencies And Integration Points

The declarations expect Bluetooth HCI types such as `struct hci_dev`, `bdaddr_t`, and `struct firmware` to be visible through including contexts. The header integrates Kconfig with source-level availability through `IS_ENABLED(CONFIG_BT_BCM)`. It is consumed by Broadcom-capable transports and implemented by `btbcm.c`.

## Risks

The packed layout of vendor command structs is an ABI contract with Broadcom firmware; padding or field order changes would break commands. Stub return values matter: setup stubs returning zero can allow generic transport initialization to continue without Broadcom-specific setup, while direct helper calls return `-EOPNOTSUPP`. Changes should preserve this distinction. Long prototype lines should remain synchronized with exported implementations in `btbcm.c`.

## Test Signals

Build tests should cover both `CONFIG_BT_BCM=y/m` and disabled configurations for transports that include this header. Runtime tests with `BT_BCM` enabled should exercise PatchRAM setup, BDADDR checks, PCM parameter commands, and Apple setup. Disabled-helper builds should confirm transports either avoid unsupported direct calls or handle `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/bluetooth/btbcm.h -->
