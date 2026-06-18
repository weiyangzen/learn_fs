# subset-b-004018 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/tegra-hsp.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/tegra-hsp.c

## Purpose
`tegra-hsp.c` implements the NVIDIA Tegra Hardware Synchronization Primitive mailbox controller. It exposes two mailbox controller instances: doorbells for lightweight notifications between masters and shared mailboxes for 32-bit or 128-bit payload exchange.

## Important APIs, Types, and Functions
Core types are `struct tegra_hsp`, `struct tegra_hsp_doorbell`, `struct tegra_hsp_mailbox`, `struct tegra_hsp_channel`, and `struct tegra_hsp_soc`. Mailbox operations are split between `tegra_hsp_db_ops` and `tegra_hsp_sm_ops`. Important routines include `tegra_hsp_doorbell_irq()`, `tegra_hsp_shared_irq()`, `tegra_hsp_doorbell_startup()`, `tegra_hsp_mailbox_send_data()`, `tegra_hsp_mailbox_flush()`, `tegra_hsp_db_xlate()`, `tegra_hsp_sm_xlate()`, `tegra_hsp_probe()`, and `tegra_hsp_resume()`.

## Control Flow, State, and Persistence
Probe maps the HSP register block, reads the dimensioning register, discovers shared and doorbell IRQs, allocates mailbox channels, registers two mailbox controllers, then requests interrupts. Doorbell clients are translated from device-tree master IDs, enabled through the CCPLEX doorbell's enable register at startup, and signaled by writing `HSP_DB_TRIGGER`. Shared mailbox clients choose RX/TX and 32-bit/128-bit modes via phandle flags. TX writes data, marks the mailbox full, and enables EMPTY interrupts until `tegra_hsp_shared_irq()` observes completion. RX handles FULL interrupts and clears registers after delivering data. Runtime state lives in the `hsp->mask` interrupt-enable bitmap, mailbox producer flags, channel `con_priv`, and SoC capability tables; no persistent storage is used beyond hardware registers restored on resume.

## Dependencies and Integration Points
The driver depends on Linux mailbox controller APIs, platform device probing, OF match data, IRQ handling, Tegra fuse silicon detection, PM resume hooks, and `dt-bindings/mailbox/tegra186-hsp.h`. It integrates with device-tree compatibles for Tegra186, Tegra194, Tegra234, and Tegra264 and with clients using HSP phandles.

## Risks and Test Signals
Key risks are interrupt storms from level-triggered EMPTY interrupts, stale `chan` pointers during early doorbell IRQs, incorrect dimensioning shifts for new SoCs, wrong 128-bit mailbox selection, and missed resume reprogramming. Tests should exercise DT xlate paths, startup/shutdown mask changes, full/empty IRQ ordering, flush timeout behavior, suspend/resume with active clients, and unsupported SoC capability combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/tegra-hsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ti-msgmgr.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/ti-msgmgr.c

## Purpose
`ti-msgmgr.c` implements the TI Message Manager and AM654 Secure Proxy mailbox controller. It maps SoC-specific queue/thread register windows into mailbox channels used by firmware protocols such as TI SCI.

## Important APIs, Types, and Functions
Important structures are `ti_msgmgr_desc`, `ti_msgmgr_valid_queue_desc`, `ti_queue_inst`, and `ti_msgmgr_inst`. Core routines are `ti_msgmgr_queue_get_num_messages()`, `ti_msgmgr_queue_is_error()`, `ti_msgmgr_queue_rx_data()`, `ti_msgmgr_queue_rx_interrupt()`, `ti_msgmgr_last_tx_done()`, `ti_msgmgr_send_data()`, `ti_msgmgr_queue_startup()`, `ti_msgmgr_queue_shutdown()`, `ti_msgmgr_of_xlate()`, `ti_msgmgr_queue_setup()`, `ti_msgmgr_suspend()`, `ti_msgmgr_resume()`, and `ti_msgmgr_probe()`.

