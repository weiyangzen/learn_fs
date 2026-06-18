# subset-b-004593 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.c

Purpose: Implements the PA Semi PWRficient on-chip GMAC/XAUI Ethernet PCI netdev driver. It owns PCI probe/remove, DMA channel setup, NAPI, RX/TX descriptor processing, PHY link adjustment, MTU changes, interrupt handling, checksum assist rings, and MAC register programming.

Important APIs and flow: `pasemi_mac_probe()` enables the MAC PCI function, finds the separate DMA and I/O bridge PCI functions, maps the MAC to a DMA interface, reads the device-tree MAC address, installs `pasemi_netdev_ops`, and registers the netdev. `pasemi_mac_open()` allocates RX/TX DMA rings, optionally allocates checksum rings for jumbo MTUs, programs MAC/DMA registers, fills RX buffers, enables channels, attaches the PHY, enables NAPI, and requests RX/TX IRQs. The datapath is `pasemi_mac_start_tx()` for DMA mapping SKB fragments and ringing TX, `pasemi_mac_clean_tx()` for completion cleanup, and `pasemi_mac_clean_rx()` for status parsing, checksum marking, GRO delivery, stats, and RX refill. `pasemi_mac_close()` reverses this by stopping timers/NAPI/PHY, draining rings, pausing DMA engines, freeing IRQs, checksum rings, and RX/TX resources.

State and persistence: Runtime state is in `struct pasemi_mac` plus RX/TX/checksum ring objects with producer/consumer indexes, DMA descriptors, per-slot SKB/DMA metadata, interrupt names, PHY link state, and message mask. Hardware state persists in MAC config/RMON registers, DMA channel registers, event flags, and RX interface buffer rings until close/reset.

Dependencies and integration: Depends on PA Semi firmware/platform helpers (`pasemi_dma_*`, `pasemi_read/write_*`, IOB registers), PCI, Open Firmware MDIO/PHY binding, NAPI/GRO, DMA mapping, ethtool ops from `pasemi_mac_ethtool.c`, and PPC firmware feature checks for DMA translation bits.

Risks and test signals: Resource unwind is delicate across separate PCI devices, DMA channels, IRQs, NAPI, and checksum rings. `pasemi_mac_replenish_rx_ring()` reserves before checking allocation failure, and TX error cleanup must unmap both head and page fragments correctly. The remove path frees `mac->tx`/`mac->rx` channels even though close also frees resources, so device removal while the interface has not been opened or after unregister-close paths needs attention. Useful tests are probe/open/close/remove, IRQ storm and netpoll, jumbo MTU checksum offload, DMA mapping failures, PHY missing fallback, RX CRC/error descriptors, TX queue full/wake, and `CONFIG_PPC_PASEMI_IOMMU_DMA_FORCE` versus LPAR translation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.h

Purpose: Defines the PaSemi MAC driver's software state, ring sizing, ring access macros, MAC type identifiers, and MAC configuration register offsets/bitfields.

Important APIs/types/functions: `struct pasemi_mac_txring`, `struct pasemi_mac_rxring`, and `struct pasemi_mac_csring` wrap `struct pasemi_dmachan` with locks, ring indexes, descriptor metadata, timers, buffer rings, checksum event flags, and back-pointers. `struct pasemi_mac` is the private netdev state tying together PCI devices, NAPI, DMA interface, RX buffer size, checksum rings, PHY link values, IRQ names, and debug mask. Descriptor macros (`TX_DESC`, `RX_DESC`, `CS_DESC`, `*_INFO`, `RX_BUFF`) and `RING_USED`/`RING_AVAIL` provide the implementation's index arithmetic. Register constants cover `PCFG`, `MACCFG`, address registers, TX pause timing, RMON counters, and DMA interface channel mapping.

State and persistence: The header fixes RX/TX/checksum ring sizes as powers of two and encodes the hardware register ABI used by `pasemi_mac.c` and `pasemi_mac_ethtool.c`. The first-member `pasemi_dmachan` comments are part of the allocation contract with `pasemi_dma_alloc_chan()`.

