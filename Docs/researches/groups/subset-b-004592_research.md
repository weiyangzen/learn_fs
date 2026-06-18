# Research: subset-b-004592

This grouped report covers NXP LPC Ethernet, the OPEN Alliance TC6 MAC-PHY SPI helper, OKI/LAPIS PCH GBE configuration and driver files, and PA Semi Ethernet build glue. Each source file section is delimited for reconciliation into the mapped `Docs/researches/<source_path>_research.md` output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/nxp/lpc_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/nxp/lpc_eth.c

## Purpose
This is the platform netdev driver for the NXP LPC32xx Ethernet MAC. It binds the `nxp,lpc-eth` OF device, configures RMII or MII mode, allocates a fixed coherent DMA area for descriptor/status rings and packet buffers, registers an MDIO bus and phylib PHY, and exposes a single-queue Ethernet device with NAPI, multicast filtering, ethtool link settings, suspend/resume, and basic MAC address management.

## Important APIs, Types, And Functions
`struct netdata_local` is the driver-private state: platform/netdev handles, MMIO base, clock, MDIO bus, optional `phy_node`, coherent DMA base, TX/RX descriptor/status pointers, ring counters, cached link/speed/duplex, spinlock, and NAPI object. Register helpers are macros over the LPC MAC register layout. Lifecycle entry points are `lpc_eth_drv_probe()`, `lpc_eth_drv_remove()`, `lpc_eth_open()`, `lpc_eth_close()`, `lpc_eth_drv_suspend()`, and `lpc_eth_drv_resume()`. Data path functions are `lpc_eth_hard_start_xmit()`, `__lpc_handle_xmit()`, `__lpc_handle_recv()`, `lpc_eth_poll()`, and `__lpc_eth_interrupt()`. PHY/MDIO functions include `lpc_mii_init()`, `lpc_mii_probe()`, `lpc_mdio_read()`, `lpc_mdio_write()`, and `lpc_handle_link_change()`.

## Control Flow
Probe selects the SoC interface mode from `phy-mode`, obtains memory/IRQ/clock resources, maps registers, requests the IRQ, allocates DMA memory from optional LPC32xx IRAM or coherent SDRAM, reads or generates the MAC address, shuts the MAC down for idle power, resets MII management, initializes NAPI, registers the netdev, and then registers/probes the MDIO bus. Opening enables the clock, resumes the PHY, resets and initializes the MAC and descriptor rings, starts phylib, starts the queue, and enables NAPI. Interrupts clear and mask MAC interrupt status, schedule NAPI, and the poll routine handles TX completions then RX packets before re-enabling interrupts. Transmit copies skb data into a preallocated TX buffer, programs one descriptor, advances the hardware produce index, and frees the skb. Receive copies completed RX buffers into fresh skbs, updates stats, advances the consume index, and passes packets with `netif_receive_skb()`.

## State And Persistence
All state is runtime-only. Hardware state lives in MAC registers, PHY registers, descriptor/status rings, and coherent DMA buffers. The driver persists no settings to disk or NVM. Link state is cached in `netdata_local` and reprogrammed into MAC duplex/speed registers when phylib reports a change. Optional IRAM allocation is platform-owned and not freed by `dma_free_coherent()`.

## Dependencies And Integration Points
The driver depends on platform/OF probing, `lpc32xx_set_phy_interface_mode()`, optional `lpc32xx_return_iram()`, Linux clock APIs, phylib, MDIO, NAPI, netdevice operations, coherent DMA, and ethtool phylib helpers. Device tree properties include `phy-mode`, `use-iram`, optional `phy-handle`, and an optional `mdio` child.

## Risks And Edge Cases
TX and RX paths copy packets through fixed-size DMA buffers, so jumbo frames are unsupported and oversized skb assumptions are risky. `__lpc_eth_init()` uses `tmp &= ~LPC_COMMAND_RXENABLE | LPC_COMMAND_TXENABLE`, whose precedence leaves TX enable set while clearing RX; changing this area needs care. IRQ is requested before netdev registration and before `ndev->name` is final. `of_phy_find_device()` returns a referenced PHY device, but the path immediately reconnects by name. MDIO polling can busy-wait up to 100 ms. Suspend/resume directly resets hardware around clock changes and must preserve phylib/netdev ordering.

