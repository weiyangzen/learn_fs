# Research: subset-b-004445

Grouped research for Intel PRO/100 and PRO/1000 Ethernet driver files listed in work item `subset-b-004445`. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e100.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e100.c

Purpose: Linux PCI network driver for Intel 8255x/PRO/100 Fast Ethernet devices. It owns PCI probing, register mapping, EEPROM and PHY discovery, command/RX descriptor management, NAPI polling, ethtool operations, Wake-on-LAN, suspend/resume, shutdown, and PCI error recovery for the legacy `e100` netdev.

Important APIs, types, and data structures:

- Module and PCI integration: `e100_id_table`, `e100_driver`, `e100_init_module()`, `e100_cleanup_module()`, `e100_probe()`, and `e100_remove()` register a `pci_driver` named `e100` for many Intel 8255x IDs. `INTEL_8255X_ETHERNET_DEVICE()` encodes device IDs plus an ICH flag in `driver_data`.
- Netdev integration: `e100_netdev_ops` wires `.ndo_open`, `.ndo_stop`, `.ndo_start_xmit`, multicast mode, MAC address setting, MII ioctl, TX timeout, optional netpoll, and feature toggles. `e100_ethtool_ops` exposes link settings, register dumps, WoL, EEPROM, ring parameters, diagnostics, stats, physical ID LED control, and timestamp info.
- Hardware register model: `struct csr` maps SCB command/status, port reset/self-test register, EEPROM control, MDI control, and RX DMA count. Enums define SCB commands (`cuc_start`, `ruc_start`, `cuc_dump_reset`), interrupt acknowledgements, RU states, EEPROM opcodes, command block opcodes, and reset/self-test port commands.
- Descriptor and DMA state: `struct cb` is the transmit/control command block used for IA address setup, configuration, multicast list, firmware upload, dump, and TX. `struct rx` wraps receive frame descriptors backed by SKBs. `struct mem` is a coherent DMA area for self-test, stats, and dump buffer. `struct nic` is the private state container and holds rings, locks, MMIO, NAPI, timers, work item, EEPROM cache, firmware pointer, stats accumulators, PHY/MII state, and feature flags.
- EEPROM and PHY APIs: `e100_eeprom_read()`, `e100_eeprom_write()`, `e100_eeprom_load()`, and `e100_eeprom_save()` bit-bang the serial EEPROM and maintain a cached `nic->eeprom[]`. `mdio_ctrl_hw()`, `mdio_ctrl_phy_82552_v()`, and `mdio_ctrl_phy_mii_emulated()` back the MII library through `mdio_read()`/`mdio_write()`.
- Command engine: `e100_exec_cmd()` waits for the SCB command byte to clear and posts CU/RU commands. `e100_exec_cb()` allocates the next command block, invokes a preparation callback, links it into the circular hardware-visible chain, starts or resumes the CU, and handles queue pressure.
- RX/TX datapath: `e100_xmit_frame()` and `e100_xmit_prepare()` map SKB data into a TX command block. `e100_tx_clean()` reclaims completed CBs. `e100_rx_alloc_list()`, `e100_rx_alloc_skb()`, `e100_rx_clean()`, `e100_rx_indicate()`, and `e100_start_receiver()` maintain the receive frame area and feed packets to the stack through `netif_receive_skb()`.

Control flow:

- Probe flow: `e100_probe()` allocates an Ethernet netdev, sets RXFCS/RXALL hardware features, installs netdev/ethtool ops, initializes NAPI and private state, enables the PCI device, requests BARs, enforces 32-bit DMA, maps CSR registers with `pci_iomap()`, derives MAC generation/ICH defaults, initializes locks, resets the device before bus mastering, creates the watchdog timer and TX-timeout work item, allocates the coherent `struct mem`, loads the EEPROM, initializes the PHY, installs the MAC address from EEPROM, derives initial WoL from EEPROM, registers the netdev, and creates a DMA pool for command blocks.
- Open/up flow: `e100_open()` turns carrier off and calls `e100_up()`. `e100_up()` allocates the RX list and CB pool, performs `e100_hw_init()`, programs multicast/configuration, starts the receiver, arms the watchdog, requests the shared IRQ, wakes the queue, enables NAPI, then unmasks interrupts. Error paths unwind CBs and RX buffers.
- Hardware initialization: `e100_hw_init()` performs selective and software reset, runs the DMA self-test, initializes PHY quirks, loads CU/RU base addresses, optionally loads microcode, issues configuration and IA-address command blocks, points the CU dump engine at coherent stats memory, starts dump-reset accounting, and leaves interrupts disabled until open completes.
- Firmware flow: `e100_request_firmware()` selects `e100/d101m_ucode.bin`, `e100/d101s_ucode.bin`, or required `e100/d102e_ucode.bin` based on MAC type, validates exact firmware size and embedded patch offsets, and caches the `struct firmware *`. `e100_setup_ucode()` copies the little-endian microcode into a CB and patches CPUSaver parameters before `e100_load_ucode_wait()` waits for completion.
- TX flow: `ndo_start_xmit` optionally applies the ICH 10 Mbps half-duplex NOP workaround, calls `e100_exec_cb()` with `e100_xmit_prepare()`, stops the queue on `-ENOSPC` or `-ENOMEM`, and returns `NETDEV_TX_OK` or `NETDEV_TX_BUSY`. Completion is not interrupt-per-packet; `e100_tx_clean()` runs from NAPI/netpoll and frees SKBs, unmaps DMA, updates stats, restores CB availability, and wakes a stopped queue.
- RX flow: the driver keeps a circular RFA of SKB-backed RFDs. It deliberately sets the EL bit and size zero on the before-last buffer so hardware stops safely before the software updates links. `e100_rx_indicate()` syncs descriptor headers, checks complete/OK bits and RU no-resource state, unmaps the completed buffer, adjusts length and optional FCS handling, rejects errored or oversized frames unless RXALL is active, updates stats, and passes good SKBs upward. `e100_rx_clean()` then refills empty slots and restarts the RU if it had suspended.
- Interrupt/NAPI flow: `e100_intr()` reads/acks SCB interrupt bits, marks `ru_running` suspended on RNR, disables IRQs, and schedules NAPI. `e100_poll()` cleans RX and TX, keeps polling if the budget was consumed, otherwise completes NAPI and reenables interrupts. Netpoll follows the same disable/interrupt/clean/enable structure.
- Watchdog flow: `e100_watchdog()` periodically reads MII settings, logs carrier transitions, generates a software interrupt to recover from RX allocation failures, updates hardware stats, adjusts adaptive inter-frame spacing on collision-prone half-duplex links, reissues multicast setup for old 82557 lockup mitigation, toggles the ICH 10 Mbps half-duplex workaround, and rearms itself.
- Down/timeout flow: `e100_down()` disables NAPI, stops the queue, resets hardware, frees IRQ, deletes the watchdog, drops carrier, and frees CB/RX lists. `e100_tx_timeout()` schedules `e100_tx_timeout_task()`, which serializes under RTNL and restarts the interface if running.
- Ettool flow: link settings delegate to the MII library but reconfigure hardware after changes. Register dumps combine SCB state, PHY registers in ABI-specific reverse order, and a CU dump buffer. EEPROM get/set use the cached EEPROM image and write back with checksum recalculation. Offline diagnostics run EEPROM, self-test, MAC loopback, and PHY loopback after taking the device down and restoring link settings.
- Power/error flow: suspend/shutdown detach the netdev, take it down if running, enable reverse auto-negotiation for 82552 when WoL/ASF is needed, and power off or prepare sleep. Resume reenables PCI, restores bus mastering, clears reverse auto-negotiation, brings the netdev back up if needed, and attaches it. PCI error recovery detaches/down/disables, requests slot reset, reinitializes hardware on function zero, and reopens on resume.

State and persistence behavior:

- Persistent hardware state is primarily EEPROM: station address, WoL capability bit, ASF/GCL/SMBus metadata, PHY interface hints, and checksum. The driver caches up to 256 EEPROM words and permits ethtool writes only with `E100_EEPROM_MAGIC`.
- Runtime state is in `struct nic`, SKBs, DMA mappings, MMIO registers, the coherent `struct mem`, and firmware pointer `nic->fw`. Ring sizes live in `nic->params` and can change via ethtool ringparam but are not persisted beyond driver lifetime.
- Statistics are split between netdev software counters, hardware dump-reset counters in coherent memory, and driver accumulators for flow-control/TCO/short/overlength counters. `e100_update_stats()` consumes hardware dump data from the previous dump command and starts the next dump-reset.
- WoL state is represented in `nic->flags & wol_magic` and mirrored into device wakeup enablement; it is initialized from EEPROM but ethtool changes are runtime device state, not EEPROM writes.
- Firmware is requested lazily and cached so resume/hibernate reinitialization does not call `request_firmware()` again.