## Control Flow, State, and Persistence
Probe selects a descriptor from OF match data, maps data/status/control resources, creates queue instances and mailbox channels, and registers the controller. For legacy Message Manager, valid queue/proxy pairs come from static descriptors; for Secure Proxy, each thread is exposed and direction is read at channel startup from the control register. TX writes message words in order and writes zero through the final register to complete transmission. RX reads every 32-bit register because the final read acknowledges the hardware queue. Suspend disables RX IRQs and marks RX channels polled so noirq TI SCI calls can still receive responses; resume restores IRQ mode. State is in queue direction, IRQ number, `rx_buff`, `polled_rx_mode`, mapped register pointers, and descriptor limits; persistence is the hardware FIFO/register state, not a filesystem format.

## Dependencies and Integration Points
The driver uses mailbox controller APIs, platform resource mapping by name, OF IRQ lookup, PM ops, `readl_poll_timeout_atomic()`, and `linux/soc/ti/ti-msgmgr.h` message objects. It binds `ti,k2g-message-manager` and `ti,am654-secure-proxy`.

## Risks and Test Signals
Risks include using sub-32-bit IO on queue registers, incorrect queue/proxy DT cells, Secure Proxy direction changes, shared IRQ spurious events, RX buffer lifetime across startup/shutdown, and suspend-time polling regressions. Tests should cover max and trailing-byte message sizes, invalid phandle args, TX credit exhaustion, RX IRQ and polled RX paths, suspend/resume with SCI traffic, and secure-proxy error/status masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ti-msgmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/zynqmp-ipi-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/zynqmp-ipi-mailbox.c

## Purpose
`zynqmp-ipi-mailbox.c` implements the Xilinx ZynqMP and Versal Inter-Processor Interrupt mailbox controller. It exposes per-remote-agent TX/RX mailbox channels backed by IPI firmware calls and optional shared memory message buffers.

## Important APIs, Types, and Functions
Key types are `zynqmp_ipi_pdata`, `zynqmp_ipi_mbox`, and `zynqmp_ipi_mchan`. Important routines include `zynqmp_ipi_fw_call()`, `zynqmp_ipi_interrupt()`, `zynqmp_sgi_interrupt()`, `zynqmp_ipi_peek_data()`, `zynqmp_ipi_last_tx_done()`, `zynqmp_ipi_send_data()`, `zynqmp_ipi_startup()`, `zynqmp_ipi_shutdown()`, `zynqmp_ipi_mbox_probe()`, `zynqmp_ipi_setup()`, `versal_ipi_setup()`, `xlnx_mbox_init_sgi()`, `zynqmp_ipi_probe()`, and `zynqmp_ipi_free_mboxes()`.

## Control Flow, State, and Persistence
Top-level probe reads the local IPI ID, allocates private data for child mailbox nodes, registers one child device/controller per remote ID, then configures either an SPI/shared IRQ or per-CPU SGI path. Channel startup opens the firmware mailbox once per TX/RX pair and enables notification IRQs for RX. TX copies request data into the request buffer, then invokes `SMC_IPI_MAILBOX_NOTIFY`; RX responses use `SMC_IPI_MAILBOX_ACK` after optional response-buffer writes. Interrupt handling polls firmware status per remote mailbox, copies pending request data from IO memory into the preallocated `zynqmp_ipi_message`, and delivers it to the mailbox core. State includes per-channel `is_opened`, buffer mappings/sizes, remote/local IDs, SGI mappings, and firmware call method. The driver persists no data itself; correctness depends on firmware-visible message buffer contents and IPI status.

## Dependencies and Integration Points
The driver depends on ARM SMCCC SMC/HVC calls, mailbox controller APIs, OF child nodes and `reg-names`, IRQ domains, CPU hotplug, per-CPU IRQs, and `linux/mailbox/zynqmp-ipi-message.h`. It binds `xlnx,zynqmp-ipi-mailbox` and `xlnx,versal-ipi-mailbox`.

## Risks and Test Signals
Risks include incorrect buffer resource pairing, SGI hotplug cleanup using dynamic CPUHP state, status/ack races, missing bounds when buffers are absent, and firmware method mismatches. Tests should cover buffered and bufferless Versal layouts, invalid IPI IDs, TX/RX startup ordering, interrupt delivery through SPI and SGI, CPU hotplug cycles, message length limits, and remove cleanup after partial child registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/zynqmp-ipi-mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mcb/Kconfig

## Purpose
This Kconfig file defines build-time configuration for MEN Chameleon Bus support and its PCI and LPC carriers.