## Test Signals
Good signals are successful OF probe, IRQ request, clock enable/disable, MDIO bus registration, PHY attach, valid MAC fallback from hardware/DT/random, link-up/down phylib messages, TX/RX traffic with queue wakeups, multicast/promiscuous filter behavior, suspend/resume with no stuck MDC clock, and unload with no IRQ, DMA, or MDIO lifetime warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/nxp/lpc_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oa_tc6.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oa_tc6.c

## Purpose
This file implements the reusable OPEN Alliance TC6 10BASE-T1x MAC-PHY serial interface library. It provides SPI control register access, direct PHY register access through an MDIO bus, MAC-PHY reset/configuration, an IRQ-driven SPI data thread, TX chunking, RX chunk reassembly, and exported APIs for concrete MAC-PHY netdev drivers.

## Important APIs, Types, And Functions
`struct oa_tc6` stores SPI/netdev/PHY/MDIO handles, control and data SPI buffers, locks, pending/ongoing TX skbs, RX reassembly skb, kthread and waitqueue state, TX credits, RX chunks available, and interrupt/error flags. Exported APIs are `oa_tc6_init()`, `oa_tc6_exit()`, `oa_tc6_start_xmit()`, `oa_tc6_read_register(s)()`, `oa_tc6_write_register(s)()`, and `oa_tc6_zero_align_receive_frame_enable()`. Internal control helpers build odd-parity TC6 headers and verify echoed replies. Data helpers parse footers, process extended status, reassemble RX frames across 64-byte chunks, and split a linearized TX skb into chunk payloads.

## Control Flow
Initialization allocates `oa_tc6`, configures SPI realtime scheduling, allocates control/data buffers, performs a MAC-PHY software reset, unmasks MAC-PHY error interrupts, registers an MDIO bus, attaches the internal PHY, enables config synchronization, reads initial TX credit/RX chunk status, starts a FIFO-scheduled SPI kthread, requests the MAC-PHY IRQ, and kicks one empty data transfer to clear reset-complete IRQ state. Control register operations are serialized by `spi_ctrl_lock`. TX accepts at most one waiting skb; the kthread wakes on IRQs or TX availability, fills SPI chunks according to TX credits, adds empty chunks when RX data must be clocked out, performs `spi_sync()`, and processes received chunk footers/payloads. Fatal footer/status errors stop the kthread by returning an error.

## State And Persistence
State is in memory and MAC-PHY registers only. TX flow control is `tx_credits` plus `waiting_tx_skb` and `ongoing_tx_skb`; RX flow is `rx_chunks_available`, `rx_skb`, and `rx_buf_overflow`. Register writes configure reset, interrupt masks, configuration sync, zero-align receive frames, and PHY MMD/C22 registers. No persistent storage exists.

## Dependencies And Integration Points
The library depends on SPI, kthreads, waitqueues, phylib, MDIO, netdevice stats, `ptp_classify` consumers indirectly through callers, and the public `<linux/oa_tc6.h>` interface. Concrete SPI MAC-PHY drivers call `oa_tc6_init()`, wire their `ndo_start_xmit` to `oa_tc6_start_xmit()`, and call `oa_tc6_exit()` during teardown.

## Risks And Edge Cases
Only one waiting TX skb is queued, so backpressure relies on `NETDEV_TX_BUSY` and queue stopping. TX skbs are linearized, which can be expensive or fail under memory pressure. RX reassembly assumes footer offsets and start/end markers are well-formed; malformed stream handling currently treats header, loss-of-frame, config-unsync, and RXD-header-bad errors as non-recoverable. `oa_tc6_mdiobus_read()` stores a signed error in a `bool ret`, which collapses negative errors to true before returning. `oa_tc6_exit()` disconnects PHY before stopping the thread, so users must ensure no concurrent data work depends on PHY state.

## Test Signals
Useful tests include SPI control read/write echo validation, reset-complete polling, MDIO C22/C45 register access, PHY attach, IRQ wakeups with empty chunks, TX credit exhaustion and queue restart, RX frames spanning one or many chunks, RX buffer overflow recovery, zero-align enablement, and error-footer paths that report and stop cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oa_tc6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Kconfig

## Purpose
This Kconfig file introduces the OKI Semiconductor Ethernet vendor menu.