Dependencies and integration points:

- Kernel subsystems: PCI core, DMA mapping and DMA pools, NAPI/netdev, MII library, ethtool, firmware loader, timers/workqueues, RTNL, PM sleep ops, PCI AER/error recovery, and optional netpoll.
- Hardware contracts: Intel 8255x SCB/CU/RU command model, serial EEPROM timing, MDI register protocol, hardware stats dump format, and MAC/PHY generation quirks. The driver is restricted to 32-bit DMA.
- The file is self-contained for `e100`; it does not depend on a separate local header. Firmware blobs under `e100/` must be available for required D102E hardware and optional CPUSaver support on supported MACs.

Risks and maintenance concerns:

- Command-block ordering is subtle. `e100_exec_cb()` relies on the current CB S-bit being set before clearing the previous S-bit plus a DMA write barrier; changing this can race hardware consumption of the command list.
- RX RFA maintenance is fragile. The before-last EL/size-zero protocol, DMA sync ordering, and RU state transitions are designed to avoid hardware touching descriptors while software relinks them.
- EEPROM writes can permanently alter device configuration. The set path updates the cached image and checksum, but offset/length odd-byte handling is coarse because it converts byte offsets to word ranges with `(len >> 1) + 1`.
- Some paths busy-wait or sleep for hardware completion, including SCB command acceptance, EEPROM bit-banging, firmware load, register dump, self-test, loopback tests, and link tests. These are acceptable in control paths but risky if moved into atomic contexts.
- `e100_loopback_test()` compares received data against the original SKB after `e100_xmit_frame()` handed ownership to TX cleanup logic; the path currently avoids normal TX cleanup until after the compare, but ownership assumptions are tight.
- `e100_set_features()` mutates `netdev->features` directly and returns `1` after reconfiguring, which is an older driver style and should be treated carefully if ported to newer feature negotiation expectations.
- The module parameter `eeprom_bad_csum_allow` permits operation with bad EEPROM checksum and potentially invalid MAC address; this is useful for recovery but a production risk.
- MII-less PHY emulation is deliberately limited and comments call several variants untested.

Test signals:

- Build coverage with `CONFIG_E100=m/y`, firmware declarations, PM, netpoll, and PCI error recovery enabled where possible.
- Probe/remove on supported 82557/82558/82559/82550/82551/ICH variants; confirm BAR selection with and without `use_io`, 32-bit DMA mask, valid EEPROM checksum, MAC assignment, and firmware loading behavior.
- Interface lifecycle: repeated `ip link set up/down`, module unload while closed/open, TX timeout injection, and error-path unwinds for IRQ, DMA pool, RX list, CB pool, firmware, and EEPROM failures.
- Datapath: sustained TX/RX, queue stop/wake under TX ring pressure, RX allocation failures followed by watchdog software interrupt recovery, VLAN-sized frames, RXFCS and RXALL toggles, multicast/promiscuous/allmulti changes, and NAPI budget exhaustion.
- Ettool: `ethtool -i`, `-d`, `-e/-E` with correct magic, `-g/-G`, `-s`, `--test online/offline`, `--identify`, `-S`, WoL get/set, and MII ioctl compatibility.
- Power/error: suspend/resume with WoL on/off, shutdown poweroff wake behavior, ASF-enabled devices, and simulated PCI error recovery through detected/slot_reset/resume callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/Makefile

Purpose: kbuild object list for the legacy Intel PRO/1000 `e1000` driver.

Important APIs, types, and functions: this file has no C APIs. It declares `obj-$(CONFIG_E1000) += e1000.o` and composes `e1000.o` from `e1000_main.o`, `e1000_hw.o`, `e1000_ethtool.o`, and `e1000_param.o`.

Control flow: build-time only. When `CONFIG_E1000` is enabled as built-in or module, kbuild descends into this directory and links the four listed objects into one driver object. `e1000_ethtool.o` is always part of the driver, so ethtool support is not optional within this Makefile.

