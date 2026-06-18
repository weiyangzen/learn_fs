# subset-b-004333 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne.c

Purpose: this is the legacy ISA/ISAPnP NE1000/NE2000 programmed-I/O driver for NS8390-compatible Ethernet boards. It probes user-supplied ISA I/O ports, ISAPnP clones, and optionally a small boot-time ISA port list, then wires the device into the shared 8390 core through `alloc_eip_netdev()`, `eip_netdev_ops`, `eip_interrupt`, and `NS8390p_init()`. It also supports old clone exceptions through `bad_clone_list` and the `bad=0xbad` module escape hatch.

Important APIs, types, and functions: module parameters `io[]`, `irq[]`, `bad[]`, and `msg_enable` are the external configuration surface. `do_ne_probe()` selects explicit, ISAPnP, or auto-probe discovery. `ne_probe_isapnp()` attaches and activates matching PnP devices, copies their port/IRQ into the netdev, and stores the `struct pnp_dev` in `ei_status.priv`. `ne_probe1()` owns hardware validation, reset acknowledgement, SAPROM reads, signature/clone detection, IRQ probing, interrupt reservation, `ei_status` setup, and `register_netdev()`. Runtime data movement is supplied by `ne_reset_8390()`, `ne_get_8390_hdr()`, `ne_block_input()`, and `ne_block_output()`. Platform integration uses `ne_drv_probe()`, `ne_drv_remove()`, suspend/resume hooks, synthetic module-time `platform_device`s in `pdev_ne[]`, and optional legacy `ne_probe()` for `CONFIG_NETDEV_LEGACY_INIT`.

Control flow: module initialization optionally creates up to four synthetic platform devices, then calls `platform_driver_probe()`. Probe allocates an 8390 netdev, receives resources either from real platform resources or module arrays, and calls `do_ne_probe()`. `ne_probe1()` reserves the I/O window, performs a register sanity test, resets the NIC, initializes remote DMA registers to read 32 SAPROM bytes, distinguishes 8-bit versus 16-bit cards by duplicated bytes, validates the NE signature or known clone prefixes, discovers/fixes the IRQ, requests the interrupt, sets `ei_status` pages/callbacks, initializes the 8390 core, and registers the netdev. Packet receive and transmit later run through the 8390 core, which calls the driver callbacks to perform remote-DMA header reads, ring-buffer reads, and TX-buffer writes via `insb`/`insw`/`outsb`/`outsw`. Removal unregisters the netdev, detaches any PnP device, frees the IRQ, releases the I/O region, and frees the netdev.

State and persistence: all persistent driver state is in module arrays, synthetic platform devices, the `net_device`, and `ei_status`/`struct ei_device`. There is no disk persistence. Hardware state includes the 8390 page registers, RX/TX ring page layout, interrupt mask/status, and the station address read from SAPROM. `ei_status.dmaing`, `txing`, and callback pointers are central runtime state. `ei_status.priv` is reused as a PnP-device pointer, so cleanup and PM paths depend on it being cleared after detach.

Dependencies and integration points: depends on ISA I/O accessors, optional ISAPnP, platform-device plumbing, the generic netdev stack, and `8390.h`/8390 core symbols. Integration with old boot code comes from `<net/Space.h>` and `CONFIG_NETDEV_LEGACY_INIT`. Architecture-specific details affect `DCR_VAL`, especially Atari/Q40, TX49XX, and Realtek RTL8019 8-bit stop-page limiting.

Risks: ISA auto-probing can disturb other 8390 devices, so it is deliberately constrained. The driver relies on global `ei_status`, which is fragile for multi-device paths and PnP storage. Remote-DMA concurrency is guarded by `ei_status.dmaing` diagnostics rather than recovery. Bad-clone acceptance can bind unsupported hardware if signatures collide. Error paths must keep IRQ and I/O-region ownership balanced. Timing loops around reset and transmit RDC are short and hardware-sensitive. Odd-byte handling and word-mode selection are common corruption risks on unusual buses.

Test signals: useful build coverage includes `CONFIG_NE2000`, `CONFIG_ISA`, `CONFIG_ISAPNP`, and architecture variants that alter `DCR_VAL`. Runtime signals include probe logs with detected MAC/IRQ, successful `register_netdev()`, no reset-ack or invalid-signature warnings, TX RDC timeout absence, clean suspend/resume with PnP devices, packet RX/TX across odd and even lengths, and unload/reload without leaked I/O regions or IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne2k-pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne2k-pci.c

Purpose: this driver supports PCI NE2000 clone adapters such as RealTek RTL-8029, Winbond, Holtek, Via, SureCom, Compex, KTI, and NetVin variants. It moves PCI discovery and shared IRQ handling out of the old ISA driver while still using the generic 8390 core for Ethernet operation.

