# subset-b-004584 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/macsonic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/macsonic.c

## Purpose
`macsonic.c` is the Macintosh platform and NuBus glue for the shared DP83932 SONIC Ethernet core. It identifies onboard, comm-slot, DuoDock, Apple, Dayna, and DaynaLink SONIC variants, selects the correct register offset and 16-bit versus 32-bit DMA descriptor layout, obtains a MAC address from PROM or CAM, and binds the shared `sonic.c` netdevice operations to platform and NuBus driver models.

## Important APIs, types, and functions
Key local types are `enum macsonic_type` and the `macsonic_netdev_ops` table. `SONIC_READ()` and `SONIC_WRITE()` are defined before including `sonic.c`, so the shared core uses NuBus word access through `dev->base_addr` and `lp->reg_offset`. `macsonic_open()` requests the primary IRQ and, for onboard A/UX remapping, also `IRQ_NUBUS_9`; `macsonic_close()` unwinds both. `mac_onboard_sonic_probe()` handles built-in and comm-slot probing. `mac_sonic_nubus_probe_board()` handles card-specific register bases, PROM bases, DCR values, DMA bit mode, and IRQ mapping. `mac_sonic_platform_probe()` and `mac_sonic_nubus_probe()` allocate `struct net_device`, initialize `struct sonic_local`, call shared setup, then register the netdev.

## Control flow
Module init registers both platform and NuBus drivers. Platform probe allocates an Ethernet device, stores `lp->device`, sets platform drvdata, performs onboard probing, initializes debug messaging, and registers the netdev. NuBus probe skips PDS/comm-slot cases, scans functional resources for a recognized network card, allocates a netdev, configures the board, and registers it. Open acquires IRQs before delegating to `sonic_open()`. Close delegates to `sonic_close()` before freeing IRQs. Removal unregisters the netdev, frees coherent descriptor memory allocated by `sonic_alloc_descriptors()`, and frees the netdev.

## State and persistence
Persistent hardware state comes from NuBus resources, PROM bytes, CAM contents left by firmware/MacOS, Macintosh model metadata, and the SONIC register set. Runtime state is held in `struct sonic_local`: register offset, DMA bit mode, descriptor memory, DMA addresses, rings, stats, and lock. The driver has no disk persistence. It may randomize the MAC address if PROM and CAM contents are invalid.

## Dependencies and integration points
This file depends on classic Macintosh platform data, NuBus APIs, `hwreg_present()`, VIA interrupt mapping, DMA coherent allocation, and the shared `sonic.h`/`sonic.c` core. It integrates with the kernel netdevice stack via `net_device_ops`, platform driver registration, NuBus driver registration, and standard Ethernet address helpers.

## Risks and edge cases
Register access macros depend on `dev` and `lp` local variable names being in scope when shared `sonic.c` code is compiled into this translation unit. MAC discovery is fragile: PROM bytes may be bit-reversed, absent, or invalid, and CAM fallback only works if earlier firmware initialized it. The onboard probe uses model-specific assumptions and direct hardware presence checks. The dual-IRQ path must remain re-entrant; the shared interrupt handler relies on `lp->lock` for that. Descriptor memory is freed only after successful probe paths allocate it, so cleanup labels must stay aligned with setup order.

## Test signals
Useful signals are successful platform and NuBus probe logs, correct MAC extraction for each supported board family, `register_netdev()` success, interrupt delivery on both onboard IRQ mappings, RX/TX traffic through shared SONIC paths, multicast CAM reload behavior, suspend-free removal, and leak-free failure paths when descriptor allocation or registration fails. Build coverage requires Macintosh/NuBus configurations that compile this file and the included `sonic.c` core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/macsonic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/natsemi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/natsemi.c

## Purpose
`natsemi.c` is a PCI Ethernet driver for National Semiconductor DP83815/DP83816-style DP8381x controllers. It manages PCI probe/remove, EEPROM and MDIO access, internal/external PHY selection, descriptor rings, NAPI RX/TX interrupt handling, multicast filtering, MTU changes, ethtool support, Wake-on-LAN, a DSP configuration workaround, and power management.

## Important APIs, types, and functions
The main private state is `struct netdev_private`, which stores MMIO base, coherent RX/TX descriptor rings, SKB and DMA address arrays, NAPI, timer, lock, PHY/media configuration, filters, thresholds, silicon revision, EEPROM size, and WoL state. `natsemi_probe1()` maps PCI BAR 1, reads the EEPROM-derived MAC, initializes media, and registers the netdev plus a `dspcfg_workaround` sysfs file. `netdev_open()` resets hardware, requests the IRQ, allocates rings, enables NAPI, initializes registers, and starts the timer. `start_tx()`, `netdev_tx_done()`, `intr_handler()`, `natsemi_poll()`, and `netdev_rx()` implement the data path. `netdev_close()`, `natsemi_suspend()`, and `natsemi_resume()` coordinate shutdown and PM. Ettool helpers cover registers, EEPROM, link settings, message level, WoL, secure-on password, and nway reset.

