# subset-b-004443 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.c

## Purpose
`core.c` is the main IBM PowerPC 4xx on-chip EMAC network driver. It binds Open Firmware platform EMAC nodes to Linux `net_device` instances, wires the EMAC to shared MAL DMA channels and optional ZMII/RGMII/TAH helper blocks, manages PHY or fixed-link setup, and implements the netdev datapath, link polling, MDIO access, ethtool hooks, reset handling, and module registration.

## Important APIs, Types, and Functions
Key exported/internal entry points are the platform-driver lifecycle `emac_probe()`, `emac_remove()`, `emac_init()`, and `emac_exit()`. Netdev operations are split between `emac_netdev_ops` for non-gigabit and `emac_gige_netdev_ops` for gigabit/scatter-gather-capable paths, with `emac_open()`, `emac_close()`, `emac_start_xmit()`, `emac_start_xmit_sg()`, `emac_change_mtu()`, `emac_set_multicast_list()`, `emac_set_mac_address()`, and `emac_tx_timeout()`. MAL integration is through `struct mal_commac_ops` callbacks: `emac_poll_tx()`, `emac_poll_rx()`, `emac_peek_rx()`/`emac_peek_rx_sg()`, and `emac_rxde()`. MDIO is implemented by `__emac_mdio_read()`, `__emac_mdio_write()`, `emac_mdio_read()`, and `emac_mdio_write()`, with optional Linux phylib MDIO bus support in `emac_dt_mdio_probe()` and `emac_dt_phy_connect()`. Hardware setup centers on `emac_reset()`, `emac_configure()`, `emac_reinitialize()`, and `emac_full_tx_reset()`.

## Control Flow
Module init builds a small ordered boot list of EMAC device-tree nodes, registers MAL/ZMII/RGMII/TAH helper drivers, then registers the EMAC platform driver. Probe skips disabled or unused nodes, allocates an Ethernet device, initializes locks and work, parses device-tree properties, maps EMAC registers, waits for phandle dependencies, registers a `mal_commac`, derives descriptor-ring pointers from MAL memory, attaches bridge/helper blocks, initializes PHY state, picks netdev operations, and registers the netdev. Open allocates RX skbs for all RX descriptors, starts PHY polling or fixed carrier, configures EMAC registers, registers with MAL polling, enables MAL TX/RX channels, enables EMAC TX/RX, and wakes the netif queue. TX maps skbs into MAL descriptors, optionally splitting SG/fragments into `MAL_MAX_TX_SIZE` chunks, then kicks EMAC via TMR0. MAL NAPI later calls `emac_poll_tx()` to reclaim completed descriptors. RX NAPI consumes completed descriptors, handles single-buffer and multi-descriptor packets, validates status bits, optionally copies small packets, replenishes descriptors, performs TAH checksum annotation, and passes a list to `netif_receive_skb_list()`.

## State and Persistence
Runtime state lives in `struct emac_instance`, including OF devices, feature flags, PHY/link state, MAL channel numbers, descriptor pointers, skb rings, statistics, work items, and locks. The global `busy_phy_map` prevents duplicate PHY-address probing across EMACs, and `emac_boot_list` serializes early probe ordering. Hardware state is entirely register/DMA based: EMAC MR0/MR1/RMR/TMR/RWMR/STACR, MAL descriptors, bridge registers, and optional PHY registers. There is no disk persistence. Important synchronization includes `link_lock` around link reconfiguration, `mdio_lock` around shared MDIO selection, `netif_tx_lock_bh()`/`netif_addr_lock()` around multicast queue coordination, and spinlocking for statistics and IRQ status updates.

## Dependencies and Integration Points
This file depends on Linux netdev, NAPI via MAL, phylib/OF MDIO, platform-device probing, OF properties and phandles, DMA mapping APIs, PowerPC DCR/SDR register helpers, and the local `core.h`, `emac.h`, `phy.h`, `mal.h`, `zmii.h`, `rgmii.h`, `tah.h`, and `debug.h`. Device-tree properties such as `mal-device`, `mal-tx-channel`, `mal-rx-channel`, `cell-index`, FIFO sizes, `phy-address`, `phy-map`, `phy-handle`, `mdio-device`, and bridge phandles are the main integration contract. Etthtool integration exposes link settings, ring parameters, pause state, private stats, and composite register dumps that include MAL plus optional bridge/TAH state.

## Risks
DMA unmap calls are intentionally omitted for EMAC descriptor traffic based on PPC 4xx assumptions, which is fragile if the DMA API or supported platforms change. Reset and disable paths use tight polling loops and hardware-specific clock workarounds; missing TX clocks or incorrect feature flags can cause probe or link failures. `busy_phy_map` is global rather than per ASIC, so multi-ASIC systems may be over-constrained. The SG TX path estimates descriptor needs and has an undo path, so descriptor accounting regressions can stall queues. Link polling reconfigures hardware under `link_lock`; missed cancellation or races could reconfigure a closing device. Device-tree dependency handling is central and probe-deferral-sensitive.

## Test Signals
Useful test signals include successful probe logs for EMAC/MAL/bridge/PHY discovery, stable interface ordering, open/close cycling, link up/down transitions with speed/duplex/pause changes, MDIO reads through `SIOCGMIIREG`/phylib, `ethtool -S` counter changes, `ethtool -d` composite register dump sizing, TX timeout recovery, MTU changes including jumbo transition, multicast/promiscuous mode transitions, and RX/TX traffic with checksum offload when TAH is present. Device-tree variants for EMAC, EMAC4, EMAC4SYNC, fixed-link, RGMII, ZMII, SGMII/GPCS, and clock-workaround SoCs are high-value coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.h