State and persistence behavior: no runtime state and no persistent data. The file only affects generated build artifacts.

Dependencies and integration points: depends on the kernel Kconfig symbol `CONFIG_E1000`, normally selected from the Intel Ethernet Kconfig menu. It assumes the companion source files in the same directory provide the main PCI/netdev driver, hardware helper layer, ethtool hooks, and module parameter processing.

Risks: a missing object in `e1000-y` would compile out an essential part of the driver. Renaming files or splitting optional features requires this object list to remain synchronized with exported symbols such as `e1000_set_ethtool_ops()` from `e1000_ethtool.c` and core routines declared in `e1000.h`.

Test signals: build with `CONFIG_E1000=m` and `CONFIG_E1000=y`; verify `e1000.o` links all four objects, module load succeeds, and no unresolved symbols appear from ethtool, hardware, or parameter code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000.h

Purpose: main private header for the legacy Intel PRO/1000 `e1000` driver. It centralizes kernel includes, build constants, descriptor/ring data structures, the adapter private state layout, state bits, logging helpers, and cross-file function prototypes shared by `e1000_main.c`, `e1000_hw.c`, `e1000_ethtool.c`, and `e1000_param.c`.

Important APIs, types, and definitions:

- Build/device helpers: `BAR_0`, `BAR_1`, `INTEL_E1000_ETHERNET_DEVICE()`, `E1000_MAX_INTR`, and reset polling constant `E1000_CHECK_RESET_COUNT`.
- Descriptor sizing: default/min/max TX and RX descriptor counts (`E1000_DEFAULT_TXD`, `E1000_MAX_TXD`, `E1000_MIN_TXD`, `E1000_MAX_82544_TXD`, and RX equivalents), interrupt throttle bounds (`E1000_MIN_ITR_USECS`, `E1000_MAX_ITR_USECS`), RX buffer sizes from 128 to 16384, flow-control thresholds, queue wake threshold, and RX buffer write batching.
- EEPROM/management constants: `E1000_EEPROM_82544_APM`, `E1000_EEPROM_APME`, `E1000_MNG_VLAN_NONE`, SmartSpeed bounds, packet buffer shifts, and default master/slave setting.
- Buffer wrappers: `struct e1000_tx_buffer` stores SKB pointer, DMA address, timestamp, byte length, watch descriptor index, mapping kind, segment count, and bytecount. `struct e1000_rx_buffer` stores either a page or fragment pointer plus DMA address.
- Ring types: `struct e1000_tx_ring` and `struct e1000_rx_ring` hold coherent descriptor memory, DMA address, size/count, producer/consumer indices, buffer-info arrays, hardware head/tail register offsets, plus TX TSO tracking or RX top SKB/CPU. Descriptor access macros include `E1000_DESC_UNUSED()`, `E1000_RX_DESC_EXT()`, `E1000_RX_DESC()`, `E1000_TX_DESC()`, and `E1000_CONTEXT_DESC()`.
- Adapter state: `struct e1000_adapter` is the driver-private netdev state. It contains VLAN and management state, WoL, SmartSpeed, link speed/duplex, stats lock, aggregate packet/byte counters, interrupt throttle settings, flow-control autoneg, TX/RX rings and queue counts, NAPI, checksum counters, hardware stats (`struct e1000_hw_stats`), PHY info/stats, offline test rings, log level, feature flags such as TSO force, Smart Power Down, quad-port role, resource bookkeeping, reset/watchdog/fifo/phy work items, and PCI/netdev pointers.
- State bits: `enum e1000_state_t` defines `__E1000_TESTING`, `__E1000_RESETTING`, `__E1000_DOWN`, and `__E1000_DISABLED` for `adapter->flags`.
- Logging and cross-file APIs: `e_dbg`, `e_err`, `e_info`, `e_warn`, `e_notice`, and device logging wrappers standardize messages. External prototypes include lifecycle (`e1000_open()`, `e1000_close()`, `e1000_up()`, `e1000_down()`), reset/reinit, link speed/duplex setting, resource allocation/free, stats update, link detection, PHY power-up, ethtool op installation, option checking, and `e1000_get_hw_dev()`.