Important APIs, types, and functions: `ne2k_pci_tbl` maps PCI IDs to entries in `pci_clone_list`, whose flags describe 16-bit-only, 32-bit-only, full-duplex, and reduced stop-page quirks. Module parameters `options[]`, `full_duplex[]`, and `msg_enable` control debug and full-duplex overrides. `ne2k_pci_init_one()` performs PCI enablement, BAR validation, I/O region reservation, 8390 register sanity checking, SAPROM reads, netdev allocation, `ei_status` setup, and registration. `ne2k_pci_open()` and `ne2k_pci_close()` request/free shared IRQs and open/close the 8390 core. `ne2k_pci_reset_8390()`, `ne2k_pci_get_8390_hdr()`, `ne2k_pci_block_input()`, and `ne2k_pci_block_output()` are the 8390 callbacks. Full-duplex support is chipset-specific through `set_realtek_fdx()`, `set_holtek_fdx()`, and `ne2k_pci_set_fdx()`. Ethtool hooks expose driver info and message level.

Control flow: `module_pci_driver()` registers the PCI driver. Probe enables the PCI device, checks BAR0 is I/O space, reserves the 32-byte NE I/O extent, verifies 8390 behavior, allocates an 8390 netdev, resets the card, initializes remote-DMA registers, reads the SAPROM using byte or long I/O depending on flags, sets the memory ring pages, stores the `pci_dev` in `ei_status.priv`, initializes `NS8390_init()`, sets the MAC, and registers the interface. Opening requests the device IRQ with `IRQF_SHARED`, optionally programs full duplex, and calls `ei_open()`. TX/RX paths use remote DMA through the dataport, selecting word or long I/O and rounding counts for hardware requirements. PM detach/attach paths detach the netdev and reinitialize 8390 state on resume.

State and persistence: runtime state lives in the netdev private `struct ei_device`, global `ei_status`, PCI drvdata, and module parameter arrays. `ei_status.ne2k_flags` aliases `reg0` for chipset flags. Destructive hardware state includes reset, DCFG, remote DMA registers, ring page registers, IRQ masks, and chipset-specific full-duplex registers. There is no persistent storage beyond module parameters.

Dependencies and integration points: depends on PCI, I/O-port access, generic netdev, ethtool, and the 8390 core. Endianness handling is explicit for PowerPC through little-endian I/O helper definitions and by converting descriptor/header counts. It integrates with PCI PM through `SIMPLE_DEV_PM_OPS` and with userspace through ethtool message-level controls.

Risks: fnd-count indexing is subtle because module option arrays are matched to discovery order. Long-I/O paths round transfer counts and must not overrun skb buffers. The `ONLY_32BIT_IO` and `ONLY_16BIT_IO` flags must match silicon behavior or packet data can corrupt. The full-duplex register sequences are magic values for a narrow chipset set. Like other 8390 drivers, `ei_status.dmaing` detects but does not repair concurrent remote-DMA use. Probe failure returns `-ENODEV` for many conditions, which can hide exact root causes.

Test signals: compile with `CONFIG_NE2K_PCI`, `CONFIG_PCI`, and big-endian or PowerPC coverage if available. Runtime validation should check PCI ID binding, BAR reservation, MAC readout, shared IRQ operation, ping/traffic under 16-bit and 32-bit clones, full-duplex override behavior for Realtek/Holtek, ethtool `msglvl`, suspend/resume, TX RDC timeout absence, and unload freeing the I/O region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/ne2k-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/pcnet_cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/pcnet_cs.c

Purpose: this is a PCMCIA/CardBus-era NE2000-compatible driver for many NS8390-based PC Card Ethernet and combo cards. It supports remote-DMA operation, optional shared-memory windows, card-specific MAC discovery, transceiver selection, MII management for DL10019/DL10022 devices, and a watchdog for lost interrupts and link changes.

Important APIs, types, and functions: module parameters include `if_port`, `use_big_buf`, `mem_speed`, `delay_output`, `delay_time`, `use_shmem`, `full_duplex`, and `hw_addr[]`. `struct hw_info` records MAC-location and quirk flags such as `DELAY_OUTPUT`, `HAS_MISC_REG`, `USE_BIG_BUF`, `HAS_IBM_MISC`, `IS_DL10019`, `IS_DL10022`, `HAS_MII`, and `USE_SHMEM`. `struct pcnet_dev` extends 8390 private state with PCMCIA linkage, memory mapping, watchdog, PHY IDs, link state, and flags. Probe/configuration entry points are `pcnet_probe()`, `pcnet_config()`, `pcnet_try_config()`, `pcnet_confcheck()`, `try_io_port()`, and `pcnet_detach()`. MAC-discovery helpers are `get_hwinfo()`, `get_prom()`, `get_dl10019()`, `get_ax88190()`, and `get_hwired()`. Runtime hooks include `pcnet_open()`, `pcnet_close()`, `pcnet_reset_8390()`, `set_config()`, `ei_ioctl()`, `ei_watchdog()`, remote-DMA callbacks, shared-memory callbacks, and setup helpers.