## Purpose
`core.h` is the private contract for the IBM EMAC core driver. It gathers local EMAC/MAL/PHY/bridge headers, defines descriptor-ring sizing and MTU helpers, declares the central `struct emac_instance`, and documents feature bits and ethtool register-dump layout shared by `core.c` and helper modules.

## Important APIs, Types, and Functions
Inline helpers `emac_rx_size()`, `emac_rx_skb_size()`, and `emac_rx_sync_size()` derive hardware RX buffer sizes from MTU and MAL limits. `struct emac_stats` and `struct emac_error_stats` define the ethtool statistics layout that must stay in lockstep with `emac_stats_keys` in `core.c`. `struct emac_instance` is the driver’s full per-netdev state: EMAC register base, OF devices, MAL linkage, PHY/MDIO state, optional ZMII/RGMII/TAH state, FIFO sizes, descriptor rings, skb arrays, counters, locks, work, and open/reset flags. `emac_has_feature()` gates implementation-specific behavior against compile-time possible features and runtime device-tree/compatible detection. Address hash-table helpers compute XAHT slots/registers/masks and locate IAHT/GAHT register blocks. `struct emac_ethtool_regs_hdr` and `struct emac_ethtool_regs_subhdr` define the composite register dump framing.

## Control Flow
The header does not run control flow itself, but it shapes all control flow in `core.c`: probe fills `struct emac_instance`, open/close mutate descriptor and PHY fields, TX/RX poll paths use descriptor and skb arrays, and ethtool register dumping uses the register-dump header constants. Feature macros such as `EMAC_FTR_EMAC4`, `EMAC_FTR_HAS_TAH`, and clock-workaround flags are tested before reset, link, checksum, bridge, and register-layout decisions.

## State and Persistence
All state is in-memory kernel state or MMIO/DMA references. Ring sizes are compile-time `CONFIG_IBM_EMAC_TXB` and `CONFIG_IBM_EMAC_RXB`, hard-limited to 256 descriptors each. MTU calculations include VLAN-capable L2 overhead and MAL’s 4080-byte RX ceiling. No persistent storage is used.

## Dependencies and Integration Points
The file depends on Linux netdevice, DMA, locking, interrupt, and PowerPC DCR headers, plus local register and helper headers. Its feature masks depend on Kconfig symbols such as `CONFIG_IBM_EMAC_EMAC4`, `CONFIG_IBM_EMAC_TAH`, `CONFIG_IBM_EMAC_ZMII`, `CONFIG_IBM_EMAC_RGMII`, and `CONFIG_IBM_EMAC_NO_FLOW_CTRL`.

## Risks
Statistics layout drift is a concrete risk because `EMAC_ETHTOOL_STATS_COUNT` assumes the concatenated `u64` structures match string keys. Ring-size macros derive from config and are used for descriptor allocation and wrap control, so invalid config or changed descriptor assumptions can corrupt rings. Feature masks combine compile-time and runtime bits; unsupported runtime device-tree properties can produce disabled stubs or `-ENXIO` paths.

## Test Signals
Builds under multiple Kconfig combinations are important: with/without EMAC4, TAH, RGMII, ZMII, and no-flow-control. Runtime test signals are correct ethtool stat counts, valid register dump component framing, successful jumbo MTU RX buffer sizing, and no descriptor wrap/accounting warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/debug.h

## Purpose
`debug.h` centralizes debug-print macros for the IBM EMAC family. It gives EMAC, MAL, ZMII, and RGMII code consistent `KERN_DEBUG` formatting with the OF node included when `CONFIG_IBM_EMAC_DEBUG` is enabled.

## Important APIs, Types, and Functions
`EMAC_DBG(d, name, fmt, arg...)` emits a printk prefixed by the subsystem name and `d->ofdev->dev.of_node`. `DBG`, `MAL_DBG`, `ZMII_DBG`, and `RGMII_DBG` are level-1 debug macros; `DBG2`, `MAL_DBG2`, `ZMII_DBG2`, and `RGMII_DBG2` are level-2 macros. `DBG_LEVEL` is set to `1` when `CONFIG_IBM_EMAC_DEBUG` is enabled and `0` otherwise.

## Control Flow
There is no runtime flow beyond macro expansion. With debug disabled the macros compile to no-ops, so call sites incur no printk behavior. With debug enabled, frequently executed paths such as TX/RX polling and register changes can produce debug logs.

## State and Persistence
The file keeps no state. It relies on the caller’s object exposing `ofdev`, which is true for the EMAC helper instance structs in this driver family.

## Dependencies and Integration Points
It includes `core.h`, which in turn includes many local headers. That creates a broad include dependency for a small macro file and assumes consumers can tolerate the full private EMAC type graph.

## Risks
The no-op macro signatures are inconsistent for `DBG` versus `MAL_DBG` style macros, but existing call sites compile because they match the expected forms. Enabling debug on busy datapath code may flood logs and alter timing. Because the macro dereferences `d->ofdev`, misuse with partially initialized objects can crash.

## Test Signals
Kconfig build coverage with `CONFIG_IBM_EMAC_DEBUG=y` and unset is the main signal. Runtime debug logs should include OF node paths and not appear when debug is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/emac.h