Dependencies and integration: Includes netdev, ethtool, spinlock, and PHY definitions, and relies on PA Semi DMA descriptor/register definitions from platform headers included by C files.

Risks and test signals: Ring masks assume power-of-two sizes; changing sizes requires validating all descriptor increment units, hardware size programming, and RING math. Register bitfield macros are hardware ABI, so tests should include build coverage and runtime validation of MTU, link speed/duplex, RMON stats, and DMA descriptor wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac_ethtool.c

Purpose: Provides ethtool support for the PaSemi MAC driver: message level, link query, ring occupancy, hardware/RMON statistics, strings, and PHY-backed link settings.

Important APIs and flow: `pasemi_mac_ethtool_get_msglevel()` and `pasemi_mac_ethtool_set_msglevel()` expose `mac->msg_enable`. `pasemi_mac_ethtool_get_ringparam()` reports static max pending values and current `RING_USED()` counts scaled to hardware descriptor units. `pasemi_mac_get_sset_count()`, `pasemi_mac_get_strings()`, and `pasemi_mac_get_ethtool_stats()` publish 33 stats: DMA RX drops plus 32 MAC RMON counters. `pasemi_mac_ethtool_ops` wires these to ethtool and delegates link ksettings to phylib.

State and persistence: Reads live DMA/MAC registers and in-memory ring pointers; it does not persist settings except for the debug message mask.

Dependencies and integration: Depends on `pasemi_mac.h`, PA Semi DMA register helpers, netdev ethtool APIs, and an attached PHY for link setting get/set operations.

Risks and test signals: `get_ringparam()` assumes `mac->tx` and `mac->rx` exist, so ethtool ring queries before open can dereference null private ring pointers. Stats string count must stay aligned with RMON reads. Test with interface down/up, PHY absent fallback, RMON counter reset on open, and unsupported string sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Kconfig

Purpose: Adds the Pensando vendor menu and the `CONFIG_IONIC` option for the Pensando/AMD Ionic Ethernet driver.

Important APIs/types/functions: `NET_VENDOR_PENSANDO` gates the vendor submenu. `IONIC` is a tristate depending on `64BIT`, `PCI`, and optional PTP clock support; it selects `NET_DEVLINK`, `DIMLIB`, `PAGE_POOL`, and `AUXILIARY_BUS`.

Control flow: Kernel configuration first enables the vendor bucket, then offers the Ionic NIC driver. When built as a module, the module name is `ionic`.

State and dependencies: No runtime state. The Kconfig selections directly determine whether devlink, adaptive interrupt moderation, page-pool RX allocation, auxiliary RDMA device registration, and optional PTP code are available to the compiled driver.

Risks and test signals: Build matrix should cover built-in, module, and disabled `IONIC`, plus `CONFIG_PTP_1588_CLOCK` on/off. Dependency drift is important: removing `AUXILIARY_BUS`, `PAGE_POOL`, or `NET_DEVLINK` selections would break source files in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Makefile

Purpose: Connects the Pensando Ethernet vendor directory to the Ionic driver subdirectory.

Important APIs/types/functions: `obj-$(CONFIG_IONIC) += ionic/` causes Kbuild to descend into `pensando/ionic` when the driver is enabled.

Control flow: There is no runtime behavior; this is a build-routing file controlled entirely by `CONFIG_IONIC`.

State and dependencies: Depends on the Kconfig option from the sibling `Kconfig` and the `ionic/Makefile`.

Risks and test signals: Build tests should verify that `CONFIG_IONIC=m` produces the module from the subdirectory and that disabling `IONIC` skips it cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/Makefile

Purpose: Defines the object composition of the Ionic Ethernet driver.

Important APIs/types/functions: Builds `ionic.o` from bus, devlink, device, debugfs, LIF, RX filter, ethtool, TX/RX, stats, firmware, and auxiliary-bus objects. `ionic-$(CONFIG_PTP_1588_CLOCK) += ionic_phc.o` adds PHC/PTP support only when enabled.

Control flow: Kbuild links all listed objects into one built-in or module target selected by `CONFIG_IONIC`.