Control flow: the header itself has no executable control flow, but it defines the shared control contract. Core driver code allocates and initializes `struct e1000_adapter`, programs ring counts, allocates descriptor resources using the ring structs, and then the ethtool layer reads or mutates those same fields under state bits such as `__E1000_RESETTING` and `__E1000_TESTING`. The descriptor macros are used directly by datapath and offline loopback-test code to translate ring indices into hardware descriptors.

State and persistence behavior:

- Runtime state is concentrated in `struct e1000_adapter`; this includes hardware configuration mirrors (`struct e1000_hw`), software-maintained counters, work items, rings, and feature flags.
- Rings contain both coherent descriptor memory and per-buffer DMA mappings, so ownership and cleanup are split between the ring descriptors and the `buffer_info` arrays.
- EEPROM and hardware NVM state are not stored directly here, but `adapter->eeprom_wol`, `adapter->wol`, and `hw.eeprom` fields expose persistent hardware configuration to the rest of the driver.
- No disk persistence is introduced by this header. Persistence exists only through hardware EEPROM writes performed by implementation files.

Dependencies and integration points:

- Includes a broad Linux kernel surface: PCI, netdevice, etherdevice, SKB, DMA mapping, timers, interrupts, MII, ethtool, VLAN, TCP/IP headers, checksum, reboot, and scheduler queue headers.
- Includes `e1000_hw.h`, which provides hardware register constants, descriptor definitions, EEPROM/PHY/MAC types, and low-level hardware helpers used by the declared functions.
- The header is the ABI between the driver translation units. Changes to `struct e1000_adapter`, ring structs, or prototypes must be synchronized across `e1000_main.c`, `e1000_ethtool.c`, `e1000_param.c`, and hardware code.

Risks and maintenance concerns:

- `struct e1000_adapter` is large and shared widely; adding or reordering fields can perturb cache locality and can break code that relies on fields for stats offsets in `e1000_ethtool.c`.
- `E1000_DESC_UNUSED()` uses `smp_load_acquire()` and `READ_ONCE()` around producer/consumer indices. Simplifying it would risk queue accounting races between datapath and cleanup.
- Ring count constants differ for pre-82544 versus 82544+ hardware. Ettool ring changes and resource setup must preserve those device-specific limits and descriptor alignment requirements.
- The header exposes many mutable hardware mirrors without encapsulation, so callers must use the correct locking/reset state conventions from implementation files.
- The logging macros assume local variables named `adapter` or `hw` in callers; moving them to contexts without those names will fail or log through the wrong object.

Test signals:

- Compile all four `e1000` objects after any header change, with warnings enabled, because stats offsets and prototypes are consumed across files.
- Exercise descriptor ring setup/teardown, TX/RX datapath, NAPI, ethtool stats, ringparam changes, reset/reinit paths, and offline loopback tests.
- Validate multiple MAC generations, especially descriptor limits for pre-82544 versus 82544+ devices, and confirm `E1000_DESC_UNUSED()` behavior under queue wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_ethtool.c

Purpose: ethtool support and offline diagnostics for the legacy Intel PRO/1000 `e1000` driver. It translates kernel ethtool requests into driver/hardware state changes for link settings, flow control, register and EEPROM access, ring sizing, self-tests, Wake-on-LAN, LED identification, interrupt coalescing, and statistics.

Important APIs, types, and functions:

- Stats metadata: `struct e1000_stats`, `E1000_STAT()`, `E1000_NETDEV_STAT()`, and `e1000_gstrings_stats[]` map ethtool statistic names to offsets in either `struct e1000_adapter` or `struct net_device`. `e1000_get_ethtool_stats()` uses the metadata to copy 32-bit or 64-bit values into the ethtool buffer after `e1000_update_stats()`.
- Link settings: `e1000_get_link_ksettings()` reports supported/advertised modes, copper/fiber port type, current speed/duplex, autoneg, and MDI/MDI-X state. `e1000_set_link_ksettings()` validates MDI-X rules, serializes through `__E1000_RESETTING`, updates autoneg advertisement or forced speed/duplex through `e1000_set_spd_dplx()`, updates `hw->mdix`, and resets or restarts the device.
- Link and pause: `e1000_get_link()` forces a fresh hardware link check when carrier is down. `e1000_get_pauseparam()` and `e1000_set_pauseparam()` expose and update RX/TX pause and flow-control autoneg, then either restart the adapter or call `e1000_setup_link()`/`e1000_force_mac_fc()`.
- Register dump: `e1000_get_regs_len()` returns 32 registers. `e1000_get_regs()` fills MAC registers, descriptor pointers, interrupt timers, PHY type and PHY-specific diagnostic registers for IGP or M88 PHYs, idle/receive errors, 1000T status, and management control on newer copper MACs.
- EEPROM access: `e1000_get_eeprom_len()`, `e1000_get_eeprom()`, and `e1000_set_eeprom()` expose hardware EEPROM with vendor/device magic validation, odd-byte read-modify-write preservation, endianness conversion, SPI multiword reads where supported, and checksum update when the modified range includes the checksum region.
- Ring parameters: `e1000_get_ringparam()` reports per-MAC descriptor limits and active ring counts. `e1000_set_ringparam()` clamps and aligns requested counts, serializes through `__E1000_RESETTING`, optionally takes the device down, allocates replacement ring structs, sets up new resources before freeing old ones, then restarts the adapter or restores old rings on failure.
- Offline tests: `e1000_reg_test()`, `e1000_eeprom_test()`, `e1000_intr_test()`, `e1000_loopback_test()`, and `e1000_link_test()` provide ethtool self-test data. Helpers allocate temporary descriptor rings, build/check loopback frames, configure PHY/MAC loopback for different MAC/PHY generations, and clean up afterward.
- WoL/LED/coalesce: `e1000_wol_exclusion()`, `e1000_get_wol()`, and `e1000_set_wol()` enforce device/port-specific wake capabilities. `e1000_set_phys_id()` drives hardware LEDs for ethtool identify. `e1000_get_coalesce()` and `e1000_set_coalesce()` expose RX interrupt throttle on 82545+ hardware.
- Registration: `e1000_ethtool_ops` holds all implemented operations, and `e1000_set_ethtool_ops()` installs it on the netdev.

Control flow:

- Ettool operations generally begin by obtaining `struct e1000_adapter *adapter = netdev_priv(netdev)` and then operate on `adapter->hw`, `adapter->tx_ring`, `adapter->rx_ring`, and adapter flags.
- Link-setting changes serialize against resets by spinning on `test_and_set_bit(__E1000_RESETTING, &adapter->flags)`. If the netdev is running, they call `e1000_down()` and `e1000_up()` to apply changes; otherwise they call `e1000_reset()`. The reset bit is cleared on all normal error paths.
- Ring resizing takes the same reset bit, optionally downs the running adapter, allocates new TX/RX ring arrays, swaps them into the adapter, sets counts for all queues, pre-allocates resources if running, swaps back to free old resources, restores the new rings, and calls `e1000_up()`. Allocation/setup failures restore old ring pointers, free partial allocations, restart the old adapter if needed, and clear the reset bit.
- Offline diagnostics set `__E1000_TESTING`. Offline mode saves autoneg/speed/duplex state, performs link test before reset, closes a running interface or resets a stopped one, runs register/EEPROM/interrupt/loopback tests with resets between them, restores link configuration, resets, clears testing, and reopens if it was originally running. Online mode only runs link test and marks other tests passed by default.
- Interrupt test temporarily requests the device IRQ with a test handler, masks all interrupts, forces individual cause bits through `ICS`, observes `adapter->test_icr`, distinguishes shared versus unshared IRQ behavior, disables interrupts, and frees the IRQ.
- Loopback test builds temporary TX/RX rings directly in hardware registers, configures PHY or transceiver loopback based on media/MAC generation, sends 64 frames per loop iteration by moving TDT, polls RX buffers for signature bytes, then clears loopback and frees all temporary DMA mappings.
- EEPROM get/set compute first and last EEPROM word from byte offset/length. Reads allocate just the requested word span; writes allocate a full EEPROM-sized buffer, preserve partial edge words when offsets are odd, convert endianness before and after byte copy, write the word span, and update the EEPROM checksum when needed.

State and persistence behavior:

- Link, pause, MDI-X, interrupt throttle, ring counts, WoL, and autoneg settings are runtime adapter/hardware state. Some of these mirror persistent defaults from EEPROM but this file usually does not persist them unless the explicit EEPROM write operation is used.
- EEPROM writes are persistent hardware modifications and are guarded by an ethtool magic value `vendor_id | device_id << 16`. Checksum is updated for changes affecting the checksum-covered range.
- Offline testing temporarily mutates hardware registers, descriptor registers, PHY loopback bits, IRQ handlers, and adapter state bits. It saves and restores autoneg advertisement, forced speed/duplex, and autoneg boolean around the destructive portion.
- Statistics are read from live adapter/netdev memory through offset metadata. This couples ethtool stat layout tightly to `struct e1000_adapter` and `struct net_device` field sizes.
- WoL settings update `adapter->wol` and device wakeup enablement. Port and device exclusions prevent advertising unsupported wake modes.

Dependencies and integration points:

- Depends on `e1000.h` for adapter/ring definitions, state bits, register macros (`er32`, `ew32`, `E1000_WRITE_FLUSH()`), constants, logging, and core function prototypes.
- Depends on low-level hardware helpers from `e1000_hw.c`/`e1000_hw.h`, including EEPROM read/write/checksum, PHY register access, PHY reset, link setup, flow-control forcing, LED control, speed/duplex discovery, and link checking.
- Integrates with the kernel ethtool API through `struct ethtool_ops`, `ethtool_link_ksettings`, `ethtool_eeprom`, `ethtool_ringparam`, `ethtool_test`, `ethtool_wolinfo`, `ethtool_pauseparam`, and coalesce structures.
- Uses PCI/DMA APIs for offline descriptor rings and IRQ APIs for interrupt testing. Uses SKB allocation for loopback frames and raw allocated RX buffers for test receives.

Risks and maintenance concerns:

- Offline tests are intentionally invasive: register tests write many MAC registers, interrupt tests replace the IRQ handler, and loopback tests reprogram descriptor registers. They must only run while the adapter is isolated by `__E1000_TESTING` and, for offline mode, after closing or resetting the normal datapath.
- `e1000_set_link_ksettings()` and `e1000_set_pauseparam()` spin-sleep on `__E1000_RESETTING`. Any new caller that holds locks needed by reset/down/up could deadlock.
- Ring resize swaps adapter ring pointers several times to free old resources after new resources are created. Error paths must preserve pointer ownership exactly or risk leaking DMA memory or freeing active rings.
- Stats extraction uses raw offsets and assumes field sizes are either `u32` or `u64`. Any structure field type change in `e1000_adapter` can silently break ethtool stats unless `e1000_gstrings_stats[]` is updated.
- EEPROM writes allocate `max_len` bytes but only initialize edge words and copied bytes before writing the requested word span; the targeted span is covered, but changes to this logic must preserve odd offset behavior and checksum handling.
- The loopback receive wait condition is timing-sensitive and uses DMA syncs plus signature-byte checks. Slow hardware, virtualization, or unusual descriptor counts can expose timeout or false-failure behavior.
- WoL support has several device/port exclusions, including quad/dual-port function restrictions. Adding device IDs requires validating wake capabilities per port, not just per MAC family.
- Coalesce conversion treats values `0..4` specially and rejects `2`; callers and documentation must match this legacy ITR encoding.

Test signals:

- Build and link as part of `e1000.o` with `CONFIG_E1000=m/y`.
- Ettool coverage: `ethtool -i`, `-k`, `-S`, `-d`, `-e`, EEPROM write with valid/invalid magic, `-g/-G`, `-a/-A`, `-c/-C`, `-p`, `-s`, `--show-eee` absence expectations, `--test online`, and `--test offline`.
- Link setting matrix: copper versus fiber, autoneg on/off, forced 10/100/1000 where supported, MDI/MDI-X auto/manual validation, and carrier-down fresh link checks.
- Ring resize under traffic and while stopped, including allocation-failure injection and descriptor count alignment on pre-82544 versus newer MACs.
- Offline diagnostics on representative 82542/82543/82544/82545/82546/82540/82541/82547 devices or emulations where available, with attention to PHY loopback variants and shared IRQ behavior.
- WoL get/set on unsupported devices, dual/quad-port function B exclusions, KSP3 unicast exclusion, and `device_can_wakeup()` false cases.
- Interrupt throttle programming on 82545+ and rejection on older MACs or invalid usec values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_ethtool.c -->