## Control flow
Module init registers a PCI driver. Probe enables the device, handles nonstandard PM state, requests regions, maps MMIO, reads and reconstructs the MAC from EEPROM, sets up private state, detects internal or external PHY, assigns netdev and ethtool operations, initializes media, registers the device, and creates sysfs. Open resets the chip, requests IRQ, allocates coherent rings, initializes descriptors, writes MAC/filter registers, enables interrupts, starts RX/TX, and schedules `netdev_timer()`. Interrupts only acknowledge and disable device interrupts, then schedule NAPI. NAPI drains RX, completes TX, handles abnormal interrupts, and reenables interrupts when idle. Close disables NAPI/timer/IRQ, sets `hands_off`, stops engines, freezes stats, drains and frees rings, and optionally restarts silent RX for WoL.

## State and persistence
Persistent inputs include EEPROM contents, WOL command registers, silicon revision, module parameters, and ethtool-configured media/WoL settings retained in private state while loaded. Runtime state is split between hardware registers and `netdev_private`: producer/consumer ring indices, mapped SKBs, RX mode hash table, cached TX/RX config, PHY settings, `SavedClkRun`, DSP expected value, and `hands_off` PM/shutdown gating.

## Dependencies and integration points
The file uses PCI managed enable/region helpers, MMIO accessors, DMA mapping/coherent APIs, NAPI, netdevice ops, ethtool, MII ioctl helpers, timers, sysfs device attributes, PM ops, and CRC multicast hashing. It interacts directly with DP8381x register semantics, EEPROM serial protocol, internal MII registers, and external MII bit banging.

## Risks and edge cases
The file notes incomplete big-endian support. Descriptor ownership ordering is delicate: TX sets descriptor ownership last and uses `wmb()`, while RX must recover from multi-buffer packets with an AN-1287 reset sequence. The `hands_off` flag and IRQ/NAPI synchronization protect PM and close paths; regressions can create IRQ storms or hardware access during suspend. DSP and cable errata handling is revision-sensitive and timer-driven. The external PHY scan must move the internal PHY to avoid bus conflicts. WoL paths restart RX with a null ring pointer and must preserve PME bits. MTU changes while running temporarily stop RX/TX and rebuild RX buffers.

## Test signals
Important test signals include PCI probe/remove on DP83815/DP83816 variants, internal and external PHY link negotiation, NAPI RX under load, TX queue stop/wake behavior, RX OOM timer refill, multicast/promiscuous filtering, MTU changes up to the driver limit, ethtool register/EEPROM/WoL/link operations, sysfs `dspcfg_workaround` toggling, suspend/resume with and without WoL, and forced TX timeout/RX reset recovery. Kernel build tests should include `CONFIG_NET_POLL_CONTROLLER` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/natsemi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/ns83820.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/ns83820.c

## Purpose
`ns83820.c` is the PCI driver for the National Semiconductor DP83820 10/100/1000 Ethernet controller. It supports 32-bit and 64-bit DMA addressing, descriptor-based RX/TX, link-state handling for copper and optical/TBI interfaces, hardware checksum assistance, optional VLAN tag acceleration, ethtool link operations, statistics collection, and device BIST/load setup.

## Important APIs, types, and functions
`struct ns83820` is the private device state, containing MMIO base, PCI/netdev pointers, RX descriptor state in `struct rx_info`, a refill work item, locks, cached CFG/IMR/MEAR values, TX ring indices/SKBs/descriptors, and a TX watchdog timer. Descriptor access is abstracted by `desc_addr_set()` and `desc_addr_get()` for 32-bit versus 64-bit DMA. RX setup and service live in `ns83820_setup_rx()`, `rx_refill()`, `rx_irq()`, `rx_action()`, and `ns83820_rx_kick()`. TX is handled by `ns83820_hard_start_xmit()`, `do_tx_done()`, `ns83820_tx_timeout()`, and `ns83820_tx_watch()`. Probe and teardown are `ns83820_init_one()` and `ns83820_remove_one()`.