Control flow: the PCMCIA core matches `pcnet_ids` and calls `pcnet_probe()`, which allocates an 8390 netdev with extra private space and calls `pcnet_config()`. Configuration loops CIS options, requests I/O windows, enables the device, derives IRQ and base address, rejects AX88190 hardware that should use `axnet_cs`, reads the MAC by CIS window, PROM, DL10019 registers, AX88190 registers, or user override, applies card/user flags, chooses normal or big packet-buffer page ranges, and prefers shared memory when available and not disabled. It then initializes `ei_status`, optionally probes MII PHYs, registers the netdev, and logs card properties. Opening verifies card presence, configures misc/MII registers, requests a shared IRQ wrapper, starts the watchdog, and opens the 8390 core. IRQs call the 8390 interrupt path and reset stale counters. The watchdog detects pending interrupts after latency expiry, temporarily fast-polls after dropped interrupts, polls MII link state, toggles collision/full-duplex programming, switches between Ethernet and HomePNA PHYs when present, and reinitializes the 8390 core on link changes.

State and persistence: state lives in PCMCIA resources, `struct pcnet_dev`, `ei_status`, mapped shared-memory windows, timers, PHY register state, and the netdev. No state is persisted to disk. `link->open` tracks active opens for suspend/resume. Shared-memory mode stores `ei_status.mem`, `ei_status.priv` as window size, and device `mem_start`/`mem_end`; remote-DMA mode stores only ring page limits and callbacks.

Dependencies and integration points: depends on PCMCIA CIS/resource APIs, netdevice/etherdevice, MII ioctls, timers, I/O port access, optional CIS firmware files, and the 8390 core. It integrates with userspace via old `SIOCGMIIPHY`, `SIOCGMIIREG`, `SIOCSMIIREG`, and `ndo_set_config` port switching. `MODULE_FIRMWARE` entries declare replacement CIS blobs for known cards.

Risks: the enormous device ID table and many card quirks make regressions easy. The shared-memory setup scribbles on adapter memory to validate the mapping; offset/window calculations must be exact. The watchdog re-enters interrupt handling if an interrupt appears lost, so timer, IRQ, and close synchronization are important. MDIO/EEPROM bit-banging is timing-sensitive. User-supplied `hw_addr[]` can force invalid or duplicate MACs. `ei_status` global state and PCMCIA hot-unplug/suspend paths must remain balanced around IRQs, timers, and ioremap windows.

Test signals: compile with `CONFIG_PCMCIA` and `CONFIG_PCNET_CS`; check all referenced CIS firmware names are packaged where needed. Runtime signals include successful I/O-resource allocation, MAC read by each supported mechanism, remote-DMA traffic, shared-memory traffic with wraparound receive, if_port switching for combo media, MII ioctl reads/writes, link beat found/lost messages, no watchdog storm, suspend/resume with open devices, hot unplug cleanup, and timer/IRQ cleanup on close and detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/pcnet_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/stnic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/stnic.c

Purpose: this is a SuperH SolutionEngine-specific National Semiconductor DP83902A ST-NIC Ethernet driver. It supplies board-specific register access, reset, and remote-DMA callbacks to the generic 8390 core.

Important APIs, types, and functions: `stnic_probe()` is the module init and only probes when `MACH_SE` is true. `STNIC_READ()`, `STNIC_WRITE()`, and `STNIC_DELAY()` encapsulate the SH7750 memory-mapped 16-bit register access pattern. `stnic_reset()`, `stnic_get_hdr()`, `stnic_block_input()`, and `stnic_block_output()` implement the 8390 operations. `stnic_init()` resets and calls `NS8390_init()`. `stnic_cleanup()` unregisters and frees the singleton device. `stnic_eadr` is a fallback MAC address and can be overwritten by `sh_bios_get_node_addr()` when `CONFIG_SH_STANDARD_BIOS` is enabled.

Control flow: initialization checks the machine vector, allocates an 8390 netdev, resolves the MAC, assigns a fake `base_addr` plus the fixed `IRQ_STNIC`, sets `ei_netdev_ops`, requests an unshared IRQ, initializes `ei_status` for 16-bit access and endianness, attaches ST-NIC callbacks, initializes hardware, stores `msg_enable`, and registers the netdev. RX and TX use remote DMA through the `PA_83902_IF` register with explicit endian byte ordering. Reset toggles `PA_83902_RST` and delays. Cleanup unregisters the netdev, frees the IRQ, and frees the netdev.

State and persistence: the driver is singleton state: `stnic_dev`, `stnic_eadr`, the netdev, and global `ei_status`. Hardware state is fixed physical mappings from the SolutionEngine board headers. No state persists beyond the loaded module and hardware registers.

Dependencies and integration points: depends on SuperH board headers, `mach-se/mach/se.h`, optional SH BIOS, IRQ_STNIC, raw volatile memory-mapped access, and the 8390 core. It is tightly coupled to SolutionEngine hardware and is not a generic platform driver.

Risks: the hardcoded fallback MAC address is explicitly marked as needing board-specific replacement. Pointer casts to physical addresses and volatile accessors are architecture-specific and bypass common `ioremap` patterns. `stnic_cleanup()` assumes `stnic_dev` is valid after successful init. Odd-length TX/RX rounds up and reads/writes extra bytes, requiring the caller buffers and hardware to tolerate it. There is little probe-time validation beyond `MACH_SE`.