## Important APIs, Types, and Functions
It declares `MCB` as the parent tristate, `MCB_PCI` as the PCI carrier option, and `MCB_LPC` as the LPC/non-PCI carrier option. `MCB` depends on `HAS_IOMEM`; `MCB_PCI` additionally depends on `PCI`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Its state is the kernel configuration graph: enabling `MCB` permits the carrier submenu, and carrier selections determine which modules are built.

## Dependencies and Integration Points
It integrates with Kbuild and the matching `drivers/mcb/Makefile`. The help text documents module names `mcb.ko`, `mcb-pci.ko`, and `mcb-lpc.ko`.

## Risks and Test Signals
Risks are dependency drift between carrier code and Kconfig, missing `HAS_IOMEM`, or help text/module-name mismatch. Test signals are `allyesconfig`, `allmodconfig`, `randconfig`, and builds with `MCB=y/m`, `MCB_PCI=y/m`, and `MCB_LPC=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mcb/Makefile

## Purpose
The Makefile wires MCB objects into Kbuild.

## Important APIs, Types, and Functions
It builds `mcb.o` from `mcb-core.o` and `mcb-parse.o` under `CONFIG_MCB`, and separately builds `mcb-pci.o` and `mcb-lpc.o` for their carrier configs.

## Control Flow, State, and Persistence
There is no runtime flow. Link composition matters because `mcb-core.o` exports the bus API and `mcb-parse.o` exports Chameleon parsing used by carriers.

## Dependencies and Integration Points
The file depends on the symbols declared in `drivers/mcb/Kconfig` and Kbuild's `obj-*`/`*-y` conventions. It is the build integration point for MCB namespace exports imported by carrier modules.

## Risks and Test Signals
Risks include omitting parser objects from the core module or changing module boundaries without adjusting namespace imports. Test signals are modular and built-in builds for each config combination and `modpost` namespace/export validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-core.c -->
# sources/distributed-fs/ceph-client/drivers/mcb/mcb-core.c

## Purpose
`mcb-core.c` implements the Linux bus type for MEN Chameleon Bus devices. It lets carrier drivers allocate MCB buses and devices while function drivers bind by Chameleon device IDs.

## Important APIs, Types, and Functions
The file defines matching/probe/remove/shutdown callbacks for `mcb_bus_type`, sysfs attributes for carrier metadata, and exported APIs such as `__mcb_register_driver()`, `mcb_unregister_driver()`, `mcb_device_register()`, `mcb_alloc_bus()`, `mcb_release_bus()`, `mcb_bus_get()`, `mcb_bus_put()`, `mcb_alloc_dev()`, `mcb_free_dev()`, `mcb_bus_add_devices()`, `mcb_get_resource()`, `mcb_request_mem()`, `mcb_release_mem()`, and `mcb_get_irq()`.

## Control Flow, State, and Persistence
`fs_initcall(mcb_init)` registers the bus. Carriers call `mcb_alloc_bus()`, parse Chameleon tables into `mcb_device` objects, register them, then call `mcb_bus_add_devices()` to bind drivers. Driver probe pins the carrier module and device until remove. Bus numbering is allocated by `IDA`; bus lifetime is tied to device release and `mcb_bus_put()`. Runtime state lives in kernel device model structures, bus refs, resource descriptors, and sysfs-visible Chameleon header fields. There is no durable persistence.

## Dependencies and Integration Points
It depends on `linux/mcb.h`, the kernel device model, module refs, IDA, resource APIs, and sysfs attributes. Carrier drivers import the `MCB` namespace and function drivers use MCB registration helpers.

## Risks and Test Signals
Risks include global unregister scanning all devices on the bus type rather than only a carrier's children, module ref imbalance on failed probe/remove, resource lifetime mistakes, and IRQ fallback returning uninitialized resources. Tests should cover multiple carriers, failed function-driver probe, remove while devices are bound, sysfs attribute reads, resource request conflicts, and namespace/modpost checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-internal.h -->
# sources/distributed-fs/ceph-client/drivers/mcb/mcb-internal.h

## Purpose
`mcb-internal.h` defines shared private constants and Chameleon descriptor layouts used by the MCB parser and carrier drivers.

## Important APIs, Types, and Functions
It defines MEN/Altera PCI IDs, `CHAMELEONV2_MAGIC`, `CHAM_HEADER_SIZE`, descriptor type and bus type enums, packed `chameleon_fpga_header`, `chameleon_gdd`, `chameleon_bdd`, and `chameleon_bar` structures, field extraction macros such as `GDD_IRQ()`, `GDD_DEV()`, `GDD_BAR()`, and `BAR_CNT()`, plus the parser prototype `chameleon_parse_cells()`.

## Control Flow, State, and Persistence
The header has no executable flow. Its layouts describe on-device FPGA Chameleon tables and therefore define how persistent hardware metadata is interpreted into runtime `mcb_bus` and `mcb_device` objects.

## Dependencies and Integration Points
It depends on Linux types and `linux/mcb.h` definitions such as `CHAMELEON_FILENAME_LEN`. It is included by `mcb-parse.c`, `mcb-pci.c`, and `mcb-lpc.c`.

## Risks and Test Signals
Risks include packed bitfield portability in `chameleon_bdd`, endian mistakes for GDD fields, incorrect BAR count sizing, and format drift if newer Chameleon versions appear. Tests should parse known descriptor blobs, validate little-endian extraction on non-x86 architectures, and build both PCI and LPC carriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-lpc.c -->
# sources/distributed-fs/ceph-client/drivers/mcb/mcb-lpc.c

## Purpose
`mcb-lpc.c` implements an LPC/non-PCI carrier for MEN Chameleon Bus FPGAs on specific MEN systems discovered via DMI.

## Important APIs, Types, and Functions
Important elements are `struct priv`, `mcb_lpc_probe()`, `mcb_lpc_remove()`, `mcb_lpc_create_platform_device()`, fixed `sc24_fpga_resource` and `sc31_fpga_resource`, the `mcb_lpc_driver`, the DMI match table, and module init/exit.

## Control Flow, State, and Persistence
Module init checks DMI; a match callback allocates a platform device with a fixed memory resource. Probe requests and maps the resource, allocates an MCB bus, parses Chameleon cells, optionally shrinks the reserved mapping to the actual table size, and attaches discovered MCB devices. Remove releases the MCB bus, while devm handles IO mappings and memory regions. Persistent input is firmware/DMI identity plus FPGA descriptor memory; runtime state is `struct priv` and registered device-model objects.

## Dependencies and Integration Points
The file uses platform device APIs, DMI matching, IO memory mapping, `chameleon_parse_cells()`, and MCB namespace exports. It binds a synthetic `mcb-lpc` platform device only on supported MEN product versions.

## Risks and Test Signals
Risks include fixed physical resource assumptions, DMI table drift, resource remapping after table-size discovery, and exit unregistering a possibly unset platform device. Tests should cover matching and nonmatching DMI systems, parse failure cleanup, table sizes below and equal to `CHAM_HEADER_SIZE`, and module unload after failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-lpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-parse.c -->
# sources/distributed-fs/ceph-client/drivers/mcb/mcb-parse.c

## Purpose
`mcb-parse.c` parses MEN Chameleon FPGA descriptor tables and instantiates MCB devices from general device descriptors.

## Important APIs, Types, and Functions
Main routines are `get_next_dtype()`, `chameleon_parse_gdd()`, `chameleon_parse_bar()`, `chameleon_get_bar()`, and exported `chameleon_parse_cells()`. `chameleon_parse_bdd()` is present but currently a stub.

## Control Flow, State, and Persistence
Parsing copies the header from IO memory, validates Chameleon v2 magic, stores revision/model/minor/name into the MCB bus, obtains BAR descriptors either from the table or from the carrier map base, then iterates descriptor cells until `CHAMELEON_DTYPE_END`. General descriptors allocate `mcb_device`, decode ID/revision/variant/BAR/group/instance, skip unsupported/missing/IO-mapped BARs without failing the whole parse, fill IRQ and memory resources, and register devices. The return value is the parsed table size so carriers can remap the exact descriptor window. Persistent state is hardware descriptor memory; runtime state is allocated devices and resource ranges.

## Dependencies and Integration Points
It uses IO accessors, kernel allocation helpers, resource flags, exported MCB registration APIs, and `mcb-internal.h` layouts. PCI and LPC carriers both call `chameleon_parse_cells()`.

## Risks and Test Signals
Risks include unimplemented bridge descriptors, invalid descriptor loops without bounds beyond hardware data, endian handling, BAR count validation, leaking an allocated device if `mcb_device_register()` fails after initialization, and unsupported IO BARs. Tests should feed valid/invalid descriptor tables, zero-cell tables, bad magic, missing BARs, max BAR descriptors, and bridge descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-pci.c -->
# sources/distributed-fs/ceph-client/drivers/mcb/mcb-pci.c

## Purpose
`mcb-pci.c` implements the PCI carrier for MEN Chameleon Bus FPGA devices.

## Important APIs, Types, and Functions
Core elements are `struct priv`, `mcb_pci_get_irq()`, `mcb_pci_probe()`, `mcb_pci_remove()`, the PCI ID table for MEN and Altera vendor IDs with Chameleon device ID, and `mcb_pci_driver`.

## Control Flow, State, and Persistence
Probe enables the PCI device, sets bus mastering, rejects IO-mapped BAR0, maps an initial Chameleon header window, allocates an MCB bus, installs a carrier-specific IRQ callback that returns the PCI IRQ, parses Chameleon cells, optionally remaps to the exact table size, and attaches devices. Remove releases the bus and disables the PCI device. Runtime state is held in PCI drvdata and MCB bus/device structures. Persistent input is PCI configuration/resource state and FPGA descriptor memory.

## Dependencies and Integration Points
The file integrates PCI core probing, IO memory resource management, `chameleon_parse_cells()`, and MCB bus exports. It imports the `MCB` namespace.

## Risks and Test Signals
Risks include assuming descriptors live in BAR0, unsupported IO BARs, cleanup ordering after parse failures, and using one PCI IRQ for all child devices. Tests should cover probe failure at each step, table remapping, device remove with bound children, both vendor IDs, and PCI resource edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mcb/mcb-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/Kconfig

## Purpose
This Kconfig file defines the kernel configuration menu for Multiple Device RAID, bcache, and device-mapper targets under `drivers/md`.

## Important APIs, Types, and Functions
It declares `MD`, `BLK_DEV_MD`, bitmap options, RAID personalities, cluster support, `BCACHE` via a sourced sub-Kconfig, `BLK_DEV_DM`, and many DM targets including crypt, snapshot, thin, cache, verity, switch, integrity, zoned, audit, VDO, and pcache.

## Control Flow, State, and Persistence
There is no runtime flow. The file encodes dependency and select relationships that determine which modules compile and which helper libraries are pulled in. It gates the entire subtree under `MD` and sources nested Kconfigs for bcache, persistent-data, dm-vdo, and dm-pcache.

## Dependencies and Integration Points
It integrates with the block layer, crypto, DLM, RAID6, async RAID helpers, device-mapper libraries, IMA, integrity keyrings, and `drivers/md/Makefile`. User-visible help text documents expected modules and operational caveats.

## Risks and Test Signals
Risks include bad `select` relationships causing hidden dependency build failures, stale help text, and target configs drifting from Makefile object lists. Test signals are broad `randconfig`, `allmodconfig`, built-in versus modular MD/DM combinations, and configs with optional crypto/keyring/zoned/audit dependencies toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/Makefile

## Purpose
The Makefile composes software RAID, bcache, and device-mapper objects for Kbuild.

## Important APIs, Types, and Functions
It defines object groups for `dm-mod`, multipath path selectors, snapshots, mirrors, thin/cache metadata targets, `md-mod`, `raid456`, `linear`, and many individual DM targets. It also descends into `bcache/`, `persistent-data/`, `dm-vdo/`, and `dm-pcache/` based on config symbols.

## Control Flow, State, and Persistence
There is no runtime flow. Build ordering matters: RAID personalities are linked before `md.o` so personality init is available for MD auto-initialization. Conditional `dm-mod-objs` additions include init, uevent, zone, IMA, audit, and verity helper objects.

## Dependencies and Integration Points
This file is the Kbuild integration point for `drivers/md/Kconfig` symbols and module names. It ties MD, bcache, and DM code to block-layer kernel builds.

## Risks and Test Signals
Risks include link-order regressions, config/object mismatches, built-in-only helpers being omitted, and optional feature objects not following Kconfig dependencies. Tests should include `make drivers/md/` under representative configs, module installs, and `modpost` validation for enabled DM features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/Kconfig

## Purpose
This Kconfig file declares bcache configuration options.

## Important APIs, Types, and Functions
It defines `BCACHE`, `BCACHE_DEBUG`, and `BCACHE_ASYNC_REGISTRATION`. `BCACHE` selects `CRC64` and `CLOSURES` and optionally deprecated block holder support with sysfs.

## Control Flow, State, and Persistence
There is no runtime flow. The config controls whether bcache is built and whether debug checks or asynchronous sysfs registration behavior are included.

## Dependencies and Integration Points
It is sourced from `drivers/md/Kconfig` and paired with `drivers/md/bcache/Makefile`. Help text points users to the admin guide.

## Risks and Test Signals
Risks include missing selects for required libraries, debug-only code compile drift, and sysfs async registration behavior being enabled without tests. Test signals are builds with `BCACHE=m/y`, `BCACHE_DEBUG=y`, and `BCACHE_ASYNC_REGISTRATION=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/Makefile