## Purpose
`emac.h` defines the IBM PowerPC 4xx EMAC hardware register layout and bitfields used by `core.c`. It covers common EMAC registers plus EMAC4 and EMAC4SYNC layout variants, mode registers, RX/TX controls, interrupt bits, MDIO/STACR fields, FIFO threshold helpers, and descriptor status bits.

## Important APIs, Types, and Functions
`struct emac_regs` maps the MMIO register block with unions for EMAC4 and EMAC4SYNC differences. Important bit groups include `EMAC_MR0_*` for reset/TX/RX enable/idleness, `EMAC_MR1_*` and `EMAC4_MR1_*` for duplex, flow control, speed, FIFO size, jumbo, and OPB clock control, `EMAC_RMR_*` for receive filtering, `EMAC_ISR_*`/`EMAC4_ISR_*` for interrupt/error status, `EMAC_STACR_*`/`EMACX_STACR_*` for MDIO access, and `EMAC_TX_*`/`EMAC_RX_*` descriptor status masks. Macros `EMAC_TMR1()`, `EMAC4_TMR1()`, `EMAC4_MR1_OBCI()`, and `EMAC_STACR_OPBC()` encode timing/frequency fields.

## Control Flow
The header has no function control flow. `core.c` uses these definitions during reset, configuration, MDIO transactions, multicast filtering, TX descriptor creation/reclamation, RX descriptor validation, and interrupt accounting.

## State and Persistence
The state represented here is hardware state in EMAC registers and MAL descriptor control words. The C struct layout must match the device’s big-endian MMIO layout; accesses are made with `in_be32()`/`out_be32()` by callers. There is no persistent state.

## Dependencies and Integration Points
It includes Linux types and PHY interface definitions. It is tightly coupled to device-tree compatible strings handled in `core.c` because those determine whether EMAC4/EMAC4SYNC register unions and bit interpretations are used.

## Risks
Register-layout drift or wrong compatible matching can point callers at the wrong union member. Many macros encode hardware-specific constants with little type checking. Descriptor error masks directly affect packet drop/error accounting and checksum behavior, especially when TAH is present.

## Test Signals
Hardware bring-up, `ethtool -d` register dumps, MDIO read/write success, interrupt counter increments for injected errors, multicast filter behavior, and jumbo-speed configuration all validate this header indirectly. Cross-building for EMAC4 and EMAC4SYNC variants catches missing field references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.c

## Purpose
`mal.c` implements the IBM EMAC Memory Access Layer, a shared DMA engine that owns descriptor memory, DCR register programming, interrupt handling, and NAPI dispatch for one or more communication MACs (`mal_commac`) such as EMAC instances.

## Important APIs, Types, and Functions
Public functions include `mal_register_commac()`, `mal_unregister_commac()`, `mal_set_rcbs()`, `mal_tx_bd_offset()`, `mal_rx_bd_offset()`, channel enable/disable routines, `mal_poll_add()`, `mal_poll_del()`, `mal_poll_disable()`, `mal_poll_enable()`, `mal_get_regs_len()`, `mal_dump_regs()`, `mal_init()`, and `mal_exit()`. Internal IRQ handlers are `mal_serr()`, `mal_txeob()`, `mal_rxeob()`, `mal_txde()`, `mal_rxde()`, and `mal_int()` for common-error configurations. `mal_poll()` is the shared NAPI poller.

## Control Flow
Probe allocates `struct mal_instance`, reads OF `num-tx-chans`/`num-rx-chans`, maps DCRs, sets feature flags for special SoCs, initializes lists/lock/NAPI, resets MAL, configures MAL CFG, allocates coherent descriptor memory for all TX/RX channels, writes channel table pointer DCRs, requests interrupts, enables MAL error events and EOB interrupts, then publishes drvdata. EMAC probe registers a `mal_commac`, which claims TX/RX channel masks and enables NAPI if it is the first user. End-of-buffer IRQs schedule NAPI and disable EOB interrupts; NAPI calls each registered commac’s TX reclaim then RX poll callbacks, completes, reenables EOB interrupts, and checks for rotting packets or stopped RX channels. Descriptor-error IRQs set `MAL_COMMAC_RX_STOPPED` and call the commac `rxde` callback for affected RX channels.

## State and Persistence
`struct mal_instance` holds DCR host mapping, channel counts, IRQ numbers, commac lists, NAPI object, channel allocation masks, coherent descriptor memory, feature flags, and a dummy netdev used for NAPI. State is volatile. Descriptor memory is coherent DMA and shared with EMAC users by offset.

## Dependencies and Integration Points
The module depends on platform/OF probing, PowerPC DCR access, DMA coherent allocation, NAPI, IRQs, local `core.h`/`mal.h`, and EMAC commac callbacks. Device-tree compatible strings distinguish MAL v1/v2, Axon behavior, and legacy type matches. EMAC uses MAL offsets and channel APIs to operate its rings.

## Risks
MAL is shared: channel-mask conflicts or list misuse can break multiple EMACs. NAPI fairness is explicitly simple and may favor earlier poll-list entries. RX channel numbering has a special divide-by-eight adjustment for certain SoCs, which is easy to regress. IRQ error handling often logs and continues; PLB/OPB errors may indicate bad DMA addresses or hardware setup. Removal warns if commacs remain registered.