## Important APIs, Types, And Functions
It defines `NET_VENDOR_OKI` as a boolean vendor selector, defaults it to `y`, depends on `PCI`, and sources `drivers/net/ethernet/oki-semi/pch_gbe/Kconfig` when enabled.

## Control Flow
During kernel configuration, disabling `NET_VENDOR_OKI` hides the OKI-specific driver prompts without directly changing object builds outside this subtree. Enabling it exposes the PCH GBE option.

## State And Persistence
The only state is generated kernel configuration. There is no runtime state.

## Dependencies And Integration Points
It integrates with the top-level Ethernet vendor menu and gates the PCH GBE Kconfig. The dependency on PCI reflects that the included driver is PCI based.

## Risks And Edge Cases
Because the vendor option defaults to `y`, the PCH GBE prompt remains visible on PCI-capable configurations unless explicitly hidden. Removing or changing the `source` path would make the driver unreachable from menuconfig.

## Test Signals
`make menuconfig`/`oldconfig` should show OKI devices under Ethernet vendors when PCI is available, and should expose `PCH_GBE` only inside this menu.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Makefile

## Purpose
This Makefile connects the OKI vendor directory to the PCH GBE module directory.

## Important APIs, Types, And Functions
The single build rule is `obj-$(CONFIG_PCH_GBE) += pch_gbe/`.

## Control Flow
When `CONFIG_PCH_GBE` is enabled as built-in or module, kbuild descends into `oki-semi/pch_gbe/` and uses that directory's Makefile to build the module objects.

## State And Persistence
No runtime state exists. The file only affects build graph generation.

## Dependencies And Integration Points
It depends on `CONFIG_PCH_GBE` from the nested Kconfig and integrates with the parent Ethernet make hierarchy.

## Risks And Edge Cases
The directory is not entered for vendor selection alone; it is entered only when the concrete driver symbol is enabled. A path typo would silently drop the driver from builds.

## Test Signals
Building with `CONFIG_PCH_GBE=m` should produce the `pch_gbe` module from the nested directory; disabling it should skip the directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Kconfig

## Purpose
This Kconfig file defines the EG20T/ML7223/ML7831 PCH Gigabit Ethernet driver option.

## Important APIs, Types, And Functions
`PCH_GBE` is a tristate symbol titled `OKI SEMICONDUCTOR IOH(ML7223/ML7831) GbE`. It depends on PCI, either MIPS_GENERIC, X86_32, or COMPILE_TEST, and `PTP_1588_CLOCK`. It selects `MII`, `PTP_1588_CLOCK_PCH`, and `NET_PTP_CLASSIFY`.

## Control Flow
When selected, the driver can be built in or as a module and the nested Makefile builds the multi-object `pch_gbe` driver.

## State And Persistence
The file only contributes kernel configuration state.

## Dependencies And Integration Points
The PTP selections match the driver's hardware timestamp code, which calls PCH PTP helper APIs and uses packet classification. `MII` is required for generic MII ioctl and ethtool link helpers.

## Risks And Edge Cases
The hard dependency on `PTP_1588_CLOCK` prevents building a non-PTP variant even if timestamping is not used at runtime. Architecture gating limits normal visibility to historical platforms, with `COMPILE_TEST` preserving broader build coverage.

## Test Signals
Kconfig resolution should select the MII/PTP helper symbols. Compile tests should cover the driver on non-target architectures only when `COMPILE_TEST` and PTP support are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Makefile

## Purpose
This Makefile defines the object composition of the PCH GBE driver.

## Important APIs, Types, And Functions
It builds `pch_gbe.o` for `CONFIG_PCH_GBE` and composes it from `pch_gbe_phy.o`, `pch_gbe_ethtool.o`, `pch_gbe_param.o`, and `pch_gbe_main.o`.

## Control Flow
kbuild links the listed objects into a single built-in object or module depending on the tristate setting.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
The object order links PHY helpers, ethtool support, module parameter validation, and the PCI/netdev core into one driver module.

## Risks And Edge Cases
Adding exported internal functions requires ensuring their defining object remains part of `pch_gbe-y`. Missing one of these objects would break probe, ethtool registration, PHY access, or option handling at link time.

## Test Signals
`CONFIG_PCH_GBE=y/m` should compile one `pch_gbe` target containing all four implementation objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe.h