## Purpose
The bcache Makefile builds the monolithic `bcache.o` module from its component objects.

## Important APIs, Types, and Functions
`bcache-y` includes allocation, bset, btree, debug, extents, IO, journal, moving GC, request, stats, superblock, sysfs, trace, util, writeback, and feature objects.

## Control Flow, State, and Persistence
There is no runtime flow. Object composition matters because many files share internal symbols and initialize global workqueues, sysfs types, and metadata handlers inside one module.

## Dependencies and Integration Points
It is controlled by `CONFIG_BCACHE` from Kconfig and integrates bcache into `drivers/md/Makefile` through `obj-$(CONFIG_BCACHE) += bcache/`.

## Risks and Test Signals
Risks include missing new objects from `bcache-y`, link failures from conditional debug code, and trace object dependencies. Test signals are `BCACHE=m` and `BCACHE=y` builds with debug and async registration toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/alloc.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/alloc.c

## Purpose
`alloc.c` implements bcache bucket allocation, invalidation, priority/generation handling, and sector allocation within open data buckets.

## Important APIs, Types, and Functions
Important functions are `bch_inc_gen()`, `bch_rescale_priorities()`, `bch_can_invalidate_bucket()`, `__bch_invalidate_one_bucket()`, `invalidate_buckets_lru()`, `invalidate_buckets_fifo()`, `invalidate_buckets_random()`, `bch_allocator_thread()`, `bch_bucket_alloc()`, `__bch_bucket_free()`, `bch_bucket_free()`, `__bch_bucket_alloc_set()`, `bch_bucket_alloc_set()`, `bch_alloc_sectors()`, `bch_open_buckets_alloc()`, `bch_open_buckets_free()`, and `bch_cache_allocator_start()`. `struct open_bucket` tracks active write buckets.