State and dependencies: Encodes module-level integration boundaries. Files in this subset depend on objects outside it (`ionic_main.o`, `ionic_lif.o`, `ionic_stats.o`, `ionic_txrx.o`, `ionic_phc.o`) for adminq waits, LIF lifecycle, statistics, datapath, and timestamping.

Risks and test signals: Missing an object here causes link failures or absent features. Test both PTP enabled and disabled builds, and module load/unload to verify init/exit references across objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic.h

Purpose: Provides top-level Ionic driver definitions, PCI IDs, timing constants, main device state, VF state, and cross-object function declarations.

Important APIs/types/functions: `struct ionic` holds PCI/device/devlink objects, `ionic_dev`, command mutex, debugfs root, BAR descriptions, identity data, workqueue, primary LIF, queue/interrupt sizing, interrupt bitmap, CPU affinity masks, doorbell watchdog work, notifier, VF operation lock, VF array, and watchdog timer. `struct ionic_vf` stores VF policy and DMA-backed stats. Declarations expose admin queue posting/waiting, device command waits, setup/identify/init/reset, port identify/init/reset, and `ionic_doorbell_wa()`.

State and persistence: This is the root in-memory state allocated through devlink private storage in `ionic_devlink_alloc()` and attached to the PCI device. It persists for the PCI probe lifetime and is shared by bus, devlink, LIF, ethtool, firmware, auxiliary, and debugfs code.

Dependencies and integration: Includes firmware ABI (`ionic_if.h`), device primitives (`ionic_dev.h`), and devlink declarations. PCI IDs cover Pensando Ionic Ethernet PF and VF devices.

Risks and test signals: Locking contracts are spread across users: `dev_cmd_lock` serializes device commands and `vf_op_lock` protects VF arrays. Tests should cover PF/VF probe, SR-IOV changes, firmware reset, doorbell workaround devices, devlink lifecycle, and module unload after workqueue/timer activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_api.h

Purpose: Declares the Ionic API surface shared with auxiliary clients, especially RDMA, and describes admin-command, interrupt, and CMB allocation contracts.

Important APIs/types/functions: `struct ionic_aux_dev` embeds an `auxiliary_device` and points back to the Ethernet LIF. `struct ionic_admin_ctx` carries a completion plus 64-byte admin command and 16-byte completion storage. `struct ionic_intr_info` records IRQ name, index/vector, rearm count, DIM coalescing value, affinity mask, and affinity notifier. Exported APIs include `ionic_adminq_post_wait()`, `ionic_error_to_errno()`, `ionic_request_rdma_reset()`, `ionic_intr_alloc/free()`, and `ionic_get_cmb()/ionic_put_cmb()`.

State and persistence: This header defines ownership boundaries for objects allocated in the Ethernet driver but used by auxiliary devices. CMB page reservations persist until explicitly returned by page id and order.

Dependencies and integration: Includes Linux auxiliary bus support plus Ionic firmware/register ABIs. `ionic_aux.c`, `ionic_dev.c`, and `ionic_lif.c` implement or export these symbols under namespace `NET_IONIC`.

Risks and test signals: API users must pair interrupt and CMB allocation/free calls and must not outlive the parent LIF/auxiliary device. Tests should cover RDMA-capable and non-RDMA devices, auxiliary unbind during reset, CMB exhaustion, interrupt affinity updates, and admin command timeout/error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.c

Purpose: Registers an auxiliary RDMA child device for RDMA-capable Ionic LIFs and exports an RDMA-triggered LIF reset command.

Important APIs and flow: `ionic_auxbus_register()` checks `IONIC_LIF_CAP_RDMA`, allocates `struct ionic_aux_dev`, assigns an ID from a global IDA, initializes an auxiliary device named `rdma`, parents it to the PCI device, and adds it to the auxiliary bus. `ionic_auxbus_unregister()` serializes with `lif->adev_lock`, deletes and uninitializes the child, and clears `lif->ionic_adev`. `ionic_auxbus_release()` frees the ID and wrapper memory. `ionic_request_rdma_reset()` sends `IONIC_CMD_RDMA_RESET_LIF` under `dev_cmd_lock` and is exported in namespace `NET_IONIC`.