## Test Signals
Probe logs showing MAL version and channel counts, successful EMAC registration with non-conflicting channels, TX/RX EOB interrupt activity, NAPI traffic on multiple EMACs, descriptor-error recovery, `ethtool -d` MAL register dump content, and removal without non-empty commac-list warnings are key signals. SoC variants with common error interrupt and clear-ICINTSTAT behavior need targeted coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.h

## Purpose
`mal.h` defines the Memory Access Layer register map, descriptor format, commac callback interface, per-MAL state, feature flags, and public MAL APIs used by EMAC core code.

## Important APIs, Types, and Functions
Register constants cover MAL CFG/ESR/IER, TX/RX channel active/reset/status registers, channel table pointers, and receive channel buffer size registers. `MAL_MAX_TX_SIZE` and `MAL_MAX_RX_SIZE` define the 4080-byte payload chunks; `mal_rx_size()` aligns RX sizes and `mal_tx_chunks()` estimates TX descriptor use. `struct mal_descriptor` is the hardware BD format. `struct mal_commac_ops` is the callback table for TX poll, RX poll, RX peek, and RX descriptor-error handling. `struct mal_commac` contains channel masks, flags, and list nodes. `struct mal_instance` stores hardware, NAPI, descriptor memory, registered commacs, and feature state. Public declarations expose channel management, polling, registration, and ethtool dump helpers.

## Control Flow
The header’s definitions are consumed by `mal.c` and `core.c`: EMAC fills `mal_commac`, MAL NAPI dispatches callbacks, and EMAC TX/RX code reads/writes descriptor control bits such as `MAL_RX_CTRL_EMPTY`, `MAL_RX_CTRL_FIRST`, `MAL_RX_CTRL_LAST`, `MAL_TX_CTRL_READY`, and `MAL_TX_CTRL_WRAP`.

## State and Persistence
All state is volatile kernel or device state. The descriptor format is shared with DMA hardware, so field sizes and endian behavior matter. `MAL_COMMAC_RX_STOPPED` and `MAL_COMMAC_POLL_DISABLED` are bit positions stored in `mal_commac.flags`.

## Dependencies and Integration Points
The file relies on DCR helpers via `dcr_read()`/`dcr_write()` wrappers and Kconfig feature symbols for special MAL behavior. Its API is the narrow integration point between the shared DMA engine and EMAC netdev instances.

## Risks
Descriptor-size constants and channel offsets must match allocation logic exactly. A bad `MAL_CHAN_MASK()` channel number can select the wrong hardware channel. Compile-time feature masks can silently disable support for a SoC whose device tree is present. The `mal_regs` dump reserves arrays for 32 channels, matching the implementation’s BUG_ON bounds.

## Test Signals
Build and runtime validation should cover descriptor wrap behavior, RX size alignment, TX chunk calculation for large packets, multi-channel channel-mask conflicts, and ethtool register dump size. Kconfig variants for `CONFIG_IBM_EMAC_MAL_CLR_ICINTSTAT` and `CONFIG_IBM_EMAC_MAL_COMMON_ERR` need compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/mal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.c

## Purpose
`phy.c` provides legacy MII/GMII PHY support for the IBM EMAC driver. It implements generic autonegotiation/forced-link operations, reset helpers for external PHYs and internal GPCS, several PHY-specific initialization sequences, and a probe routine that identifies a PHY by MII ID and fills `struct mii_phy`.

## Important APIs, Types, and Functions
Public functions are `emac_mii_reset_phy()`, `emac_mii_reset_gpcs()`, and `emac_mii_phy_probe()`. Generic operations are `genmii_setup_aneg()`, `genmii_setup_forced()`, `genmii_poll_link()`, and `genmii_read_link()`, grouped into `generic_phy_ops`. PHY-specific init routines include `cis8201_init()`, `m88e1111_init()`, `m88e1112_init()`, `et1011c_init()`, and `ar8035_init()`. The table `mii_phy_table` matches ET1011C, CIS8201, BCM5248, Marvell 88E1111/88E1112, Atheros AR8035, and a generic fallback.

## Control Flow
EMAC initializes a `mii_phy` with MDIO callbacks, then calls `emac_mii_phy_probe()` for candidate addresses. Probe resets the PHY, reads ID registers, selects a definition, derives supported link modes from BMSR/ESTATUS when the definition does not hard-code features, and initializes default advertising. Later link setup calls `setup_aneg()` or `setup_forced()`. Link polling reads BMSR twice to clear latches, waits for autoneg completion when enabled, and `read_link()` computes speed/duplex/pause from negotiated partner registers or BMCR forced settings. GPCS reset additionally programs SGMII-recommended registers.

## State and Persistence
The file mutates only `struct mii_phy` fields and PHY/GPCS MDIO registers. No state persists beyond hardware register settings and the EMAC-owned `mii_phy` instance.

## Dependencies and Integration Points
It depends on Linux MII/ethtool constants and the caller-provided MDIO read/write hooks in `struct mii_phy`. `core.c` integrates it into device-tree and legacy PHY discovery, and may replace it with phylib-backed operations when `phy-handle` is present.

## Risks
Vendor-specific register writes are hard-coded and board-sensitive. Generic feature discovery assumes standard MII registers behave correctly. The PHY table has a generic all-zero mask fallback, so unknown PHYs are accepted with generic operations rather than rejected. Reset polling returns a boolean-like timeout result, so callers must interpret nonzero as failure. GPCS address handling depends on EMAC mode and device-tree defaults.