## Control Flow, State, and Persistence
The allocator thread runs under `bucket_lock`, drains `free_inc` into reserve freelists once prio/gen metadata is safe, invalidates reclaimable buckets according to LRU/FIFO/random policy, and writes priorities/generations with `bch_prio_write()` when cache sync requires it. Allocating a bucket pops from reserve lists, pins it, marks GC state, assigns priority, and updates availability stats. Sector allocation chooses or allocates open buckets, fills a `bkey` with pointer and extent size, advances pointer offsets, and retains bucket pins while data is pending insertion. Persistent correctness depends on writing incremented bucket generations before reuse, preventing stale on-disk btree pointers from becoming valid after crash.

## Dependencies and Integration Points
The file depends on `bcache.h`, `btree.h`, FIFO/heap utilities, kthreads, random selection, tracepoints, GC wakeups, priority writes, and bkey pointer helpers. It is called by btree, request, writeback, and moving-GC paths.

## Risks and Test Signals
Risks include generation wraparound, deadlock between allocation and GC/prio writes, reserve starvation, incorrect pin accounting, open-bucket locality races, and IO disable shutdown behavior. Tests should stress random writes, writeback and moving GC reserves, crash recovery around prio writes, allocator thread stop, `CACHE_SET_IO_DISABLE`, low-space GC, and debug duplicate-bucket checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bcache.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/bcache.h