## Control flow
Probe negotiates a 64-bit or 32-bit DMA mask, allocates a netdev and coherent RX/TX descriptor arrays, maps BAR 1, disables interrupts, requests IRQ, allocates a device name under RTNL, resets hardware, runs SRAM/EEPROM BIST and EEPROM load, configures CFG/TXCFG/RXCFG/VRCR/VTCR/PCR/WCSR, reads the MAC from perfect-match memory, sets features, and registers the netdevice. Open initializes RX descriptors and buffers, initializes TX ring links, starts the TX watchdog, and starts the queue. The ISR reads `ISR` and dispatches to `ns83820_do_isr()`, which schedules RX tasklet work, handles TX completions, MIB overflow, PHY changes, RX idle/overrun recovery, and interrupt mask updates. Stop disables interrupts, resets the chip, synchronizes IRQs, cleans RX/TX rings, and deletes the watchdog.

## State and persistence
Persistent hardware inputs include EEPROM-loaded MAC/perfect-match memory, silicon revision, optical transceiver bits, and module parameters `lnksts`, `ihr`, and `reset_phy`. Runtime state is descriptor ownership, SKB arrays, RX idle/empty pointers, TX done/free/intr indices, cached interrupt mask, cached CFG, link state, and software stats. There is no filesystem persistence.

## Dependencies and integration points
The driver integrates with PCI, DMA mapping, netdevice ops, ethtool link settings, tasklets, workqueues, timers, VLAN acceleration when `CONFIG_VLAN_8021Q` is enabled, and standard Ethernet helpers. It directly programs DP83820 registers and optionally uses hardware checksum and VLAN insertion/stripping.

## Risks and edge cases
RX refill and RX tasklet locking is subtle because descriptors are a chain rather than a simple hardware ring. TX supports fragmented SKBs by consuming multiple descriptors; queue stop/wake depends on accurate free-space arithmetic. Link-state polarity is configurable via `lnksts`, and wrong polarity breaks carrier decisions. Optical and copper paths configure duplex/speed differently. Comments document hardware errata around AUTO_1000, 1024-byte DMA bursts, VLAN runt handling, and IP fragment checksum rejection. RX DMA is mapped with `REAL_RX_BUF_SIZE`; unmap sizes and buffer length assumptions should be audited carefully when changing RX buffer constants. Several PHY MII routines are compiled out under `PHY_CODE_IS_FINISHED`.

## Test signals
Useful tests include PCI probe with both 32-bit and 64-bit DMA masks, BIST success/failure logging, RX/TX traffic with fragmented SKBs, TX timeout watchdog behavior, VLAN RX/TX when enabled, checksum offload correctness for TCP/UDP/IP and fragments, multicast/promiscuous filter toggling, optical TBI autonegotiation, copper speed/duplex changes through ethtool, interrupt mitigation parameter coverage, and unload after active traffic. Build tests should cover VLAN and non-VLAN configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/ns83820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.c

## Purpose
`sonic.c` is the shared DP83932/DP83934 SONIC Ethernet controller implementation included by machine-specific wrappers such as `macsonic.c` and `xtsonic.c`. It owns descriptor allocation layout, open/close, TX, interrupt handling, RX buffer turnover, multicast CAM programming, statistics, timeout recovery, and controller initialization, while wrappers provide register access macros and probe/remove logic.

## Important APIs, types, and functions
The file operates on `struct sonic_local` from `sonic.h`. Key functions are `sonic_msg_init()`, `sonic_alloc_descriptors()`, `sonic_open()`, `sonic_close()`, `sonic_tx_timeout()`, `sonic_send_packet()`, `sonic_interrupt()`, `sonic_rx()`, `sonic_get_stats()`, `sonic_multicast_list()`, and `sonic_init()`. It uses wrapper-provided `SONIC_READ()`/`SONIC_WRITE()` and inline descriptor accessors from `sonic.h`.

## Control flow
Wrapper probe allocates a netdev and calls `sonic_alloc_descriptors()`. Open allocates and DMA maps receive SKBs, then calls `sonic_init()`, which resets the controller, initializes RRA/RDA/TDA/CAM areas, loads resource pointers, loads CAM, enables interrupts, and starts RX. TX pads short packets, maps the SKB, appends a descriptor after `eol_tx`, clears the previous EOL, issues `SONIC_CR_TXP`, and stops the netdev queue if the ring becomes full. Interrupt handling loops over masked status bits, acknowledges them, calls `sonic_rx()` for packets, reaps completed TX descriptors, updates error counters, restarts aborted TX when appropriate, and disables interrupts on bus retry. RX hands completed buffers to the stack, allocates replacement buffers, updates the receive resource area, advances descriptor EOL, and clears RBE when safe.

## State and persistence
Runtime state lives in `struct sonic_local`: coherent descriptor page subdivisions, logical DMA addresses, RX/TX SKB arrays, ring indices, `eol_rx`, `eol_tx`, stats, message mask, and lock. Hardware state includes CAM entries, tally counters, command/status registers, and receive resource pointers. No state persists beyond driver lifetime except hardware/firmware-provided MAC setup done by wrappers.