## Purpose
This header is the shared private interface for the OKI/LAPIS/Intel EG20T PCH Gigabit Ethernet driver. It defines the MMIO register layout, bit masks, descriptor formats, ring structures, hardware/MAC/PHY state, statistics, platform quirk data, and cross-file prototypes.

## Important APIs, Types, And Functions
Key types are `struct pch_gbe_regs`, `struct pch_gbe_rx_desc`, `struct pch_gbe_tx_desc`, `struct pch_gbe_buffer`, `struct pch_gbe_tx_ring`, `struct pch_gbe_rx_ring`, `struct pch_gbe_hw_stats`, `struct pch_gbe_hw`, `struct pch_gbe_privdata`, and `struct pch_gbe_adapter`. Important constants cover interrupt bits, MAC mode/reset, TCP/IP accelerator controls, RX/TX FIFO thresholds, descriptor limits and multiples, flow-control modes, RGMII rates, WOL bits, and checksum status bits. The header declares internal entry points implemented by main, PHY, ethtool, and parameter files.

## Control Flow
The header enables `pch_gbe_main.c` to own PCI/netdev lifecycle while delegating PHY operations to `pch_gbe_phy.c`, ethtool operations to `pch_gbe_ethtool.c`, and module option validation to `pch_gbe_param.c`. The adapter contains the runtime object graph that all code paths share: PCI device, netdev, MMIO registers, rings, NAPI, timer, reset work, MII info, PTP device, stats, and quirk data.

## State And Persistence
No storage is allocated in the header, but it defines all persistent-in-memory state for the driver. Hardware-visible state is represented by descriptors, DMA addresses, MAC/PHY configuration, WOL masks, timestamp controls, and feature bits. No disk persistence is modeled.

## Dependencies And Integration Points
It includes PCI, netdevice, etherdevice, ethtool, MII, vmalloc, and IP/TCP/UDP headers. It integrates with PCH PTP support, Linux DMA APIs, ethtool stats, generic MII ioctls, and module parameter validation.

## Risks And Edge Cases
The register struct is an MMIO ABI and field ordering must match hardware exactly. Descriptor and ring count constants require multiples of eight. DMA address fields in descriptors are 32-bit, while probe tries a 64-bit mask first; platform behavior must ensure usable addresses. Several stats are 32-bit and can wrap on long-lived busy interfaces.

## Test Signals
Compile coverage should catch cross-file prototype drift. Runtime validation includes register dump sanity via ethtool, descriptor ring setup, interrupt status decoding, MII access, WOL programming, checksum offload status, and PTP timestamp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_ethtool.c

## Purpose
This file supplies PCH GBE ethtool operations for driver identity, register dumps, WOL, autonegotiation, ring sizing, pause flow control, link settings, and driver statistics.

## Important APIs, Types, And Functions
`pch_gbe_ethtool_ops` wires callbacks for drvinfo, regs, WOL, nway reset, link, ringparam, pauseparam, strings/stats, and link ksettings. `pch_gbe_gstrings_stats[]` maps `struct pch_gbe_hw_stats` fields to ethtool statistic names. `pch_gbe_set_ethtool_ops()` installs the operation table. Ring resizing uses `pch_gbe_setup_rx_resources()`, `pch_gbe_setup_tx_resources()`, `pch_gbe_free_rx_resources()`, `pch_gbe_free_tx_resources()`, `pch_gbe_down()`, and `pch_gbe_up()`.

## Control Flow
Link-setting changes reset the PHY through MII helpers, update cached MAC/PHY autoneg values, and either restart the running device or reset inactive hardware. Ring changes optionally bring a running device down, allocate replacement rings, configure resources, free old rings, and bring the device back up. Pause changes update cached flow-control mode and either restart autoneg or program MAC flow control directly. Stats reads first call `pch_gbe_update_stats()` then copy configured fields by offset.

## State And Persistence
Ethtool changes mutate in-memory adapter state, MAC/PHY registers, WOL event bits, ring sizes, and netdev features. There is no persistence across module unload or reboot unless firmware/platform preserves hardware defaults.

## Dependencies And Integration Points
The file depends on generic MII ethtool helpers, PCI identity, register MMIO from `struct pch_gbe_regs`, PHY MIIM helpers, and the main driver's up/down/resource functions.