## Test Signals
PHY detection logs, successful autonegotiation at 10/100/1000, forced speed/duplex changes through ethtool, pause/asymmetric pause reporting, link flap handling, and board-specific PHY initialization on CIS8201/Marvell/ET1011C/AR8035 hardware are useful signals. MDIO error injection should confirm probe skips absent addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.h

## Purpose
`phy.h` declares the legacy PHY abstraction used by the IBM EMAC driver when not fully delegated to phylib. It defines PHY operation callbacks, static PHY definitions, live PHY state, and public probe/reset APIs.

## Important APIs, Types, and Functions
`struct mii_phy_ops` contains optional `init`/`suspend` callbacks and required-style link methods for autonegotiation, forced setup, polling, and link reading. `struct mii_phy_def` describes a PHY ID/mask, feature set, name, and ops. `struct mii_phy` stores selected definition, advertising/features, MDIO address, interface mode, GPCS address, autoneg/speed/duplex/pause state, owning netdev, and MDIO callbacks. Public declarations are `emac_mii_phy_probe()`, `emac_mii_reset_phy()`, and `emac_mii_reset_gpcs()`.

## Control Flow
`core.c` allocates/fills a `struct mii_phy`, calls probe/reset helpers, then invokes `def->ops` during initial setup, ethtool changes, and link polling.

## State and Persistence
`struct mii_phy` is volatile per-EMAC state, mirroring current PHY configuration and negotiated status. Hardware persistence is limited to PHY register programming performed by operations in `phy.c`.

## Dependencies and Integration Points
The struct uses `struct net_device` and ethtool legacy `SUPPORTED_*`/`ADVERTISED_*` bit conventions. It integrates with EMAC’s MDIO functions via callback pointers rather than owning an MDIO bus itself.

## Risks
The abstraction predates modern phylib conventions and mixes policy, cache, and hardware state. The unused `magic_aneg` and `suspend` fields indicate incomplete or legacy surface. Consumers must ensure MDIO callbacks are valid before invoking operations.

## Test Signals
Compile coverage with legacy PHY discovery, ethtool link-setting operations, and MDIO ioctl paths validates this header. Runtime checks should ensure cached `mii_phy` state tracks actual PHY status after link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.c

## Purpose
`rgmii.c` implements the platform driver for IBM EMAC RGMII bridge blocks. It configures bridge inputs for RGMII/RTBI/TBI/GMII/MII modes, updates speed-select registers on link changes, optionally gates MDIO access through the selected input, and supports ethtool register dumps.

## Important APIs, Types, and Functions
Public functions are `rgmii_attach()`, `rgmii_detach()`, `rgmii_get_mdio()`, `rgmii_put_mdio()`, `rgmii_set_speed()`, `rgmii_get_regs_len()`, `rgmii_dump_regs()`, `rgmii_init()`, and `rgmii_exit()`. Internal helpers `rgmii_valid_mode()` and `rgmii_mode_mask()` validate interface modes and compute FER bits. Probe maps the bridge registers, sets `EMAC_RGMII_FLAG_HAS_MDIO` from `has-mdio` or Axon compatibility, disables all inputs, and publishes drvdata.

## Control Flow
EMAC probe calls `rgmii_attach()` after dependency resolution. Attach validates the requested input and PHY mode, sets the input’s function-enable bits, increments users, and logs mode. During EMAC configuration, `rgmii_set_speed()` rewrites the input’s SSR speed bits for 10/100/1000. During MDIO transactions, EMAC calls `rgmii_get_mdio()` before STACR access and `rgmii_put_mdio()` afterward; when MDIO gating is supported, the functions lock the bridge, set/clear the MDIO select bit, and serialize access. Detach clears FER bits and decrements users.

## State and Persistence
State is in `struct rgmii_instance`: mapped registers, flags, mutex, user count, and platform device. Hardware state is the FER/SSR register pair. There is no persistent state.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO access, PHY mode constants, `emac_ethtool_regs_subhdr`, and EMAC core calls. Device-tree compatibles include `ibm,rgmii`, legacy `emac-rgmii`, and `ibm,rgmii-axon` fixups.

## Risks
MDIO locking is split across get/put, so every caller must pair calls exactly. Unsupported modes fail attach except MII is mapped to GMII bits. User count is protected by a mutex but only checked by `BUG_ON()` at detach. Axon behavior has a FIXME indicating possible register-bit mismatch.

## Test Signals
RGMII probe logs, attach logs with correct PHY mode, link-speed changes updating SSR, successful MDIO reads through RGMII, ethtool register dumps, and attach/detach balancing during EMAC probe/remove are useful signals. Axon hardware needs specific validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.h

## Purpose
`rgmii.h` declares the RGMII bridge register/state structures and public API used by EMAC core code, with stubbed no-op or error macros when RGMII support is not compiled.

## Important APIs, Types, and Functions
`struct rgmii_regs` maps the bridge function-enable (`fer`) and speed-select (`ssr`) registers. `struct rgmii_instance` stores the MMIO base, flags, mutex, user count, and OF platform device. `EMAC_RGMII_FLAG_HAS_MDIO` marks bridges that require MDIO selection. Public APIs include init/exit, attach/detach, MDIO get/put, speed setting, and register dump helpers.

## Control Flow
With `CONFIG_IBM_EMAC_RGMII`, `core.c` calls these functions during module init, EMAC probe/remove, MDIO transactions, link-speed reconfiguration, and ethtool dumps. Without the config, init succeeds, attach returns `-ENXIO`, and other calls are inert.