## Dependencies and integration points
The shared core depends on `sonic.h` constants, descriptor helpers, netdevice APIs, DMA mapping APIs, SKB allocation, interrupt context semantics, and wrapper-provided register access. It integrates with the networking stack through wrapper `net_device_ops`.

## Risks and edge cases
This file is included into wrapper translation units, so macro definitions and local variable assumptions are part of the ABI. SONIC descriptors and buffers must remain within addressing constraints described in `sonic.h`; descriptor EOL manipulation is central to both RX and TX correctness. TX and interrupt paths share descriptor state and rely on `lp->lock`. Multicast CAM loading must not overlap with TXP, so it quiesces TX first. Timeout recovery resets hardware and drops pending TX SKBs rather than resending. RX replacement allocation failure reuses the old buffer and increments drops, which avoids starving the RRA but may hide memory pressure.

## Test signals
Tests should exercise wrapper-driven open/close, RX buffer replacement, TX ring full stop/wake, TX timeout recovery, multicast list changes with small and all-multicast sets, promisc mode, stats counter rollover, bus retry interrupt handling, DMA mapping failure paths, and both 16-bit and 32-bit descriptor modes. Because this file is included by wrappers, build coverage must include each wrapper target rather than compiling `sonic.c` alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.h

## Purpose
`sonic.h` defines the register map, bit fields, descriptor formats, ring sizing, private state, prototypes, and descriptor access helpers for the shared SONIC Ethernet core and its platform wrappers. It encodes the controller's 16-bit versus 32-bit bus modes and the endian-sensitive descriptor layout that `sonic.c` consumes.

## Important APIs, types, and functions
The header defines SONIC register offsets (`SONIC_CMD`, `SONIC_ISR`, `SONIC_RCR`, resource and CAM registers), command/config/status bits, interrupt masks, descriptor offsets for receive resources, receive descriptors, transmit descriptors, and CAM descriptors, ring constants, and `struct sonic_local`. Inline APIs include `sonic_buf_put()`, `sonic_buf_get()`, typed CDA/TDA/RDA/RRA accessors, CAM enable accessors, and receive-resource address/index helpers. It also declares the static functions implemented by `sonic.c`.

## Control flow
The header itself has no runtime control flow, but it controls how runtime code indexes and writes coherent descriptor memory. `SONIC_BUS_SCALE()` changes descriptor spacing between 16-bit and 32-bit bus modes. Wrappers include this header, define `SONIC_READ()`/`SONIC_WRITE()`, then include `sonic.c`, causing these constants and inline helpers to become the compile-time contract for the shared implementation.

## State and persistence
`struct sonic_local` is the main state contract. It tracks DMA bit mode, register offset, descriptor memory and sub-areas, SKB rings, DMA addresses, RX/TX indices, EOL markers, message level, backing device, stats, and lock. The header also embeds hardware sizing choices: 16 receive resources/descriptors, 16 transmit descriptors, 1520-byte default receive buffers, and 16 CAM descriptors.

## Dependencies and integration points
The header depends on Linux netdevice, DMA address, SKB, and stats types through includers. It integrates platform wrappers with shared core code by exposing function prototypes and requiring wrapper-specific register macros. Its descriptor helpers use raw 16-bit access to preserve bus layout and endian expectations.

## Risks and edge cases
Comments warn that descriptor structures are endian and bus-size dependent. Incorrect `dma_bitmode`, `reg_offset`, or bus scaling corrupts descriptor interpretation. The descriptor page must not cross a 64K boundary, which `sonic_alloc_descriptors()` relies on through page-sized coherent allocation. `sonic_rr_entry()` truncates through 16-bit resource addresses, matching SONIC hardware but requiring descriptor memory placement within the expected logical range. Changing ring sizes requires preserving power-of-two masks and descriptor memory layout.

## Test signals
The header is validated indirectly by building and running each SONIC wrapper in 16-bit and 32-bit modes. Useful signals include correct descriptor addresses programmed into RRA/RDA/TDA, successful CAM loading, RX/TX operation on big-endian and little-endian configurations, and absence of descriptor corruption when multicast or timeout paths manipulate EOL bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/sonic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/xtsonic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/xtsonic.c

## Purpose
`xtsonic.c` is the Xtensa XT2000 platform wrapper for the shared SONIC Ethernet core. It probes a memory-mapped onboard SONIC controller, validates the silicon revision, reads the MAC address from CAM initialized by firmware, configures 32-bit SONIC operation, allocates shared descriptors, registers netdevice operations, and binds to a platform driver named `xtsonic`.