## Purpose
`bcache.h` is the main internal bcache header. It documents core design and declares the in-memory objects, flags, helpers, and cross-file APIs for cache sets, cache devices, backing devices, allocation, btrees, IO, writeback, and sysfs.

## Important APIs, Types, and Functions
Important types include `bucket`, `keybuf`, `bcache_device`, `cached_dev`, `cache`, `gc_stat`, `cache_set`, `bbio`, and `detached_dev_io_private`. It defines GC mark bitfields, allocation reserves, cache-set state flags, bucket/sector conversion helpers, pointer validity helpers, checksum macro `csum_set()`, error macros, lifecycle helpers, and prototypes for allocator, btree, superblock, writeback, journal, request, debug, and cache-set registration functions.

## Control Flow, State, and Persistence
This header has no standalone runtime control flow, but it defines the shared state machines used by the module. `cache_set` coordinates device attachment, bucket allocation, btree cache, garbage collection, journal, UUIDs, writeback throttling, congestion, and shutdown flags. `cache` tracks on-disk superblock data, bucket arrays, priority buckets, free lists, and allocator thread state. `cached_dev` tracks independent backing-device lifetime, dirty/writeback state, rate control, and sequential IO detection. Persistence is represented by superblocks, UUID metadata, journal roots, bucket priorities/generations, and btree keys declared in included on-disk structures.