Test signals: build coverage must include SuperH/SolutionEngine configs. Runtime signs include successful IRQ request, logged ST-NIC registration, correct MAC from SH BIOS if available, packet RX/TX on little- and big-endian configurations, reset behavior, unload cleanup, and absence of packet byte swapping or odd-length corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/stnic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/xsurf100.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/xsurf100.c

Purpose: this is a Zorro bus shim for the Individual Computers X-Surf 100 Amiga Ethernet board. It does not register a netdev directly; instead it reserves and maps board-specific control and 32-bit data areas, then registers an `ax88796` platform device with custom block I/O callbacks.

Important APIs, types, and functions: `struct xsurf100_ax_plat_data` embeds `struct ax_plat_data` and carries mapped X-Surf control/data areas. `is_xsurf100_network_irq()` checks the board interrupt status register for the `ax88796` core. `z_memcpy_fromio32()` and `z_memcpy_toio32()` force 32-bit-only transfers, including m68k inline assembly for 32-byte reads. `xs100_read()`, `xs100_write()`, `xs100_block_input()`, and `xs100_block_output()` provide accelerated NE-style remote-DMA data movement for the AX88796 core. `xsurf100_probe()` reserves resources, builds register offsets, fills AX88796 platform data, maps registers, registers the child platform device, and stores it in Zorro drvdata. `xsurf100_remove()` unregisters the child and releases mappings/regions.

Control flow: the Zorro driver matches the X-Surf 100 product ID. Probe reserves the first control region and the larger 32-bit data region, initializes register offsets as four-byte spaced registers, sets AX88796 flags for EEPROM, word length, DCR/RCR values, and IRQ checking, maps the control and data windows, installs block I/O callbacks, and calls `platform_device_register_resndata()` with IRQ and memory resources for `ax88796`. The `ax88796` driver then owns netdev creation and 8390-compatible operation, invoking the X-Surf callbacks for RX/TX transfers. Removal unwinds child device registration, iounmap, and memory region ownership.

State and persistence: state is transient platform data copied into the child platform device and Zorro drvdata. The static `reg_offsets[32]` must outlive probe because the child driver references it. Hardware state is in the mapped Zorro control area, 8390 register window, and data-area FIFOs. No persistent storage exists.

Dependencies and integration points: depends on Zorro bus APIs, Amiga interrupt definitions, the `ax88796` platform-driver contract, m68k Zorro accessors (`z_read*`, `z_write*`), and 8390 constants via `8390.h`. Integration is deliberately layered: this driver supplies bus/board adaptation while `ax88796` supplies the generic netdev.

Risks: lifetime of platform data and static register offsets must remain valid for the child. Error paths must unmap and release both regions in the right order. The custom 32-bit copy routines assume aligned counts after the caller’s block sizing, and the tail path uses 16/8-bit dataport accesses. `is_xsurf100_network_irq()` filters shared Amiga port IRQs and incorrect status interpretation can lose or misroute interrupts. `xsurf100_remove()` assumes a registered child exists and retrieves platform data from it.

Test signals: build with Zorro/Amiga and AX88796 support. Runtime checks include successful child `ax88796` device creation, reserved regions visible, interrupt filtering under shared Amiga port IRQ load, RX/TX throughput using the 32-bit area, odd-length TX/RX tails, child removal on module unload, and no leaks on any probe failure stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/xsurf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/zorro8390.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/zorro8390.c

Purpose: this is the Amiga Zorro-II NS8390 driver for Ariadne II and older X-Surf boards containing RTL8019AS-compatible controllers. It adapts Zorro memory-mapped, word-spaced registers to the 8390 core.

Important APIs, types, and functions: `cards[]` maps Zorro IDs to board names and register offsets. The file includes `lib8390.c` directly after redefining `ei_inb/outb` and `EI_SHIFT`, producing local `__ei_*` and `__NS8390_*` core entry points. `zorro8390_reset_8390()`, `zorro8390_get_8390_hdr()`, `zorro8390_block_input()`, and `zorro8390_block_output()` implement the hardware callbacks. `zorro8390_init()` performs board reset, SAPROM reading, IRQ request, `ei_status` setup, netdev ops assignment, core init, and registration. `zorro8390_init_one()` matches Zorro devices, allocates a netdev, reserves memory, and calls init. `zorro8390_remove_one()` unregisters and frees resources.

Control flow: module init registers a Zorro driver. Probe maps the Zorro product ID to a register offset, reserves a double-size NE I/O extent due to word-spaced registers, allocates a private 8390 netdev, and calls `zorro8390_init()`. Init resets the board, primes remote-DMA registers to read the SAPROM, reads every other byte from the dataport, programs word mode, requests the shared Amiga ports IRQ, sets the MAC, fills ring pages and callbacks in `ei_status`, assigns register offsets, initializes the 8390 core, and registers the netdev. Packet I/O uses zorro byte/word reads and writes to the remote-DMA dataport, with TX completion polling and timeout reset/reinit. Remove unregisters, frees `IRQ_AMIGA_PORTS`, releases the memory region, and frees the netdev.