## Risks And Edge Cases
`pch_gbe_set_ringparam()` clamps TX pending using RX min/max constants rather than TX min/max, currently equivalent values but fragile if constants diverge. Live ring replacement has multiple rollback paths and must preserve old rings on allocation failure. Register dumps read all MAC registers by linear MMIO offset and all 32 PHY registers, so bad hardware state can make diagnostics slow or noisy. WOL settings are only cached until suspend/shutdown programs hardware.

## Test Signals
Use `ethtool -i`, `-d`, `-S`, `-g/-G`, `-a/-A`, `-s`, and `-s wol` on stopped and running devices. Validate failure rollback for ring allocation, link restart behavior, pause programming, WOL suspend wake, and stable stats output under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_main.c

## Purpose
This is the primary PCI and netdev implementation for the EG20T/OKI/LAPIS PCH Gigabit Ethernet driver. It owns PCI probe/remove, netdev open/stop/transmit, NAPI, IRQs, descriptor rings, MAC/PHY reset and programming, watchdog link maintenance, WOL suspend/shutdown, PCI error recovery, multicast filtering, MTU/features, and PCH PTP hardware timestamp integration.

## Important APIs, Types, And Functions
PCI/module entry points are `pch_gbe_probe()`, `pch_gbe_remove()`, `pch_gbe_shutdown()`, `pch_gbe_pcidev_id[]`, `pch_gbe_driver`, and PCI error handlers. Netdev operations are installed through `pch_gbe_netdev_ops`. Core lifecycle functions are `pch_gbe_sw_init()`, `pch_gbe_reset()`, `pch_gbe_up()`, `pch_gbe_down()`, `pch_gbe_open()`, and `pch_gbe_stop()`. Data path functions include `pch_gbe_xmit_frame()`, `pch_gbe_tx_queue()`, `pch_gbe_intr()`, `pch_gbe_napi_poll()`, `pch_gbe_clean_tx()`, `pch_gbe_clean_rx()`, and RX/TX resource allocation/free helpers. Timestamp APIs are `pch_gbe_hwtstamp_set()`, `pch_gbe_hwtstamp_get()`, `pch_tx_timestamp()`, and `pch_rx_timestamp()`.

## Control Flow
Probe enables the PCI device with managed MMIO mapping, sets a DMA mask, allocates the netdev, applies optional platform quirks, finds the companion PTP PCI function, installs netdev/NAPI/ethtool callbacks, resets the MAC, initializes software state and PHY/MII state, reads the MAC address, validates module options, resets hardware with those settings, registers the netdev, disables carrier, and optionally disables PHY hibernate. Open allocates coherent descriptor rings, powers the PHY, configures TX/RX registers, requests one IRQ vector, allocates a coherent RX buffer pool, preallocates TX skbs, fills RX descriptors, enables DMA/MAC RX, starts the watchdog, enables NAPI/IRQs, and starts the queue. Interrupts mask RX/TX completion sources and schedule NAPI. NAPI cleans RX packets into GRO, cleans TX completions, re-enables interrupts when work is below budget, and recovers RX DMA after FIFO stop. Stop/down reverses this by disabling NAPI/IRQs, deleting the watchdog timer, stopping carrier/queue, cleaning rings, and freeing the RX pool; stop then frees descriptor resources and may power down the PHY.

## State And Persistence
Runtime state lives in `struct pch_gbe_adapter`, descriptor rings, coherent RX pool, preallocated TX skbs, hardware registers, PHY registers, watchdog timer, reset work, stats, WOL flags, and timestamp enable fields. No file or NVM persistence is performed. Suspend/shutdown can program WOL hardware state and put PCI into low power state.

## Dependencies And Integration Points
The file depends on PCI, netdevice, NAPI, DMA mapping/coherent memory, generic MII helpers, PHY helper functions in `pch_gbe_phy.c`, ethtool setup, PCH PTP helper APIs from `ptp_pch`, GPIO lookup quirks for MinnowBoard, Linux PM, and PCI AER recovery.

## Risks And Edge Cases
TX uses preallocated internal skbs and copies/offsets packet data with two bytes of padding before DMA mapping, so skb allocation failures in `pch_gbe_alloc_tx_buffers()` are risky because returned skbs are not checked before `skb_reserve()`. RX allocates both per-packet skbs and a large coherent RX pool; cleanup ordering must avoid DMA leaks. `pch_gbe_request_irq()` does not free IRQ vectors if `request_irq()` fails. PTP code assumes the companion PCI function exists before timestamp operations. Link is maintained by timer polling rather than PHY interrupts. Error and suspend paths have many hardware state transitions and must coordinate NAPI, IRQ, timer, PHY power, and WOL programming.