## Important APIs, types, and functions
`SONIC_READ()` and `SONIC_WRITE()` access 32-bit memory-mapped registers through `dev->base_addr`. `xtsonic_open()` and `xtsonic_close()` wrap IRQ request/free around `sonic_open()` and `sonic_close()`. `sonic_probe1()` performs MMIO region reservation, silicon revision validation against `known_revisions`, reset/DCR setup, MAC extraction, descriptor allocation, and netdev operation setup. `xtsonic_probe()` obtains platform memory and IRQ resources, allocates the netdev, fills `struct sonic_local`, calls `sonic_probe1()`, initializes messages, and registers the netdev. Removal unregisters and frees descriptors, releases the region, and frees the netdev.

## Control flow
The module platform driver calls `xtsonic_probe()`. Probe requires one memory resource and one IRQ resource, then delegates hardware validation to `sonic_probe1()`. Open requests the IRQ first, then starts shared SONIC initialization. Close stops the shared core and frees the IRQ. `sonic.c` is included after the wrapper's register macros, so all common RX/TX/interrupt/statistics logic is compiled into this wrapper.

## State and persistence
Runtime state is stored in `struct sonic_local`: 32-bit DMA mode, descriptor memory, DMA addresses, rings, stats, and lock. Hardware state comes from the platform resources and SONIC CAM. The code declares external XT board NVRAM helpers but does not use them; MAC state is assumed to be in CAM from the bootloader. There is no disk persistence.

## Dependencies and integration points
The file depends on platform device resources, request/release memory regions, IRQ APIs, DMA coherent allocation, Xtensa IO headers, and the shared SONIC core. It integrates with the netdevice stack through `xtsonic_netdev_ops`.

## Risks and edge cases
The code assumes only 32-bit SONIC operation and a known revision of `0x101`. `sonic_probe1()` reserves the memory region before revision validation; the not-found path returns `-ENODEV` without releasing that region, which is a cleanup risk. MAC extraction assumes firmware initialized CAM entry 0. Register access uses volatile pointer arithmetic on `dev->base_addr`, so resource mapping expectations are architecture-specific. `request_mem_region()` uses a hardcoded `0x100`, while removal releases `SONIC_MEM_SIZE`, currently also `0x100`.

## Test signals
Useful tests include platform resource absence paths, successful probe with revision `0x101`, failure probe with unknown revision and region cleanup auditing, IRQ request failure, descriptor allocation failure, register_netdev failure, RX/TX traffic through shared SONIC code, MAC correctness from CAM, and module unload after open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/natsemi/xtsonic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Kconfig

## Purpose
This Kconfig file defines the Netronome Ethernet driver menu and feature switches for the NFP4000/NFP6000 driver family. It controls whether the `nfp` driver is built and whether optional firmware/application integrations such as TC flower offload, ABM NIC support, IPsec offload, and debugfs/debug checks are compiled.

## Important options
`NET_VENDOR_NETRONOME` gates all Netronome questions and defaults to `y`. `NFP` is a tristate driver option that depends on `PCI_MSI`, compatible VXLAN/TLS settings, and selects `NET_DEVLINK`, `CRC32`, and `DIMLIB`. `NFP_APP_FLOWER` depends on `NFP` and `NET_SWITCHDEV` and defaults to `y`. `NFP_APP_ABM_NIC` also depends on `NFP` and `NET_SWITCHDEV`, defaults to `y`, and builds ABM support into `nfp.ko`. `NFP_NET_IPSEC` depends on `NFP` and `XFRM_OFFLOAD`. `NFP_DEBUG` depends on `NFP`.

## Control flow
Kconfig evaluation first exposes the vendor gate. When enabled, it exposes the base NFP driver and feature booleans. These booleans are then consumed by makefiles and C preprocessor conditionals to include optional object files and code paths.

## State and persistence
The only persistent state is kernel configuration. The selected symbols determine build artifacts and runtime feature availability but do not store runtime driver state.

## Dependencies and integration points
This file integrates with kernel configuration, the Netronome makefiles, devlink support, switchdev/TC offload infrastructure, TLS device offload, XFRM offload, VXLAN support, and debugfs/debug infrastructure.

## Risks and edge cases
Default-y optional features increase build coverage and binary size when dependencies are present. Dependency expressions like `VXLAN || VXLAN=n` and `TLS && TLS_DEVICE || TLS_DEVICE=n` enforce compatibility with built-in/module combinations; changing them can create unresolved symbol or unusable feature combinations. ABM and flower support require matching firmware even when the code is compiled.