## State and Persistence
The header defines volatile bridge state only. Hardware register values persist only as programmed by the driver while loaded.

## Dependencies and Integration Points
It depends on platform-device declarations and EMAC core ethtool dump framing. The stubs are important integration behavior: a device tree requiring RGMII will fail EMAC config if the Kconfig option is disabled.

## Risks
Compile-time stubs can hide missing RGMII support until runtime probe. User count is a plain integer guarded by implementation mutexes. The unused `RGMII_STANDARD`/`RGMII_AXON` constants suggest legacy or incomplete bridge typing.

## Test Signals
Builds with and without `CONFIG_IBM_EMAC_RGMII`, probe failure when device tree requests RGMII without support, and valid register dump lengths when enabled are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/rgmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.c

## Purpose
`tah.c` implements the IBM EMAC TAH helper block, used for checksum assist and transmit acceleration support. It provides a small platform driver that maps TAH registers, resets/configures the block, tracks users, and contributes register dumps to EMAC ethtool output.

## Important APIs, Types, and Functions
Public functions are `tah_attach()`, `tah_detach()`, `tah_reset()`, `tah_get_regs_len()`, `tah_dump_regs()`, `tah_init()`, and `tah_exit()`. `tah_probe()` allocates and initializes `struct tah_instance`, maps registers, stores drvdata, and calls `tah_reset()`.

## Control Flow
TAH probe resets the hardware immediately and logs initialization. EMAC probe attaches to the TAH phandle/channel, enabling EMAC features such as IP checksum and scatter-gather. EMAC configuration calls `tah_reset()` when TAH is present, so the assist block is reset alongside EMAC mode changes. Detach only decrements the user count. Register dumps copy the whole `struct tah_regs` block after an EMAC subheader.

## State and Persistence
State is minimal: mapped registers, mutex, user count, and platform device. Hardware mode register state is set to enable checksum verification and configure a 10KB TX FIFO with selected thresholds. There is no disk persistence.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO, and local EMAC register-dump framing. EMAC core uses TAH presence to enable `NETIF_F_IP_CSUM`, `NETIF_F_SG`, RX checksum marking, and TAH-specific TX/RX descriptor status interpretation.

## Risks
Attach/detach do not validate channel values beyond user tracking. Reset uses a tight polling loop and only logs timeout. TAH mode settings are hard-coded, including a comment that TSO is not enabled yet. Incorrect TAH presence can produce wrong checksum behavior.

## Test Signals
TAH probe logs, EMAC feature flags showing checksum/SG support, RX checksum-offload counters, TX checksum behavior, ethtool register dump inclusion, and reset timeout absence are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.h

## Purpose
`tah.h` declares TAH register layout, instance state, mode-register bit definitions, public APIs, and no-op stubs when TAH support is disabled.

## Important APIs, Types, and Functions
`struct tah_regs` maps revision, mode, status, and transmit status registers. `struct tah_instance` stores mapped MMIO, lock, user count, and platform device. Bitfields such as `TAH_MR_SR`, `TAH_MR_CVR`, `TAH_MR_ST_*`, `TAH_MR_TFS_*`, `TAH_MR_DTFP`, and `TAH_MR_DIG` drive reset/configuration. Public functions cover init/exit, attach/detach, reset, and register dump.

## Control Flow
When `CONFIG_IBM_EMAC_TAH` is enabled, EMAC module init registers the TAH platform driver and EMAC probe/configuration can call the real functions. When disabled, init succeeds, attach returns `-ENXIO`, reset/detach are no-ops, and register dump helpers report no length.

## State and Persistence
The header defines volatile driver/MMIO state only. Register values persist only as hardware configuration during driver runtime.

## Dependencies and Integration Points
It integrates with EMAC core feature detection and ethtool register dumping. Its stubs let `core.c` compile without TAH, but device trees that declare TAH require the Kconfig option.

## Risks
Stub behavior means a missing config becomes a runtime probe/config failure. The mode bit definitions are hardware-specific and have no type checking. User count is simple and relies on implementation locking.

## Test Signals
Builds with/without `CONFIG_IBM_EMAC_TAH`, EMAC probe behavior for TAH device-tree phandles, and correct ethtool register dump sizing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/tah.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.c

## Purpose
`zmii.c` implements the IBM EMAC ZMII bridge platform driver. ZMII bridges connect EMAC inputs to MII/RMII/SMII modes, select MDIO routing, update speed bits, and expose bridge registers for ethtool dumps.

## Important APIs, Types, and Functions
Public functions are `zmii_attach()`, `zmii_detach()`, `zmii_get_mdio()`, `zmii_put_mdio()`, `zmii_set_speed()`, `zmii_get_regs_len()`, `zmii_dump_regs()`, `zmii_init()`, and `zmii_exit()`. Helpers `zmii_valid_mode()`, `zmii_mode_name()`, and `zmii_mode_mask()` validate and encode PHY interface modes. `zmii_probe()` maps registers, saves firmware FER for autodetection, clears FER, initializes the mutex, and publishes drvdata.

## Control Flow
EMAC probe calls `zmii_attach()` when a ZMII phandle is configured. Attach permits invalid modes as a non-fatal case for EMACs that may only need ZMII for MDIO, otherwise it autodetects bridge mode from saved firmware FER when no PHY mode is specified, enforces a single mode for all inputs, writes FER bits for the selected input, and increments users. EMAC MDIO transactions call get/put to lock the bridge and route MDIO to one input. Link configuration calls `zmii_set_speed()` to set or clear the 100M speed bit. Detach clears the input mode bit and decrements users.