## Dependencies and Integration Points
It includes Linux block, closure, kobject, bio, mempool, list, locking, workqueue, and kthread APIs, plus bcache-specific `bcache_ondisk.h`, `bset.h`, `journal.h`, `stats.h`, and `util.h`. Every major bcache implementation file depends on this contract.

## Risks and Test Signals
Risks include flag semantics drifting across files, refcount and closure lifetime bugs, stale pointer generation comparisons, shutdown with IO in flight, and mismatch between in-memory structures and disk metadata expectations. Tests should include attach/detach, flash-only volumes, dirty writeback recovery, GC under pressure, btree cache shrink/cannibalization, sysfs tuning, and debug builds with expensive checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bcache_ondisk.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/bcache_ondisk.h

## Purpose
`bcache_ondisk.h` defines bcache's on-disk metadata format and key encoding. It is shared with userspace-visible layout expectations via the Linux syscall-note license.

## Important APIs, Types, and Functions
Key structures are `bkey`, `cache_sb_disk`, in-memory `cache_sb`, `jset`, `prio_set`, `bucket_disk`, `uuid_entry`, `bset`, and obsolete `uuid_entry_v0`. It defines bitfield helpers for key fields, pointer fields, superblock flags, cache modes, backing-device states, replacement policies, magic-number helpers `jset_magic()`, `pset_magic()`, `bset_magic()`, and bkey utility helpers such as `bkey_u64s()`, `bkey_bytes()`, `bkey_next()`, and `bkey_idx()`.

## Control Flow, State, and Persistence
There is no active control flow. The file encodes persistent metadata: sector-addressed btree keys with variable pointer counts, cache/backing superblocks at `SB_SECTOR`, journal entries containing replay keys and btree roots, priority/generation buckets for allocation safety, UUID table entries for backing devices and flash-only volumes, and bsets that form log-structured btree nodes. The in-memory `cache_sb` intentionally differs from `cache_sb_disk`, so conversion code elsewhere must be explicit.

## Dependencies and Integration Points
The header depends on Linux integer types and sector constants and is included by core bcache headers, superblock handling, journal, allocator, and btree code. Its constants define compatibility boundaries for formatted bcache devices.

## Risks and Test Signals
Risks include incompatible bitfield changes, endian conversion mistakes, checksum/magic mismatch, superblock version handling, generation wrap semantics, and copying variable-length bkeys without padding. Tests should include format compatibility, superblock read/write round trips, journal replay, priority set checksum validation, UUID table migration, and fuzzing malformed bkeys/bsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bcache_ondisk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bset.c -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/bset.c

## Purpose
`bset.c` implements operations on bcache bkeys and sorted bsets inside btree nodes: keylist management, extent trimming, auxiliary lookup-tree construction, insertion, search, iteration, sorting, and debug validation.