State and persistence: state lives in the Zorro drvdata netdev, global `ei_status`, static register-offset table, and hardware registers. `dev->base_addr` stores a virtual Zorro address; release converts it back with `ZTWO_PADDR()`. There is no persistent storage.

Dependencies and integration points: depends on Zorro bus IDs, Amiga hardware/interrupt helpers, Zorro-II address conversion, and the 8390 core included as source. It provides netdev operations that call the included `__ei_*` symbols. Shared interrupt behavior depends on the Amiga ports IRQ.

Risks: including `lib8390.c` directly makes macro definitions and symbol names highly order-dependent. Release uses `NE_IO_EXTENT * 2`, while probe reservation also uses doubled extents; mistakes in address conversion would leak or release wrong regions. Remote-DMA conflict handling is diagnostic only. Word swapping of the packet header count and odd-byte RX/TX tails are endian-sensitive. A shared IRQ without a board-specific IRQ-status filter can rely heavily on the 8390 interrupt path to reject non-device interrupts.

Test signals: build for Amiga/Zorro configs. Runtime signs include correct product match and offset selection, MAC read from SAPROM, shared IRQ stability, packet RX/TX with odd lengths, TX RDC timeout absence, clean remove/unload, and no endian-swapped packet length errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/zorro8390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/Kconfig

Purpose: this top-level Ethernet Kconfig menu gates all Ethernet LAN drivers under `drivers/net/ethernet`. It defines the parent `ETHERNET` menu, a generic `MDIO` tristate helper symbol, sources vendor Kconfig files, and declares a few standalone drivers that live directly in the Ethernet directory.

Important APIs, types, and functions: this is declarative Kconfig rather than C code. `menuconfig ETHERNET` depends on `NET` and defaults to `y`. `config MDIO` is a bare tristate helper. The file uses many `source "drivers/net/ethernet/<vendor>/Kconfig"` directives, including the requested `actions`, `adaptec`, and `8390` subtrees. Direct symbols include `CX_ECAT`, `JME`, `KORINA`, `LANTIQ_ETOP`, `LANTIQ_XRX200`, `FEALNX`, `ETHOC`, and `OA_TC6`, each with dependency/select/help metadata.

Control flow: Kconfig evaluation enters this file from the networking driver configuration tree. If `ETHERNET` is disabled, all nested vendor choices are hidden. If enabled, each sourced vendor file contributes its own vendor gate and driver symbols. Direct driver symbols add dependencies such as `PCI`, `X86 || COMPILE_TEST`, `MIKROTIK_RB532 || COMPILE_TEST`, `SOC_TYPE_XWAY`, `HAS_IOMEM && HAS_DMA`, and `SPI`, and select supporting libraries such as `CRC32`, `MII`, `PHYLIB`, and `BITREVERSE`.

State and persistence: Kconfig state persists only in kernel configuration outputs such as `.config`. The file itself stores no runtime state, but the symbol graph determines which Makefile objects are built and which driver code is reachable.

Dependencies and integration points: the file depends on the wider Kconfig language and networking config hierarchy. It integrates with the top-level Ethernet Makefile through matching `CONFIG_*` symbols and with vendor Kconfig files through source order. Source ordering matters for menu presentation and for keeping vendor gates visible under `if ETHERNET`.

Risks: missing or misordered `source` lines can orphan an entire vendor directory. Incorrect dependencies can expose drivers on unsupported architectures or hide them from `COMPILE_TEST`. Missing `select` clauses can break builds by omitting library dependencies. Direct symbols mixed among vendor source lines make merge conflicts and alphabetical drift possible.

Test signals: run Kconfig parsing through `olddefconfig`, `allyesconfig`, `allmodconfig`, and relevant `COMPILE_TEST` builds. Confirm `CONFIG_NET_VENDOR_ACTIONS`, `CONFIG_OWL_EMAC`, `CONFIG_NET_VENDOR_ADAPTEC`, `CONFIG_ADAPTEC_STARFIRE`, and `CONFIG_NET_VENDOR_8390` appear only when expected, and that Makefile object selection follows the enabled symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/Makefile

Purpose: this top-level Ethernet Makefile maps Kconfig vendor and driver symbols to subdirectories or standalone objects under `drivers/net/ethernet`.

Important APIs, types, and functions: this is Kbuild syntax. Most lines use `obj-$(CONFIG_NET_VENDOR_*) += <vendor>/` to descend into vendor subdirectories. Direct object mappings include `ec_bhf.o` for `CONFIG_CX_ECAT`, `jme.o`, `korina.o`, `lantiq_etop.o`, `lantiq_xrx200.o`, `fealnx.o`, `ethoc.o`, and `oa_tc6.o`. Requested integration points include `obj-$(CONFIG_NET_VENDOR_8390) += 8390/`, `obj-$(CONFIG_NET_VENDOR_ACTIONS) += actions/`, and `obj-$(CONFIG_NET_VENDOR_ADAPTEC) += adaptec/`.