## State and Persistence
`struct zmii_instance` holds base registers, mutex, selected mode, user count, saved firmware FER, and platform device. Hardware state is FER/SSR/SMIIRS. No disk state exists.

## Dependencies and Integration Points
The file depends on OF platform probing, MMIO, PHY interface constants, and EMAC core ethtool framing. Device-tree compatible strings include `ibm,zmii` and legacy `emac-zmii`.

## Risks
Autodetection from firmware FER is a backward-compatibility fallback and may mis-detect boards without explicit PHY mode. All attached inputs must share a single ZMII mode. MDIO locking spans get/put and requires strict pairing. Attach increments users even when mode is invalid but tolerated for MDIO-only use, making detach behavior dependent on caller consistency.

## Test Signals
Probe logs, bridge mode logs, explicit and autodetected PHY modes, MDIO reads routed through ZMII, 10/100 speed changes, ethtool register dumps, and attach/detach balancing are primary validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.h

## Purpose
`zmii.h` declares the ZMII bridge register layout, instance state, public API, and disabled-config stubs for the IBM EMAC driver.

## Important APIs, Types, and Functions
`struct zmii_regs` maps function-enable, speed-select, and SMII status registers. `struct zmii_instance` stores mapped registers, mutex, selected PHY mode, user count, saved firmware FER, and platform device. API declarations cover init/exit, attach/detach, MDIO get/put, speed selection, and ethtool register dumping.

## Control Flow
With `CONFIG_IBM_EMAC_ZMII`, EMAC core can register and call the real ZMII helper. Without it, init succeeds, attach returns `-ENXIO`, and the remaining operations are no-ops or zero-length dump helpers.

## State and Persistence
The header defines volatile driver state and MMIO structures only. `fer_save` captures firmware-programmed register state for runtime autodetection but is not persistent across boots.

## Dependencies and Integration Points
The API is called from EMAC probe/remove, MDIO transactions, link speed changes, and ethtool register dumps. Stub behavior ties device-tree use of ZMII to the Kconfig option.

## Risks
Disabled stubs can defer configuration problems to runtime. The single `mode` field means all users of a ZMII instance must be compatible. `users` is simple and relies on implementation locking.

## Test Signals
Builds with/without `CONFIG_IBM_EMAC_ZMII`, runtime probe success for ZMII phandles, invalid mixed-mode rejection, and register dump size correctness are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/zmii.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.c

## Purpose
`ibmveth.c` is the IBM Power virtual Ethernet driver for pSeries/VIO logical LAN devices. It implements a hypervisor-call backed netdev using receive buffer pools, a shared RX completion queue, long-term TX bounce buffers, NAPI polling, multicast/filter control, checksum/large-send offloads, sysfs-tunable buffer pools, VIO probe/remove, PM resume, and KUnit tests for selected buffer-pool helpers.

## Important APIs, Types, and Functions
Module parameters `tx_copybreak`, `rx_copybreak`, `rx_flush`, and `old_large_send` tune copy/flush/offload behavior. Netdev lifecycle is handled by `ibmveth_probe()`, `ibmveth_remove()`, `ibmveth_open()`, `ibmveth_close()`, and scheduled `ibmveth_reset()`. RX pool functions include `ibmveth_init_buffer_pool()`, `ibmveth_alloc_buffer_pool()`, `ibmveth_replenish_buffer_pool()`, `ibmveth_replenish_task()`, `ibmveth_free_buffer_pool()`, `ibmveth_remove_buffer_from_pool()`, `ibmveth_rxq_get_buffer()`, and `ibmveth_rxq_harvest_buffer()`. TX functions include `ibmveth_allocate_tx_ltb()`, `ibmveth_free_tx_ltb()`, `ibmveth_send()`, `ibmveth_start_xmit()`, and `ibmveth_features_check()`. RX receive processing is in `ibmveth_poll()`, with helpers `ibmveth_rx_mss_helper()` and `ibmveth_rx_csum_helper()`. Etthtool/sysfs controls are implemented by link-setting, feature, stats, channel, and `veth_pool_*` functions.

## Control Flow
VIO probe reads VETH MAC and multicast filter attributes, allocates a multiqueue netdev, initializes adapter state, sets NAPI, determines firmware offload capabilities via `H_ILLAN_ATTRIBUTES`, initializes RX pool kobjects, sets TX queue count, configures features, and registers the netdev. Open enables NAPI, allocates buffer/filter pages, allocates coherent RX queue memory, maps buffer/filter lists, allocates per-TX-queue long-term buffers, registers the logical LAN with PHYP via `H_REGISTER_LOGICAL_LAN`, allocates active RX pools, requests the IRQ, triggers initial replenish through the interrupt path, and starts TX queues. TX copies skb linear/frags into the queue’s mapped long-term buffer, sets checksum/large-send descriptor flags, optionally encodes old large-send MSS in checksums, then calls `H_SEND_LOGICAL_LAN` with retry handling for busy multicast/broadcast fanout. IRQ disables VIO interrupts and schedules NAPI. Poll consumes RX queue entries while the toggle bit indicates pending buffers, handles invalid entries, maps correlators back to pool/index, copies small frames or hands up original skbs, derives GRO/GSO metadata for large packets, handles checksum state, submits packets via GRO, replenishes pools, completes NAPI, reenables VIO interrupts, and races safely with newly arrived entries. Close stops queues, unregisters the logical LAN, frees IRQ, updates no-buffer stats, unmaps/frees queues/lists/pools/long-term buffers, and disables NAPI.