State and persistence: The auxiliary device persists while the LIF is registered and RDMA capability is present. IDA state persists globally across devices until release callbacks run.

Dependencies and integration: Depends on the auxiliary bus, LIF state from `ionic_lif.h`, device command helpers from `ionic_dev.c`, and external RDMA drivers binding to the auxiliary device.

Risks and test signals: Lifetime depends on `auxiliary_device_uninit()` eventually invoking release; use-after-free risks center on RDMA clients during reset/remove. Test RDMA-capable probe/remove, repeated register/unregister, auxiliary add failure, ID reuse, reset requests while firmware is down, and lock ordering with `adev_lock` and `dev_cmd_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.h

Purpose: Declares auxiliary bus lifecycle hooks for Ionic LIFs.

Important APIs/types/functions: Exposes `ionic_auxbus_register(struct ionic_lif *lif)` and `ionic_auxbus_unregister(struct ionic_lif *lif)`.

Control flow: PCI/LIF setup calls register after netdev/devlink setup, and remove/reset paths call unregister before tearing down queues and LIF state.

State and dependencies: The header intentionally hides `struct ionic_aux_dev`; callers only pass the parent LIF. It depends on the LIF definition being available to C files including it.

Risks and test signals: Build coverage should verify callers compile with RDMA auxiliary support selected by Kconfig. Runtime tests should confirm unregister is idempotent when no RDMA capability created an auxiliary device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus.h

Purpose: Declares the Ionic bus abstraction used by common driver code to hide PCI-specific IRQ, doorbell, and driver registration details.

Important APIs/types/functions: Exposes IRQ lookup/allocation/free (`ionic_bus_get_irq()`, `ionic_bus_alloc_irq_vectors()`, `ionic_bus_free_irq_vectors()`), bus name lookup (`ionic_bus_info()`), module bus registration (`ionic_bus_register_driver()`, `ionic_bus_unregister_driver()`), and doorbell page map/unmap helpers.

State and persistence: No state is defined here; implementation state is stored in `struct ionic` and its PCI BAR table.

Dependencies and integration: Implemented by `ionic_bus_pci.c` and consumed by LIF, debugfs, ethtool, devlink, and main module code.

Risks and test signals: Common code assumes the PCI implementation has mapped BARs and allocated MSI-X vectors before use. Test vector allocation failures, doorbell page map/unmap for queue counts, and module register/unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus_pci.c

Purpose: Implements the Ionic PCI bus driver: device matching, BAR mapping, probe/remove, SR-IOV VF bookkeeping, PCI error/reset recovery, MSI-X vector helpers, and doorbell page mapping.

Important APIs and flow: `ionic_probe()` allocates devlink-private `struct ionic`, sets DMA masks, calls `ionic_setup_one()` for PCI enable/regions/BAR0 mapping/device identify/init/port init/CMB discovery, sizes and allocates the LIF, initializes existing VFs, registers devlink and netdev LIF, registers the RDMA auxiliary device, and starts watchdog/doorbell work. `ionic_remove()` shuts down timers/work, unregisters auxiliary/devlink/LIF, frees queues/IRQs, resets port/device, clears PCI mappings, and frees devlink storage. `ionic_sriov_configure()` enables/disables VFs and manages DMA-backed VF stats through `ionic_vf_alloc()` and `ionic_vf_dealloc()`. FLR/AER paths use `ionic_reset_prepare()` and `ionic_reset_done()` to tear down and rebuild PCI/LIF state.

State and persistence: Persists BAR metadata, mapped BAR0, VF arrays and VF stats DMA addresses, devlink private state, LIF state, IRQ vectors, CMB discovery data, and watchdog/doorbell scheduling over the probe lifetime.

Dependencies and integration: Integrates PCI core, MSI-X, devlink, debugfs, Ionic device commands, LIF lifecycle, auxiliary bus, SR-IOV, and PCI error handlers.

Risks and test signals: Probe unwind spans many subsystems and must match remove ordering. Reset paths assume `ionic->lif` is valid, so error recovery before LIF allocation is a sensitive case. VF stats DMA setup ignores older firmware command failures but must still unmap memory. Test probe failure injection at each stage, FLR while netdev is up, AER frozen channel, SR-IOV enable/disable during firmware reset, doorbell BAR mapping, and module unload after partial probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.c

Purpose: Creates debugfs inspection trees for Ionic devices, LIFs, queues, completions, interrupts, notify blocks, and RX filters when `CONFIG_DEBUG_FS` is enabled.

Important APIs and flow: `ionic_debugfs_create()` creates the global `ionic` directory; `ionic_debugfs_add_dev()` creates a per-PCI-device directory; `ionic_debugfs_add_ident()` and `ionic_debugfs_add_sizes()` expose identity and queue/interrupt sizing. `ionic_debugfs_add_lif()` adds LIF netdev and filter views. `ionic_debugfs_add_qcq()` builds per-queue directories with queue/CQ physical addresses, sizes, head/tail show files, descriptor blobs, SG blobs, interrupt register sets, and notify block status. Delete helpers remove device, LIF, and QCQ subtrees.

State and persistence: Stores debugfs dentries in `ionic->dentry`, `lif->dentry`, and `qcq->dentry`. Blob and regset wrappers are devm allocations tied to the device lifetime, while files point directly at live queue/CQ/register memory.

Dependencies and integration: Depends on debugfs, seq_file, PCI/netdev naming through `ionic_bus_info()`, LIF queue/filter structures, and register definitions. Called throughout PCI and LIF allocation/reconfiguration paths.

Risks and test signals: Debugfs files expose live structures without strong lifetime pinning beyond subtree removal, so teardown/reconfiguration ordering matters. `ionic_debugfs_add_qcq()` can return after partial creation on allocation failure. Test with debugfs enabled/disabled, queue reconfiguration, reset recovery, concurrent reads during remove, filter list locking, and descriptor blob sizes for SG and non-SG queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.h

Purpose: Declares Ionic debugfs lifecycle helpers and provides no-op stubs for non-debugfs builds.

Important APIs/types/functions: Public helpers cover global create/destroy, per-device add/delete, identity/sizes files, LIF add/delete, QCQ add/delete. Under `CONFIG_DEBUG_FS=n`, inline stubs preserve unconditional call sites.

State and dependencies: Includes `linux/debugfs.h` and references `struct ionic`, `struct ionic_lif`, and `struct ionic_qcq` through function prototypes.

Risks and test signals: Compile coverage must include debugfs enabled and disabled. Runtime tests should verify debugfs entries are recreated after reset and removed during queue/LIF/device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.c

Purpose: Implements low-level Ionic device operations: watchdog and firmware heartbeat checks, doorbell workaround scheduling, BAR0 register setup, CMB discovery/allocation, device command helpers, VF/port/LIF command builders, CQ servicing, and queue posting.

Important APIs and flow: `ionic_dev_setup()` validates BAR0 signature, maps device info/devcmd/interrupt registers, initializes dev info and watchdog workqueue, and records doorbell/CMB BARs. `ionic_map_cmb()` chooses discoverable or classic CMB mapping and initializes bitmap allocation state. `ionic_heartbeat_check()` samples firmware running/generation/heartbeat bits and enqueues LIF reset deferred work on up/down transitions. `ionic_dev_cmd_go()`, `ionic_dev_cmd_done/status/comp()`, and command-specific wrappers build firmware commands for device, port, VF, LIF, adminq, CMB discovery, and RDMA reset users. `ionic_get_cmb()` reserves bitmap regions, chooses regular or expanded-doorbell physical pages by stride, clears the memory with temporary WC mappings, and `ionic_put_cmb()` releases it. `ionic_cq_service()` advances completion color/tail and `ionic_q_post()` advances queue head and rings doorbells.

State and persistence: Owns firmware readiness state, watchdog timer/workqueue, BAR register pointers, doorbell page addresses, CMB bitmaps and physical regions, port info DMA pointers, queue/CQ indexes, and device info strings.

Dependencies and integration: Used by PCI probe/reset, LIF queue setup, adminq paths, ethtool settings, devlink firmware update, auxiliary RDMA reset, and TX/RX datapath doorbells.

Risks and test signals: Firmware reset transitions are asynchronous and depend on state bits in the LIF. CMB discovery has multiple firmware layout assumptions and bitmap allocation must be paired with release. Doorbell workaround work must stop before queue memory disappears. Test heartbeat stall/recovery, generation changes, devcmd timeout/null BAR handling, CMB classic/discovered/expanded regions, queue wraparound, completion color flips, and teardown while delayed work is queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.h

Purpose: Defines Ionic hardware-facing constants, compile-time ABI size checks, device/queue/CQ data structures, queue helper inlines, and low-level device API prototypes.

Important APIs/types/functions: Constants define descriptor limits, watchdog periods, doorbell deadlines, interrupt coalescing defaults, CMB expanded doorbell stride sizes, and XDP MTU bounds. Static asserts lock firmware ABI structure sizes. `struct ionic_dev` holds register pointers, firmware heartbeat state, doorbell/CMB resources, port info DMA memory, and device info strings. `struct ionic_queue` and `struct ionic_cq` describe software/hardware queue rings, SG rings, XDP/page-pool state, CMB mappings, doorbell values, indexes, and completion color. Inlines include `ionic_intr_init()`, `ionic_q_space_avail()`, and `ionic_q_has_space()`.

State and persistence: This header defines the persistent in-memory state manipulated by `ionic_dev.c`, LIF allocation, TX/RX, adminq, debugfs, and ethtool code.

Dependencies and integration: Includes atomic, mutex, workqueue, SKB/BPF trace headers, Ionic firmware ABI, registers, and exported API declarations.

Risks and test signals: ABI size asserts protect firmware command layouts; failures indicate incompatible `ionic_if.h` changes. Queue math assumes power-of-two descriptor counts and one empty slot. Test build with sparse/checker, max/min descriptor counts, XDP MTU boundaries, queue full/empty arithmetic, CMB queue mappings, and PTP disabled/enabled structure users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.c

Purpose: Provides the Ionic devlink instance, information reporting, firmware flashing entry point, and devlink port registration.

Important APIs and flow: `ionic_devlink_alloc()` allocates a devlink object with private `struct ionic` storage. `ionic_dl_info_get()` publishes running firmware version, fixed ASIC ID/revision, and serial number. `ionic_dl_flash_update()` delegates firmware data to `ionic_firmware_update()`. `ionic_devlink_register()` registers a physical devlink port, attaches it to the netdev with `SET_NETDEV_DEVLINK_PORT()`, and registers the devlink instance. `ionic_devlink_unregister()` reverses port and instance registration.

State and persistence: Devlink private storage owns the main `struct ionic` from PCI probe until remove. The devlink port is embedded in `struct ionic`.

Dependencies and integration: Integrates with PCI probe/remove, netdev LIF registration, devlink core, and firmware update implementation in `ionic_fw.c`.

Risks and test signals: Register ordering matters because the netdev uses the devlink port pointer. Firmware flash assumes `ionic->lif` and firmware command registers are valid. Test `devlink info`, port visibility, flash success/failure extack messages, probe unwind after devlink port registration failure, and unregister during device reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.h

Purpose: Declares Ionic devlink and firmware update entry points.

Important APIs/types/functions: Exposes `ionic_firmware_update()`, `ionic_devlink_alloc()`, `ionic_devlink_free()`, `ionic_devlink_register()`, and `ionic_devlink_unregister()`.

State and dependencies: Includes `<net/devlink.h>` and forward-relies on Ionic LIF/device definitions in including C files. The firmware update API accepts a kernel firmware object and netlink extack for user-visible errors.

Risks and test signals: Callers must register only after the LIF/netdev is allocated and unregister before freeing embedded devlink port state. Build and runtime tests should cover devlink disabled impossible by Kconfig selection, firmware flash with invalid device state, and probe error unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.c

Purpose: Implements Ionic ethtool operations for stats, driver/register info, link modes, pause/FEC, interrupt coalescing, ring and channel reconfiguration, RSS, tunables, module EEPROM pages, timestamp capability reporting, and autoneg restart.

Important APIs and flow: Stats are delegated to `ionic_stats_groups`. Link settings read DMA-updated `port_info` transceiver data and map Ionic XCVR IDs to ethtool link modes; setters issue port autoneg/speed commands under `dev_cmd_lock`. Pause and FEC setters validate firmware reset/autoneg constraints and issue port commands. Coalescing converts usecs to hardware units and updates live interrupt registers and DIM state. Ring/channel setters validate power-of-two descriptors, CMB capability/page requirements, XDP split-interrupt restrictions, then either store values while down or call `ionic_reconfigure_queues()` under `queue_lock`. RSS get/set exposes indirection table and Toeplitz key. Module EEPROM reads consistent snapshots from port-info SPROM pages. `ionic_get_ts_info()` reports PHC and hardware timestamp filters from firmware capabilities. `ionic_nway_reset()` flaps port admin state down/up.

State and persistence: Mutates LIF queue counts, descriptor counts, CMB TX/RX ring flags, coalescing values, DIM bits, RSS tables/keys, RX copybreak, and firmware port configuration. Many reads come from DMA-shared `lif->info` and `idev->port_info`.

Dependencies and integration: Depends on LIF queue reconfiguration, stats descriptors, device command wrappers, bus info, firmware identity, PTP/PHC state, SFP page definitions, and netdev ethtool core.

Risks and test signals: Most setters return `-EBUSY` during firmware reset but still rely on current LIF state consistency. CMB toggles require the device to be stopped, while descriptor count changes can reconfigure live queues. SPROM page offset handling assumes valid ethtool page requests. Test all setters during up/down and FW reset states, invalid ring/channel values, CMB insufficient pages, XDP plus split interrupts, FEC with autoneg enabled, unknown transceiver IDs, PTP absent/present, and module EEPROM page/bank validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.h

Purpose: Declares the single helper that attaches Ionic ethtool operations to a netdev.

Important APIs/types/functions: `ionic_ethtool_set_ops(struct net_device *netdev)` assigns the static `ionic_ethtool_ops` table in `ionic_ethtool.c`.

Control flow: LIF/netdev allocation calls this during netdev setup, before registration.

State and dependencies: No persistent state beyond the netdev's `ethtool_ops` pointer. Depends on netdev definitions through including files.

Risks and test signals: Build coverage should ensure the LIF code includes and calls this helper. Runtime `ethtool -i`, stats, rings, channels, RSS, and timestamp queries validate that the ops pointer was installed before netdev registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_fw.c

Purpose: Implements devlink-triggered Ionic firmware update: segmented firmware download, asynchronous install, slot activation, long status waits, and user-visible progress/error reporting.

Important APIs and flow: `ionic_firmware_update()` validates devcmd registers, copies the firmware image into the devcmd data window in chunks, issues `IONIC_CMD_FW_DOWNLOAD` for each offset, starts `IONIC_FW_INSTALL_ASYNC`, reads the returned slot, waits for `IONIC_FW_INSTALL_STATUS`, starts `IONIC_FW_ACTIVATE_ASYNC`, waits for `IONIC_FW_ACTIVATE_STATUS`, and reports final devlink flash status. `ionic_fw_status_long_wait()` polls firmware control status commands under `dev_cmd_lock`, allowing `-EAGAIN` or `-ETIMEDOUT` until the long timeout expires. Helper command builders wrap download/install/activate firmware devcmds.

State and persistence: Mutates firmware image storage on the device and selected firmware slot. In driver memory it uses only transient offsets, status, and devcmd completion data.

Dependencies and integration: Called from `ionic_dl_flash_update()` and depends on devlink notifications, firmware loader objects, netlink extack, LIF/netdev state, and serialized devcmd access from `ionic_dev.c`.

Risks and test signals: Install timeout is intentionally long for rare CPLD updates. Failures must surface useful extack messages and final flash status. The code assumes the device remains present and firmware command registers valid during the whole update. Test segmented download boundary sizes, devcmd timeout/error at each phase, invalid/null devcmd registers, device removal/reset during flash, progress notifications, and successful activation followed by reboot/reset requirements from firmware policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_fw.c -->