Control flow: during Kbuild, enabled or modular config symbols expand `obj-y` or `obj-m` entries. Vendor directory entries cause recursive descent into the corresponding subdirectory Makefile, where individual driver objects are selected. Disabled symbols expand to nothing and skip both directory traversal and compilation.

State and persistence: there is no runtime state. Build state is determined by `.config`, generated Kbuild variables, and object outputs in the build directory. The file is part of the build graph and persists as source.

Dependencies and integration points: depends on Kbuild semantics and symbol names declared in the top-level and vendor Kconfig files. It must stay synchronized with directory names and config symbols. It integrates with module naming through subdirectory Makefiles that map `CONFIG_*` to `.o` files.

Risks: a config symbol mismatch silently prevents a driver directory or object from building. Adding a vendor Kconfig without a matching Makefile line, or vice versa, creates visible config with no build output or unreachable build rules. Some directories are gated by driver-specific symbols rather than vendor symbols, so consistency checks need to account for both styles.

Test signals: use `make drivers/net/ethernet/` or targeted builds with relevant configs enabled. Confirm `CONFIG_NET_VENDOR_ACTIONS=m` descends into `actions/` and builds `owl-emac.o`, `CONFIG_NET_VENDOR_ADAPTEC=m` descends into `adaptec/`, and `CONFIG_NET_VENDOR_8390` descends into `8390/`. `allmodconfig` should not show missing-directory or unused-object errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Kconfig

Purpose: this vendor Kconfig file declares the Actions Semi Ethernet menu and the Owl EMAC driver option.

Important APIs, types, and functions: `config NET_VENDOR_ACTIONS` is a boolean vendor gate depending on `ARCH_ACTIONS || COMPILE_TEST` and defaulting to `ARCH_ACTIONS`. `config OWL_EMAC` is a tristate for the Actions Semi Owl Ethernet MAC and selects `PHYLIB`. The help text identifies S500 and S900 SoCs and 10/100 Mb/s IEEE 802.3 operation.

Control flow: the top-level Ethernet Kconfig sources this file. If the vendor gate is disabled, `OWL_EMAC` is hidden. When enabled, `OWL_EMAC=y/m` controls whether `actions/Makefile` builds `owl-emac.o` built-in or as a module.

State and persistence: configuration state persists in `.config`. No runtime state is stored here.

Dependencies and integration points: integrates with `drivers/net/ethernet/Kconfig`, `drivers/net/ethernet/Makefile`, `actions/Makefile`, and the `owl-emac.c` driver. It selects `PHYLIB` because the driver uses phylib helpers, MDIO registration, and PHY connection APIs. The vendor dependency permits native Actions builds and compile-test coverage elsewhere.

Risks: this symbol does not explicitly depend on `HAS_IOMEM`, `HAS_DMA`, OF, clocks, or reset support even though the driver uses MMIO, DMA, device tree, clock, and reset APIs; broader architecture and compile-test coverage need to catch missing dependencies. If `PHYLIB` selection is removed, `owl-emac` will fail to link.

Test signals: Kconfig parsing with `ARCH_ACTIONS`, without `ARCH_ACTIONS`, and with `COMPILE_TEST`. Build `CONFIG_OWL_EMAC=m` and `=y`, verify `PHYLIB` is selected, and confirm menu visibility under `ETHERNET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Makefile

Purpose: this Kbuild file compiles the Actions Semi Owl EMAC driver when its Kconfig symbol is enabled.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_OWL_EMAC) += owl-emac.o`.

Control flow: Kbuild descends into this directory when `CONFIG_NET_VENDOR_ACTIONS` enables the vendor directory in the parent Makefile. If `CONFIG_OWL_EMAC=y`, `owl-emac.o` is built into the kernel; if `m`, it becomes a module; if disabled, no object is produced.

State and persistence: no runtime state. Build outputs depend on `.config` and Kbuild.

Dependencies and integration points: depends on `actions/Kconfig` defining `CONFIG_OWL_EMAC` and on `owl-emac.c`/`owl-emac.h` being present. It integrates with module metadata in `owl-emac.c`.

Risks: because the Makefile is minimal, any future split of `owl-emac` into multiple objects would require updating this line into a composite-object rule. A symbol rename in Kconfig without this Makefile change would silently stop building the driver.

Test signals: targeted build with `CONFIG_NET_VENDOR_ACTIONS=y` and `CONFIG_OWL_EMAC=m/y`; verify `owl-emac.o` or module output exists and no stale object names are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.c

Purpose: this is the Actions Semi Owl SoC 10/100 Ethernet MAC platform driver. It implements DMA descriptor-ring networking, NAPI interrupt handling, MDIO/phylib integration, clock/reset setup, multicast setup frames, suspend/resume, ethtool hooks, and recovery from known MAC hardware stalls.