## Test Signals
Signals include successful probe on Intel EG20T/ROHM IDs, valid or rejected MAC handling, open/stop with no DMA leaks, RX/TX traffic and checksum offload, queue stop/wake under TX pressure, RX FIFO overrun recovery, MTU changes through jumbo ranges, multicast/promiscuous filtering, PTP tx/rx timestamp ioctls, WOL suspend/resume, PCI error recovery, MinnowBoard GPIO reset quirk, and unload after reset work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_param.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_param.c

## Purpose
This file implements module parameter parsing and validation for PCH GBE descriptor counts, speed, duplex, autonegotiation advertisement, flow control, and checksum offload defaults.

## Important APIs, Types, And Functions
Module parameters are `TxDescriptors`, `RxDescriptors`, `Speed`, `Duplex`, `AutoNeg`, `FlowControl`, `XsumRX`, and `XsumTX`. `struct pch_gbe_option` describes enable/range/list validation. `pch_gbe_validate_option()` applies defaults and rejects invalid values. `pch_gbe_check_copper_options()` derives MAC/PHY link policy. `pch_gbe_check_options()` is the exported setup hook called from probe after rings exist.

## Control Flow
Unset options become defaults. Descriptor counts are range-checked and rounded to required multiples. RX/TX checksum options clear netdev feature bits when disabled. Flow control selects one of the driver flow-control modes. Speed/duplex/autoneg combinations either enable autoneg with constrained advertisements or force 10/100 speeds; 1000 half-duplex is rejected into 1000 full-duplex autoneg behavior.

## State And Persistence
The file mutates adapter ring counts, `netdev->features`, `hw->mac.fc`, `hw->mac.autoneg`, `hw->mac.fc_autoneg`, `hw->mac.link_speed`, `hw->mac.link_duplex`, and `hw->phy.autoneg_advertised`. Values are module-load/runtime state only.

## Dependencies And Integration Points
It depends on constants and structures from `pch_gbe.h`, module parameter infrastructure, netdev feature bits, MII speed/duplex constants, and probe ordering in `pch_gbe_main.c`.

## Risks And Edge Cases
The options are global module parameters, not per-device values, so multiple adapters share one configuration. Invalid values are silently defaulted after debug logging, which may be invisible unless debug is enabled. Forced link policy must remain consistent with later ethtool changes and PHY initialization. Checksum feature changes only clear initial features; later ethtool feature changes are handled elsewhere.

## Test Signals
Load the module with boundary and invalid parameter values, verify rounded ring counts via ethtool, confirm advertised/forced link modes with `ethtool`, and check RX/TX checksum feature bits with `ethtool -k`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.c

## Purpose
This file implements PCH GBE PHY access and PHY-specific setup over the MAC MIIM interface. It handles standard PHY ID/register access, reset/power state transitions, initial MII ethtool configuration, RGMII-related reset, and AR803x-specific TX clock delay and hibernation quirks.

## Important APIs, Types, And Functions
Exported functions are `pch_gbe_phy_get_id()`, `pch_gbe_phy_read_reg_miic()`, `pch_gbe_phy_write_reg_miic()`, `pch_gbe_phy_hw_reset()`, `pch_gbe_phy_power_up()`, `pch_gbe_phy_power_down()`, `pch_gbe_phy_set_rgmii()`, `pch_gbe_phy_init_setting()`, and `pch_gbe_phy_disable_hibernate()`. Internal `pch_gbe_phy_sw_reset()` sets the MII reset bit, and `pch_gbe_phy_tx_clk_delay()` handles AR803x debug-register programming.

## Control Flow
Read/write helpers validate a 5-bit PHY register offset and call `pch_gbe_mac_ctrl_miim()`. PHY ID reads combine ID1 and ID2 into OUI/model/revision fields. Hardware reset writes default control, advertisement, next-page, 1000T, and PHY-specific control values. Initial settings build an `ethtool_cmd` from cached MAC/PHY policy, reset the BMCR, apply MII settings, software-reset the PHY, asserts CRS on TX, and optionally programs platform-specific TX delay. Power up/down only toggles BMCR power-down state.