## Test signals
Validation is primarily configuration matrix coverage: `NFP=m/y`, optional app booleans on/off, dependency-disabled combinations, allmodconfig/allnoconfig style builds, and runtime checks that devlink, flower, ABM, IPsec, and debug features appear only when configured and supported by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Makefile

## Purpose
This Makefile is the top-level build hook for Netronome Ethernet drivers. It descends into the `nfp/` subdirectory when `CONFIG_NFP` is enabled.

## Important entries
The single functional line is `obj-$(CONFIG_NFP) += nfp/`, which makes the complete Netronome NFP driver subtree conditional on the base Kconfig symbol.

## Control flow
During kbuild, if `CONFIG_NFP` is unset the subtree is skipped. If it is built-in or modular, kbuild enters `netronome/nfp/` and uses that directory's Makefile to assemble `nfp.o`.

## State and persistence
The file carries no runtime state. Build state is determined entirely by `CONFIG_NFP`.

## Dependencies and integration points
It integrates the vendor directory with kbuild and the `netronome/nfp/Makefile`. It depends on the Kconfig symbol defined in the sibling Kconfig file.

## Risks and edge cases
Because the file only gates the subtree, any incorrect dependency handling must be fixed in Kconfig or the nested Makefile. Removing or renaming this entry would silently exclude all NFP objects from builds even if Kconfig enables them.

## Test signals
Useful signals are kbuild inclusion/exclusion checks with `CONFIG_NFP=n/m/y`, verifying that `nfp/` objects are absent when disabled and included in the expected module or built-in image when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/Makefile

## Purpose
This Makefile assembles the monolithic `nfp.o` driver object from core NFP PCI/CPP libraries, datapath implementations, app modules, representor/devlink/netdev code, and optional feature object sets.

## Important entries
`obj-$(CONFIG_NFP) += nfp.o` emits the module or built-in object. `nfp-objs` includes `nfpcore` support, control channel, devlink params, NFD3/NFDK datapaths, app framework, netdev common/control/debugdump/ethtool/main, representors, SR-IOV, XSK, port/shared-buffer, and NIC app code. Conditional blocks add `crypto/tls.o` for `CONFIG_TLS_DEVICE=y`, flower app objects for `CONFIG_NFP_APP_FLOWER=y`, BPF offload objects for `CONFIG_BPF_SYSCALL=y`, ABM objects for `CONFIG_NFP_APP_ABM_NIC=y`, IPsec objects via `nfp-$(CONFIG_NFP_NET_IPSEC)`, debugfs via `nfp-$(CONFIG_NFP_DEBUG)`, and DCB support via `nfp-$(CONFIG_DCB)`.

## Control flow
kbuild expands `nfp-objs` and conditionals based on configuration, then links all selected objects into `nfp.o`. The conditional object layout mirrors runtime app registration: optional flower, BPF, ABM, TLS, IPsec, debug, and DCB features are compiled only when their symbols permit.

## State and persistence
The Makefile has build-time state only. It determines which translation units participate in the final driver and therefore which app types, offloads, and debug paths can exist at runtime.

## Dependencies and integration points
It integrates the NFP core, datapath variants, netdev management, app framework, flower/BPF/ABM/nic apps, crypto offloads, XSK support, debugfs, and DCB modules with kbuild and Kconfig.

## Risks and edge cases
The TLS block checks `CONFIG_TLS_DEVICE` directly rather than `CONFIG_NFP` because the whole file is already gated by `CONFIG_NFP`. Feature object lists must stay synchronized with Kconfig dependencies and source file renames. Objects that define app type symbols must be included whenever runtime firmware/app selection may reference them. Optional paths can bit-rot without config matrix builds.

## Test signals
Test with config matrices enabling/disabling flower, BPF syscall, ABM, IPsec, debug, TLS device, and DCB. Link tests should catch missing objects or unresolved references. Runtime smoke tests should verify expected app registration and absence of feature hooks when their objects are omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/cls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/cls.c

## Purpose
`abm/cls.c` implements TC u32 classifier offload for the NFP Advanced Buffer Management NIC app. It accepts a constrained subset of u32 filters that classify IPv4/IPv6 DSCP class-selector bits into ABM priority bands, keeps a software list of DSCP mappings per ABM link, converts that list into a packed firmware priority map, and registers the TC block callback.