Important APIs, types, and functions: register helpers `owl_emac_reg_read/write/update/set/clear()` wrap MMIO. Ring helpers manage coherent descriptor arrays and SKB/DMA arrays: `owl_emac_ring_alloc()`, `owl_emac_ring_prepare_rx()`, `owl_emac_ring_prepare_tx()`, unprepare helpers, and ring head/tail helpers. DMA helpers map and unmap RX/TX skbs. Link and MAC programming is handled by `owl_emac_set_hw_mac_addr()`, `owl_emac_update_link_state()`, `owl_emac_adjust_link()`, and setup-frame helpers. TX path is `owl_emac_ndo_start_xmit()`, `owl_emac_tx_complete_tail()`, and `owl_emac_tx_complete()`. RX path is `owl_emac_rx_process()` and `owl_emac_poll()`. Device lifecycle flows through `owl_emac_probe()`, `owl_emac_remove()`, `owl_emac_enable()`, `owl_emac_disable()`, `owl_emac_suspend()`, and `owl_emac_resume()`. MDIO uses `owl_emac_mdio_read/write/wait/init()`, while PHY attachment uses `owl_emac_phy_init()`. `owl_emac_reset_task()` is scheduled on TX timeout or repeated internal errors.

Control flow: probe allocates an Ethernet netdev, reads `phy-mode`, sets a 32-bit DMA mask, allocates RX/TX coherent descriptor rings plus SKB metadata arrays, maps MMIO, requests a shared IRQ, acquires/enables `eth` and `rmii` clocks, sets the RMII/SMII clock rate, gets reset control, obtains or randomizes the MAC address, hardware-resets the core, enables MDIO clock generation, registers the MDIO bus from the `mdio` child node, connects to the PHY, initializes reset work, assigns netdev operations and ethtool ops, adds NAPI, and registers the netdev. Open calls `owl_emac_enable()`, which stops DMA, disables/clears IRQs, prepares TX/RX rings, soft-resets the core, programs MAC address, sends a setup frame, enables NAPI/IRQs/DMA, starts PHY, and starts the queue. The IRQ handler disables interrupts and schedules NAPI. Poll clears status, completes TX, processes RX up to budget, handles receive-buffer-unavailable by issuing poll-demand, re-enables interrupts after completion, and schedules a reset after repeated internal TX/RX process-state errors. Stop disables DMA/IRQs/NAPI/PHY and frees ring buffers.

State and persistence: `struct owl_emac_priv` stores the netdev, MMIO base, clocks, reset control, RX/TX rings, MDIO bus, NAPI, PHY mode/link/speed/duplex/pause, multicast address list, reset work, message level, and spinlock. Rings persist while the device is open and own coherent descriptors plus per-slot SKBs and DMA mappings. MAC/flow-control/link state persists in hardware registers until reset or power management. No disk persistence exists; MAC may be loaded from firmware/platform data or generated randomly per boot.

Dependencies and integration points: depends on platform-device and OF APIs, DMA mapping, clock framework, reset controller, phylib, OF MDIO, NAPI, ethtool, and netdevice core. Device-tree integration requires compatible `actions,owl-emac`, a valid `phy-mode`, clocks named `eth` and `rmii`, reset control, IRQ, MMIO resource, and an available `mdio` child/PHY. Kconfig selects `PHYLIB`; parent build selects this file through `CONFIG_OWL_EMAC`.

Risks: several hardware workarounds are explicit: TX is restricted to one frame at a time, TX completion may manually clear a stuck OWN bit, interrupt disable avoids clearing status bits accidentally, and repeated internal state errors trigger full MAC reset. RX error handling reuses current SKBs on allocation/mapping failure; descriptor head/tail correctness is critical. `owl_emac_poll()` uses static TX/RX error counters shared across instances, which is a multi-device risk. Reset work disables/enables the MAC without first checking device-open lifetime beyond scheduling context. DMA descriptors store 32-bit addresses, so the 32-bit coherent mask is required. `owl_emac_ndo_set_mac_addr()` writes hardware and sends a setup frame only when not running; failure handling around setup-frame transmit can stop the queue.

Test signals: build with `CONFIG_OWL_EMAC`, OF, PM, and COMPILE_TEST. Runtime validation should include probe with complete DT resources, MDIO bus registration, PHY attach and link changes, open/close cycles, RX/TX traffic, multicast list changes beyond and within 14 addresses, promiscuous/all-multicast modes, TX timeout recovery, NAPI budget exhaustion, RX buffer unavailable interrupts, suspend/resume while down and while running, randomized MAC fallback warning, ethtool link settings and msglevel, and DMA mapping failure paths under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.h

Purpose: this header defines the register map, bit fields, constants, descriptor formats, and private data structures used by the Actions Semi Owl EMAC driver.

Important APIs, types, and functions: constants define driver name, poll/timeout durations, MTU bounds, RX frame size, SKB alignment/reserve, multicast/setup-frame limits, and ring sizes. Register macros cover MAC CSR0/1/2/3/4/5/6/7/8/9/10/11/16/17/18/19/20 and MAC_CTRL, including DMA start/stop, status, interrupt, MDIO, MAC address, flow-control, and RMII/SMII fields. Descriptor macros define RX `RDES0/RDES1` and TX `TDES0/TDES1` ownership, status, error, size, interrupt, setup-frame, and ring-end bits. Data structures include `struct owl_emac_addr_list`, `struct owl_emac_ring_desc`, `struct owl_emac_ring`, and `struct owl_emac_priv`. Clock definitions provide `owl_emac_clk_names[]`, `OWL_EMAC_NCLKS`, and `enum owl_emac_clk_map`.