## State and Persistence
`struct ibmveth_adapter` holds VIO/netdev pointers, NAPI/work, multicast filter size, buffer/filter pages and DMA addresses, TX long-term buffers, RX pools, RX queue, offload state, firmware capability counters, runtime stats, and advertised link settings. RX pool state tracks free-map producer/consumer indices, DMA addresses, skb pointers, and atomic available counts. Sysfs pool attributes persist only while the device exists; there is no disk persistence.

## Dependencies and Integration Points
The driver depends on PowerPC VIO, PHYP hypervisor calls (`H_REGISTER_LOGICAL_LAN`, `H_FREE_LOGICAL_LAN`, `H_ADD_LOGICAL_LAN_BUFFER(S)`, `H_SEND_LOGICAL_LAN`, `H_ILLAN_ATTRIBUTES`, `H_MULTICAST_CTRL`, `H_CHANGE_LOGICAL_LAN_MAC`), IOMMU/DMA mapping, NAPI/GRO, netdev multiqueue APIs, ethtool, firmware CMO support, sysfs kobjects, and optional netpoll/KUnit. VIO attributes `VETH_MAC_ADDR` and `VETH_MCAST_FILTER_SIZE` are required probe contracts.

## Risks
Open error unwinding is complex and shares loop variable `i` across TX buffer and RX pool cleanup paths. RX pool correlators are trusted after bounds/WARN checks; invalid values schedule a full reset. Multi-buffer replenish can fail after live partition migration and falls back to single-buffer hcalls only for future replenish. TX always copies into long-term buffers, so queue count, buffer size, and GSO feature checks are critical. Feature toggles may close/reopen the device, so failure recovery must preserve feature flags and pool state. Sysfs pool changes close/reopen under RTNL and must never disable all MTU-capable pools. Some checksum/large-send behavior depends on older firmware conventions such as using checksum fields to carry MSS.

## Test Signals
Runtime signals include successful VIO probe/register, open/close cycles, PHYP hcall return logs, RX replenish success/failure stats, live migration fallback from multi-buffer to single-buffer hcalls, TX/RX checksum and TSO behavior, multicast/promiscuous filter hcalls, MTU changes, sysfs pool active/num/size changes, ethtool stats/channels/features, PM resume replenish, and reset work after invalid buffer state. In-tree KUnit tests cover invalid correlator handling in `ibmveth_remove_buffer_from_pool()` and `ibmveth_rxq_get_buffer()`, providing direct regression signals for pool bounds behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.h

## Purpose
`ibmveth.h` defines the firmware/hypervisor interface constants, hcall wrappers, buffer-pool defaults, adapter state structures, TX/RX descriptor formats, and RX queue entry bits for the IBM virtual Ethernet driver.

## Important APIs, Types, and Functions
Hcall wrappers/macros include `h_register_logical_lan()`, `h_free_logical_lan()`, `h_add_logical_lan_buffer()`, `h_add_logical_lan_buffers()`, `h_send_logical_lan()`, `h_illan_attributes()`, `h_multicast_ctrl()`, and `h_change_logical_lan_mac()`. Capability bits include checksum, large send, active trunk, padded packet checksum, and RX multi-buffer support. Defaults define five RX pools, pool sizes/counts/active states, CMO pool counts, maximum TX buffer size, max/default queue counts, and max RX descriptors per hcall. Core structures are `struct ibmveth_buff_pool`, `struct ibmveth_rx_q`, `struct ibmveth_adapter`, `struct ibmveth_buf_desc_fields`, `union ibmveth_buf_desc`, and `struct ibmveth_rx_q_entry`.

## Control Flow
The header’s wrappers are called throughout `ibmveth.c` for logical LAN registration, buffer submission, packet send, attribute negotiation, multicast filtering, and MAC changes. Descriptor and RX queue bit definitions drive TX descriptor construction and RX poll parsing. Pool default arrays are used at probe to initialize per-adapter pool kobjects and runtime replenish behavior.

## State and Persistence
`struct ibmveth_adapter` is all volatile per-device state. RX pool arrays contain dynamic allocation pointers and atomic available counters. The descriptor union intentionally handles endian ordering because descriptors are passed as register-sized values to hypervisor calls. No data persists outside runtime.

## Dependencies and Integration Points
The file depends on PowerPC PAPR hypervisor call APIs and VIO conventions. It is tightly coupled to PHYP’s logical LAN ABI, including correlator layout, multicast control command bits, and `H_SEND_LOGICAL_LAN` argument conventions with optional MSS/large-send support.

## Risks
Static pool arrays in a header would be problematic if included by multiple C files, but this header is intended for the single implementation. Endian-specific descriptor field ordering is critical. `h_send_logical_lan()` has two call shapes depending on firmware large-send support; argument mismatch would corrupt sends. Pool and buffer size constants gate MTU and DMA entitlement calculations.

## Test Signals
Compile coverage on big-endian and little-endian PowerPC configurations, successful firmware capability negotiation, descriptor flag correctness in TX/RX traces, CMO desired-DMA calculations, sysfs pool defaults, and KUnit tests that exercise pool/queue structures validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ibmveth.h -->