## Important APIs, types, and functions
`struct nfp_abm_u32_match` records a TC handle, target band, mask, value, and list node. `nfp_abm_u32_check_knode()` validates the supported u32 shape. `nfp_abm_find_band_for_prio()` resolves a priority through the mapping list with fallback to `alink->def_band`. `nfp_abm_update_band_map()` repacks all priority-to-band entries and sends them with `nfp_abm_ctrl_prio_map_update()`. `nfp_abm_u32_knode_replace()` adds or updates one mapping after conflict checks. `nfp_abm_u32_knode_delete()` removes one. `nfp_abm_setup_tc_block_cb()` dispatches TC block callbacks. `nfp_abm_setup_cls_block()` registers through `flow_block_cb_setup_simple()`.

## Control flow
TC block setup invokes the callback for classifier events. The callback accepts only `TC_SETUP_CLSU32`, chain 0, and IPv4/IPv6 protocols. New or replacement knodes are validated, DSCP mask/value bits are extracted at protocol-specific offsets, conflicts against existing mappings are rejected, the match is allocated or updated, the packed map is recalculated, qdisc offload state is refreshed, and the map is written to firmware. Delete events remove the match and repack the map.

## State and persistence
Runtime classifier state is the `alink->dscp_map` list and the packed `alink->prio_map` buffer. `alink->has_prio` reflects whether any DSCP mapping exists. The resulting firmware state is persisted only until firmware/driver reset through the vNIC mailbox priority map.

## Dependencies and integration points
The file depends on TC u32 offload structures, flow block callbacks, netlink extack reporting, `struct nfp_repr`, ABM state from `main.h`, qdisc offload refresh in `qdisc.c`, and control mailbox code in `ctrl.c`.

## Risks and edge cases
The supported classifier shape is intentionally narrow: no actions, no links, terminal-only, no variable offsets, no hashing, no mark matching, one key, and only high DSCP class selector bits supported by firmware. On validation or firmware update failure, replacement falls through to delete the existing mapping for that handle, which can remove prior offload state. Conflict detection is mask-overlap based and must stay consistent with firmware match semantics. The map packing depends on power-of-two `num_bands` and `num_prios` validated in control init.

## Test signals
Useful tests include TC u32 add/replace/delete for IPv4 and IPv6 DSCP masks, invalid actions/links/nonterminal/multiple-key cases with extack messages, conflicting filters, classid out of range, firmware mailbox failures, qdisc offload status transitions when the first/last mapping is added or removed, and map packing correctness across one-band and multi-band firmware descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/cls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/ctrl.c

## Purpose
`abm/ctrl.c` is the firmware control and telemetry layer for the NFP ABM NIC app. It discovers firmware runtime symbols, validates ABM capabilities, writes RED queue thresholds/actions, reads queue and queue-manager statistics, enables/disables ABM queue management, and updates per-vNIC DSCP priority maps through the NFP net mailbox.

## Important APIs, types, and functions
Symbol names such as `_abi_pci_dscp_num_prio_%u`, `_abi_nfd_out_q_lvls_%u%s`, and `_abi_nfdqm%u_stats%s` define the firmware ABI. `nfp_abm_ctrl_find_addrs()` discovers capabilities and runtime symbols. `__nfp_abm_ctrl_set_q_lvl()` and `nfp_abm_ctrl_set_q_lvl()` write RED thresholds. `__nfp_abm_ctrl_set_q_act()` and `nfp_abm_ctrl_set_q_act()` write actions. `nfp_abm_ctrl_read_q_stats()` and `nfp_abm_ctrl_read_q_xstats()` read basic and extended stats. `nfp_abm_ctrl_qm_enable()`/`disable()` send PF mailbox commands. `nfp_abm_ctrl_prio_map_update()` writes a packed priority map into the vNIC mailbox and triggers reconfiguration.

## Control flow
ABM app init calls `nfp_abm_ctrl_find_addrs()`, which derives the PCIe PF id, reads optional firmware values for RED support, number of bands/priorities, and action mask, computes priority map size and DSCP mask, validates power-of-two geometry, and locates queue level/stat symbols if RED is supported. Per-vNIC allocation calls `nfp_abm_ctrl_read_params()` to derive `queue_base` and validate mailbox size. Qdisc/classifier paths then call threshold/action/map update helpers. Stats paths compute queue ids from band, queue base, and queue number and read firmware symbols or vNIC RX stats depending on priority support.

## State and persistence
The control layer caches firmware capability values in `struct nfp_abm`: `red_support`, `num_prios`, `num_bands`, `action_mask`, `prio_map_len`, `dscp_mask`, and runtime-symbol pointers. It also caches current thresholds/actions and clears `threshold_undef` when levels are set. Hardware/firmware state is updated through runtime-symbol writes and mailbox commands; it is not persistent across firmware reset.

## Dependencies and integration points
This file depends on NFP CPP access, runtime symbol lookup/read/write APIs, PF optional symbol reads, NFP ABI mailbox constants, `struct nfp_net` mailbox helpers, and ABM data structures in `main.h`. It is used by ABM qdisc, classifier, vNIC init, stats, and eswitch mode code.