Control flow: this header has no executable control flow. It shapes how `owl-emac.c` programs hardware: ring descriptor fields are written before ownership transfer, CSR status bits are cleared by writing status back, CSR6 controls DMA and link mode, CSR10 drives MDIO transactions, and CSR3/CSR4 receive descriptor base addresses.

State and persistence: `struct owl_emac_priv` is the central per-device state object. `struct owl_emac_ring` persists descriptor memory, DMA addresses, SKB pointers, and circular head/tail indices while the driver is active. `struct owl_emac_ring_desc` mirrors hardware DMA descriptors and must remain coherent with device-visible memory. `struct owl_emac_addr_list` caches multicast addresses for setup-frame programming.

Dependencies and integration points: the header expects kernel types and macros included by the C file, including `BIT`, `GENMASK`, `ETH_*`, `HZ`, `struct net_device`, `struct clk_bulk_data`, `struct reset_control`, `struct mii_bus`, `struct napi_struct`, `phy_interface_t`, `struct work_struct`, and spinlocks. Its register definitions must match the Actions Owl EMAC hardware manual and the C implementation.

Risks: duplicated `OWL_EMAC_VAL_MAC_CSR10_OPCODE_WR` definitions should remain consistent. Ring sizes are powers of two, required by `CIRC_SPACE` and the mask-based next-index helper. Descriptor bit definitions are correctness-critical; wrong masks can cause DMA ownership, length, or error interpretation bugs. Address fields are `u32`, tying the implementation to a 32-bit DMA mask. Header constants such as multicast limit and setup-frame length must align with hardware filtering behavior.

Test signals: compile with sparse/W=1 for type assumptions, validate ring sizes stay powers of two, exercise RX/TX descriptors under traffic, verify CSR bit programming by register traces if available, and test RMII/SMII, flow control, multicast, MDIO, and interrupt paths that consume these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/actions/owl-emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Kconfig

Purpose: this vendor Kconfig file declares the Adaptec Ethernet menu and the Starfire/DuraLAN PCI adapter driver option.

Important APIs, types, and functions: `config NET_VENDOR_ADAPTEC` is a boolean vendor gate, defaults to `y`, and depends on `PCI`. `config ADAPTEC_STARFIRE` is a tristate depending on `PCI`, selecting `CRC32` and `MII`, with help text describing Adaptec Starfire/DuraLAN 64-bit PCI boards and module name `starfire`.

Control flow: the top-level Ethernet Kconfig sources this file under `if ETHERNET`. If PCI is unavailable or the vendor gate is off, `ADAPTEC_STARFIRE` is hidden. When enabled, `adaptec/Makefile` builds `starfire.o`.

State and persistence: only Kconfig state in `.config`; no runtime state.

Dependencies and integration points: integrates with `drivers/net/ethernet/Kconfig`, the parent Ethernet Makefile, `adaptec/Makefile`, and `starfire.c`. The `CRC32` and `MII` selections reflect library requirements of the driver.

Risks: the vendor gate defaulting to `y` exposes the menu broadly on PCI systems, so driver dependencies must be accurate. Removing selected helper libraries would break link/build. Help text distinguishes older 32-bit boards that use the tulip driver; incorrect user selection may bind unsupported hardware only if PCI IDs overlap in the driver.

Test signals: Kconfig parsing with and without PCI, `CONFIG_ADAPTEC_STARFIRE=m/y` builds, selected `CRC32` and `MII` symbols, and module output named `starfire`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Makefile

Purpose: this Kbuild file maps the Adaptec Starfire Kconfig symbol to its object file.

Important APIs, types, and functions: the build rule is `obj-$(CONFIG_ADAPTEC_STARFIRE) += starfire.o`.

Control flow: when the parent Ethernet Makefile descends into `adaptec/`, Kbuild builds `starfire.o` built-in for `CONFIG_ADAPTEC_STARFIRE=y`, as a module for `m`, or not at all when disabled.

State and persistence: no runtime state. Build products are derived from `.config`.

Dependencies and integration points: depends on `adaptec/Kconfig` defining `CONFIG_ADAPTEC_STARFIRE` and on `starfire.c` existing in this directory. It integrates with module metadata in the C file and parent vendor-directory selection through `CONFIG_NET_VENDOR_ADAPTEC`.

Risks: a symbol rename or file rename without this line update would silently disable the driver build. Additional source files for Starfire would require a composite-object rule.

Test signals: targeted Kbuild with `CONFIG_NET_VENDOR_ADAPTEC=y` and `CONFIG_ADAPTEC_STARFIRE=m/y`, verifying `starfire.o` or `starfire.ko` is generated without missing-object errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/adaptec/Makefile -->