## Important APIs, Types, and Functions
Important routines include `bch_keylist_pop()`, `bch_keylist_pop_front()`, `bch_bkey_copy_single_ptr()`, `__bch_cut_front()`, `__bch_cut_back()`, `bch_btree_keys_alloc()`, `bch_btree_keys_free()`, `bch_bset_init_next()`, `bch_bset_build_written_tree()`, `bch_bset_fix_invalidated_key()`, `bch_bkey_try_merge()`, `bch_bset_insert()`, `bch_btree_insert_key()`, `__bch_bset_search()`, `bch_btree_iter_stack_init()`, `bch_btree_iter_next()`, `bch_btree_iter_next_filter()`, `bch_bset_sort_state_init()`, `bch_btree_sort_partial()`, `bch_btree_sort_lazy()`, `bch_btree_sort_into()`, and `bch_btree_keys_stats()`. Internal `bkey_float` nodes compress search keys for cacheline-indexed lookup trees.

## Control Flow, State, and Persistence
Written bsets get an auxiliary binary search tree indexed by one key per `BSET_CACHELINE`, using compressed mantissa/exponent values and fallback markers for ambiguous nodes. The active unwritten set uses a simpler lookup table that is updated on insert. Searches narrow to a cacheline range, then linearly scan variable-length keys. Btree iterators heap-merge multiple bsets in sorted order. Sorting merges sets into a compact output bset, optionally fixing overlapping extents and filtering invalid or stale keys depending on caller. State is held in `btree_keys`, `bset_tree`, auxiliary tree/prev arrays, and sort-state mempool pages; persistent output is the ordered bset key stream stored in btree-node memory and later written to disk.

## Dependencies and Integration Points
The file depends on `bset.h`, utility heap/mempool/time helpers, random sequence generation, prefetching, debug console output, and operation callbacks supplied by btree/extents code. It is central to btree lookup, insertion, compaction, GC, and journal replay.

## Risks and Test Signals
Risks include off-by-one errors in variable-length key walking, corrupt auxiliary tree indexes, bad extent trimming, merge logic hiding keys, mempool fallback bugs, stale-key filtering at the wrong time, and iterator heap corruption. Tests should include randomized bkey insert/search, overlapping extents, forced sort/partial sort, debug invariant checks, malformed bsets, memory allocation failure, and architecture coverage for bit arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bset.h -->
# sources/distributed-fs/ceph-client/drivers/md/bcache/bset.h

## Purpose
`bset.h` declares bcache bkey and bset infrastructure. It documents the bkey model, bset layout, btree iterators, auxiliary search trees, sorting interfaces, key manipulation helpers, and debug hooks.

## Important APIs, Types, and Functions
Important types are `bset_tree`, `btree_keys_ops`, `btree_keys`, `btree_iter`, `btree_iter_stack`, `bset_sort_state`, `bset_stats`, and `keylist`. It declares APIs for btree key allocation/init/free, bset initialization and tree building, insert/merge/sort, iterator setup and advancement, keylist realloc/pop, extent cutting, pointer validity callbacks, text formatting, and debug validation.

## Control Flow, State, and Persistence
The header defines how a btree node is represented as up to `MAX_BSETS` sorted sets, with the last set optionally unwritten and mutable. It specifies search behavior: written sets use compact auxiliary trees while the unwritten set uses a lookup table; iterators merge sets with heap ordering. It also defines bkey comparison, start/end extent helpers, keylist inline storage, and size/block macros used when writing bsets to disk. Persistent behavior is indirect: these declarations govern the bset layout and bkey ordering that become on-disk btree nodes.

## Dependencies and Integration Points
It includes `bcache_ondisk.h` and `util.h` and is consumed by btree, extents, journal replay, allocator-facing key creation, debug, and GC code. The `btree_keys_ops` callbacks allow extent-specific validation, merging, and sort fixups.

## Risks and Test Signals
Risks include callback contract violations, stack iterator overflow if bsets exceed assumptions, keylist reallocation errors, incorrect filtering between invalid and bad pointers, and mismatch between macros and on-disk bset sizes. Tests should cover callback implementations, maximum bset counts, stack and mempool iterators, keylist growth, bkey cut/merge helpers, and debug builds with expensive checks enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/bcache/bset.h -->