## Risks and edge cases
Firmware ABI names and exact symbol sizes are strict; mismatches fail init or RED support. Queue id calculation combines band with `NFP_NET_MAX_RX_RINGS` and per-vNIC `queue_base`, so queue geometry changes must match firmware. `nfp_abm_ctrl_stat_basic()` reads normal vNIC stats when there is no priority split, but runtime symbols when per-band stats exist. Optional firmware symbols default some values, so unsupported firmware must be distinguished from invalid geometry. Mailbox size validation is required before priority map updates.

## Test signals
Tests should cover firmware with and without RED support, one-band and multi-band configurations, invalid non-power-of-two capabilities, missing or wrong-sized runtime symbols, threshold/action no-op caching, mailbox priority map writes and failures, stat reads for per-band and non-per-band modes, QM enable/disable mailbox commands, and vNIC queue-base calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.c

## Purpose
`abm/main.c` registers and coordinates the NFP Advanced Buffer Management NIC app. It owns app-level initialization/cleanup, devlink eswitch mode transitions, representor creation/removal, per-vNIC ABM link allocation, persistent MAC assignment, queue-manager reset, ABM stats exposure, TC setup dispatch, and the `app_abm` type definition.

## Important APIs, types, and functions
`nfp_abm_portid()` encodes representor type and id into an ABM port id. `nfp_abm_setup_tc()` dispatches TC root/qdisc/block setup to ABM qdisc and classifier helpers. `nfp_abm_repr_get()`, `nfp_abm_spawn_repr()`, and `nfp_abm_kill_repr()` manage representor lookup and lifetime. Eswitch functions are `nfp_abm_eswitch_mode_get()`, `nfp_abm_eswitch_set_legacy()`, `nfp_abm_eswitch_set_switchdev()`, and `nfp_abm_eswitch_mode_set()`. Per-vNIC lifecycle is handled by `nfp_abm_vnic_alloc()`, `nfp_abm_vnic_free()`, and `nfp_abm_vnic_init()`. App lifecycle is `nfp_abm_init()` and `nfp_abm_clean()`.

## Control flow
App init validates ETH table and MAC stats availability, allocates `struct nfp_abm`, discovers firmware control addresses, allocates threshold/action state, resets firmware queue levels/actions, disables QM, and allocates representor tables for physical and PF representors. Each vNIC allocation creates an `nfp_abm_link`, reads firmware parameters, allocates a priority map, configures the physical MAC as up, keeps dst cache entries, assigns a persistent MAC from NSP hwinfo or random fallback, and initializes qdisc tracking. Switchdev mode enables QM and spawns physical plus PF representors for each vNIC; legacy mode kills all representors and disables QM. Cleanup forces legacy mode, frees representor tables and app state.

## State and persistence
`struct nfp_abm` persists for the app lifetime and stores firmware capabilities, threshold/action arrays, representor mode, and symbol pointers. Each `struct nfp_abm_link` is attached to `nn->app_priv` and stores vNIC id, queue base, total queues, priority map, DSCP mappings, default band, qdisc tree, and stats timing. Persistent MAC lookup uses NSP hardware info keys like `eth%u.mac.pf%u`; if unavailable, runtime random MAC addresses are assigned.

## Dependencies and integration points
The file integrates with the NFP app framework, PF/vNIC lists, NSP/hwinfo, NFP port and representor infrastructure, RCU-protected representor arrays, rtnl locking, devlink eswitch mode APIs, TC qdisc/classifier setup, ABM control helpers, and ethtool stats hooks.

## Risks and edge cases
Switchdev transition has multi-step failure cleanup: if any representor spawn fails, all spawned representors are killed and QM is disabled. RCU and RTNL ordering around representor arrays must remain correct. `nfp_abm_vnic_set_mac()` checks `if (id > pf->eth_tbl->count)`, which permits `id == count` even though array indexing uses `ports[id]`; this boundary deserves scrutiny. Init assumes `max_data_vnics` equals ETH table count. Firmware RED support gates switchdev mode. Qdisc radix tree must be empty on vNIC free.

## Test signals
Useful tests include app init with missing ETH table, mismatched vNIC/ETH counts, missing MAC stats, firmware discovery failure, legacy-to-switchdev and switchdev-to-legacy devlink transitions, representor spawn failure unwinds, vNIC alloc/free/init, NSP MAC lookup success/failure/parse failure, ABM port stats string/count/value exposure, TC setup dispatch for root/MQ/RED/GRED/block, and cleanup with active qdisc/classifier state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.c -->