## State And Persistence
The file updates `hw->phy.id`, `hw->phy.revision`, and PHY registers. Changes persist only in the PHY until reset or power cycle unless strap defaults reapply.

## Dependencies And Integration Points
It depends on `pch_gbe_mac_ctrl_miim()` in the main file, `adapter->mii` generic MII helpers, and platform quirk flags carried in `struct pch_gbe_privdata`.

## Risks And Edge Cases
`pch_gbe_mac_ctrl_miim()` returns zero on timeout, so read helpers cannot distinguish a timeout from a valid zero value. AR803x-specific debug access returns `-EINVAL` for unknown PHY IDs when quirks are requested. `pch_gbe_phy_hw_reset()` writes defaults without polling reset completion. Power-down comments mention WOL/AMT constraints, but the function itself does not check WOL.

## Test Signals
Validate PHY discovery, `ethtool` link mode changes, power down/up across interface stop/open, AR803x TX delay on MinnowBoard, hibernate-disable quirk, MIIM timeout logging, and correct PHY register dumps via ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.h

## Purpose
This header exposes the private PHY helper interface for the PCH GBE driver.

## Important APIs, Types, And Functions
It defines `PCH_GBE_PHY_REGS_LEN` as 32 and `PCH_GBE_PHY_RESET_DELAY_US` as 10, and declares PHY ID, MIIM read/write, hardware reset, power up/down, RGMII setup, initial settings, and hibernate-disable functions.

## Control Flow
`pch_gbe_main.c` includes this header to initialize, reset, power-manage, and query the PHY during probe, open, stop, suspend/resume, and ethtool operations. `pch_gbe_ethtool.c` uses the register length and MIIM read helper for register dumps.

## State And Persistence
The header defines no storage. Its constants constrain PHY scan/dump length and reset timing.

## Dependencies And Integration Points
It requires `struct pch_gbe_hw` from `pch_gbe.h` to be visible before prototypes are used.

## Risks And Edge Cases
The fixed register length reflects Clause 22 register space. Clause 45-style or vendor extended registers are reached only through implementation-specific debug paths, not through the generic dump length.

## Test Signals
Compile all PCH GBE objects together, verify no prototype drift, and confirm ethtool register dumps include 32 PHY registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Kconfig

## Purpose
This Kconfig file defines the PA Semi Ethernet vendor menu and the on-chip PA Semi 1/10Gbit MAC driver option.

## Important APIs, Types, And Functions
`NET_VENDOR_PASEMI` is a boolean vendor selector defaulting to `y` and depending on `PPC_PASEMI && PCI`. `PASEMI_MAC` is a tristate driver symbol depending on the same platform/PCI requirements and selecting `PHYLIB`.

## Control Flow
When the PA Semi vendor menu is enabled on PA Semi PPC PCI platforms, users can enable the PWRficient on-chip MAC driver as built-in or module.

## State And Persistence
Only generated kernel configuration state is affected.

## Dependencies And Integration Points
The file integrates with the Ethernet vendor menu and with the PA Semi MAC Makefile. `PHYLIB` selection matches the driver's PHY management needs.

## Risks And Edge Cases
The strict `PPC_PASEMI && PCI` dependency means this driver is not normally visible for generic compile testing unless the dependency is changed elsewhere. Disabling the vendor menu hides the concrete driver prompt.

## Test Signals
On a `PPC_PASEMI` PCI configuration, menuconfig should show both the vendor menu and `PASEMI_MAC`; enabling the driver should select phylib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Makefile

## Purpose
This Makefile builds the PA Semi MAC driver from its core and ethtool objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_PASEMI_MAC) += pasemi_mac_driver.o` declares the final target, and `pasemi_mac_driver-objs := pasemi_mac.o pasemi_mac_ethtool.o` lists its components.

## Control Flow
kbuild links core MAC logic and ethtool support into a single object or module according to `CONFIG_PASEMI_MAC`.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
It depends on the Kconfig symbol from the PA Semi Kconfig and participates in the parent Ethernet make hierarchy.

## Risks And Edge Cases
The comment says "A Semi" rather than "PA Semi", a documentation typo only. Link failures will occur if either component object is renamed without updating this file.

## Test Signals
With `CONFIG_PASEMI_MAC=m`, the build should produce `pasemi_mac_driver.ko` containing both core and ethtool object code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/Makefile -->
