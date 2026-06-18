# subset-b-004618 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_main.c

## Purpose
`rswitch_main.c` is the main Renesas R-Car Gen4 Ethernet Switch platform driver. It binds `renesas,r8a779f0-ether-switch`, creates one netdev per enabled TSN port (`tsn%d`), configures the common switch blocks, manages GWCA CPU-agent DMA queues, initializes ETHA/RMAC MAC ports, connects MDIO/PHY/SerDes, registers the shared Gen4 PTP clock, and exposes switchdev/L2 offload integration through `rswitch_l2`.

## Important APIs, Types, And Functions
The driver centers on `struct rswitch_private`, `struct rswitch_device`, `struct rswitch_etha`, `struct rswitch_gwca`, and `struct rswitch_gwca_queue` from `rswitch.h`. Register helpers are `rswitch_reg_wait()` and exported `rswitch_modify()`. Probe/remove/PM are `renesas_eth_sw_probe()`, `renesas_eth_sw_remove()`, `renesas_eth_sw_suspend()`, and `renesas_eth_sw_resume()`. Netdev operations are `rswitch_open()`, `rswitch_stop()`, `rswitch_start_xmit()`, stats, port identity, and hwtstamp get/set. Data-plane work is split across `rswitch_poll()`, `rswitch_rx()`, `rswitch_tx_free()`, `rswitch_gwca_irq()`, and timestamp completion `rswitch_gwca_ts_irq()`/`rswitch_ts()`. Initialization is staged through `rswitch_init()`, `rswitch_fwd_init()`, `rswitch_gwca_hw_init()`, `rswitch_ether_port_init_all()`, and per-port helpers such as `rswitch_mii_register()` and `rswitch_phy_device_init()`.

## Control Flow
Probe maps the `secure_base` resource, gets the clock, allocates PTP state, sets a 40-bit DMA mask with 32-bit fallback, prepares GWCA queue storage, enables runtime PM, then calls `rswitch_init()`. Initialization reads hardware MAC addresses, resets and clocks COMA, formats TOP queue-to-IRQ routing, configures buffer pools, allocates the GWCA linkfix table and timestamp queue, allocates per-port netdevs and DMA rings, initializes forwarding, registers PTP, requests data and timestamp IRQs, starts GWCA operation, initializes PHY/SerDes/MAC ports, and finally registers enabled netdevs. Open enables NAPI, marks the port in `opened_ports`, enables its TX/RX queue IRQ bits, starts PHY and TX queue, and refreshes bridge offload when applicable. Interrupts disable per-queue IRQs and schedule NAPI; NAPI reclaims TX descriptors, drains/refills RX descriptors, wakes the queue, and re-enables IRQs after completion. Remove unregisters notifiers, unregisters netdevs, deinitializes PHY/SerDes and GWCA, frees rings/tables, disables clocks and runtime PM.

## State And Persistence
Persistent runtime state is in `rswitch_private`: mapped register base, PTP private state, enabled/opened port bitmaps, GWCA queues, IRQ masks, a spinlock, timestamp controls, and the `gwca_halt` fail-stop flag. Per-port state tracks port index, ETHA pointer, DT node, PHY, SerDes, bridge membership, NAPI, RX/TX queues, and outstanding timestamp SKBs by tag. DMA rings are coherent memory plus RX frag buffers and SKB/unmap arrays. Hardware state includes COMA clocks, forwarding table entries, GWCA modes, descriptor base addresses, ETHA mode, RMAC speed/interface, and timestamp queues. No durable on-disk persistence exists.

## Dependencies And Integration Points
The driver depends on Linux platform, OF, phylib, MDIO, PHY framework, NAPI, DMA API, ethtool timestamping, PM runtime, and Renesas Gen4 PTP helpers (`rcar_gen4_ptp_*`). It integrates with `rswitch_l2` through `rswitch_register_notifiers()`, `rswitch_update_l2_offload()`, and exported `is_rdev()`. DT must provide `ethernet-ports`, per-port `reg`, `phy-mode`, `phy-handle`, optional `max-speed`, MDIO child nodes, SerDes PHYs, named IRQs, and memory resources.

## Risks
Descriptor lifetime is delicate: TX stores the SKB only on the final descriptor, and timestamp SKB tags require ordering barriers plus cleanup on stop. RX allocation/refill failures call `rswitch_gwca_halt()`, deinitializing GWCA from the receive path and leaving recovery to higher-level close/remove. Speed-change behavior is SoC-revision dependent; ES1.0 disables runtime speed changes and filters PHY advertised modes. Error unwinds are broad and must keep per-port allocations, `of_node_put()`, PTP registration, GWCA resources, and devm IRQ assumptions balanced. Bridge/L2 offload state must be updated when ports open/close to avoid stale forwarding. The code assumes valid descriptor status ordering and correct DT port numbering.

## Test Signals
Useful signals are successful probe with per-port MAC log lines, `ip link set tsnX up/down`, traffic across each enabled port, MTU-bound TX segmentation over multiple descriptors, NAPI budget stress, RX allocation failure injection, ethtool `-T` timestamp capability and PTP TX/RX timestamp tests, suspend/resume with running interfaces, bridge membership/offload changes, PHY link speed changes including ES1.0 fixed-speed behavior, and IRQ-name/resource validation from device tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.c

## Purpose
`rtsn.c` is the Renesas Ethernet-TSN platform driver for `renesas,r8a779g0-ethertsn`. It presents a single Ethernet netdev backed by one TX descriptor chain and one RX descriptor chain, configures TSN AXIBMI/MHD/RMAC hardware, registers an MDIO bus, connects to a PHY, and exposes Gen4 PTP-based hardware timestamping.

## Important APIs, Types, And Functions
The local `struct rtsn_private` owns all device state: netdev/platform device, mapped register base, reset/clock, PTP state, descriptor BATs, DMA rings, SKB arrays, indices, NAPI, statistics, MDIO bus, PHY link state, IRQs, and timestamp configuration. Register helpers are `rtsn_read()`, `rtsn_write()`, `rtsn_modify()`, and `rtsn_reg_wait()`. Open/close are `rtsn_open()` and `rtsn_stop()`. Data path functions include `rtsn_start_xmit()`, `rtsn_tx_free()`, `rtsn_rx()`, `rtsn_poll()`, and `rtsn_irq()`. Hardware setup is handled by `rtsn_reset()`, `rtsn_change_mode()`, `rtsn_axibmi_init()`, `rtsn_mhd_init()`, `rtsn_rmac_init()`, and `rtsn_hw_init()`. Probe/remove are `rtsn_probe()` and `rtsn_remove()`.

## Control Flow
Probe allocates an etherdev, maps `tsnes` and `gptp` resources, gets clock and reset controls, allocates/registers PTP, validates PHY mode, enables runtime PM, adds NAPI, reads or generates the MAC address, sets a 32-bit DMA mask, registers the MDIO bus, and registers the netdev. Opening enables NAPI and then calls `rtsn_init()`, which allocates descriptor BATs, allocates/formats coherent TX/RX rings, resets and configures hardware, connects PHY, and requests separate TX/RX IRQs. TX maps a padded SKB into a single descriptor, optionally marks TX timestamp request, advances `cur_tx`, and kicks `TRCR0`. IRQ clears TX/RX status, disables data IRQs, and schedules NAPI. NAPI drains RX descriptors up to budget, refills RX buffers, reclaims completed TX descriptors, wakes the queue, and re-enables IRQs. Stop stops PHY, disables NAPI, transitions hardware to disabled mode, frees IRQs, disconnects PHY, and frees rings/BATs.

## State And Persistence
Runtime state is volatile. TX/RX progress is tracked by monotonic `cur_*` and `dirty_*` counters modulo ring size. `stats` is stored in `rtnl_link_stats64`. Timestamp mode is held in `tstamp_tx_ctrl` and `tstamp_rx_ctrl`; RX timestamps come from timestamped RX descriptors, while TX timestamp completion samples the shared PTP clock during TX reclaim if the original SKB requested hardware timestamping. Hardware mode state is explicitly driven through DISABLE, CONFIG, and OPERATION modes.

## Dependencies And Integration Points
The driver uses platform resources, reset controller, clock framework, OF MDIO, phylib, NAPI, DMA API, runtime PM, ethtool timestamping, and `rcar_gen4_ptp`. DT must provide `tsnes` and `gptp` memory resources, `rx` and `tx` IRQ names, `phy-mode`, `phy-handle`, and an `mdio` child. Supported PHY interfaces are MII and RGMII variants. Netdev operations include hardware timestamp get/set, address validation, MAC setting, stats64, and phylib ioctl.

## Risks
TX supports only packets fitting a single descriptor and drops larger SKBs, so feature flags must not advertise scatter-gather or TSO. `rtsn_get_data_irq_status()` ORs in the TX/RX chain bits rather than masking with status, so interrupt handling should be checked carefully against hardware semantics. DMA addresses are stored as 32-bit descriptor fields, making the 32-bit DMA mask important. RX refill handles allocation failure by leaving descriptors unavailable until later polling. TX timestamping is approximate because completion uses current PTP time rather than a hardware TX timestamp descriptor. Open-time allocation means repeated up/down cycles exercise all error paths.

## Test Signals
Validation should include probe/remove, open/close cycles, MDIO scan/PHY attach, link speed changes through `rtsn_adjust_link()`, TX/RX traffic at MII and RGMII speeds, ring wrap at 1024 descriptors, large-SKB drop behavior, NAPI budget exhaustion, RX checksum feature toggling, ethtool timestamp capability, `SIOCSHWTSTAMP`/netlink hwtstamp get/set while down and up, and runtime PM balance during probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.h

## Purpose
`rtsn.h` is the private hardware contract for the Renesas Ethernet-TSN driver. It defines register offsets for AXIBMI, TSNMHD, RMSO, and RMRO blocks; bitfields used by `rtsn.c`; descriptor layouts; chain sizes; timeout constants; and operation-mode/descriptors enums.

## Important APIs, Types, And Constants
The central enum is `enum rtsn_reg`, which maps symbolic names such as `TATLS0`, `RATLS0`, `OCR`, `OSR`, `TGC1`, `CFCR0`, `MPSM`, `MPIC`, `MRMAC0`, and `MLVC` onto block-relative offsets. `enum rtsn_mode` defines DISABLE, CONFIG, and OPERATION values written to `OCR`. Descriptor status and type values are in `enum DIE_DT`, with `DT_FEMPTY`, `DT_FSINGLE`, `DT_LINK`, `DT_EOS`, `DT_MASK`, and interrupt-enable `D_DIE`. DMA-visible layouts are `struct rtsn_desc`, `struct rtsn_ts_desc`, `struct rtsn_ext_desc`, and `struct rtsn_ext_ts_desc`, all packed. Chain constants select one TX and one RX chain, both size 1024. `PKT_BUF_SZ` and `RTSN_ALIGN` define RX buffer allocation.

## Control Flow Role
This header has no executable control flow, but it controls how `rtsn.c` sequences hardware. AXIBMI constants drive descriptor BAT setup and interrupt enable/disable. TSNMHD constants define mode polling and TX/RX filter setup. RMAC constants encode PHY interface, link speed, MII management operations, MAC address registers, and link verification. Descriptor type constants are used by the TX path to hand descriptors to hardware and by RX/NAPI to detect completed packets and refill empties.

## State And Persistence
The structures in this file define DMA-persistent state shared between CPU and device while the interface is open. Endianness annotations (`__le16`, `__le32`, `__le64`) document hardware little-endian fields. `info_ds` carries packet length and flags, `die_dt` carries ownership/type, `dptr` carries 32-bit DMA pointers, `info1` carries extended metadata, and timestamp descriptors append nanosecond/second fields.

## Dependencies And Integration Points
The header depends only on Linux types but is tightly integrated with `rtsn.c`. Register and descriptor definitions must match the R-Car Gen4 TSN hardware manual and the DMA mask used by probe. It also mirrors some concepts used by `rswitch` descriptors, but it is private to the standalone TSN driver.

## Risks
Any offset or bitfield error can cause silent hardware misconfiguration. The 32-bit `dptr` fields constrain DMA addressability. Packed descriptor layout and endianness must remain stable; compiler padding changes would break DMA. Chain-size constants influence memory pressure, latency, and wrap logic. Some enum values represent currently unused TSN features, so future expansion must confirm offsets rather than assuming naming implies support.

## Test Signals
Compile coverage catches symbol drift. Runtime coverage comes from successful descriptor BAT programming, mode transitions, RX/TX interrupt enable/disable, PHY interface/speed programming, MDIO reads/writes, and correct interpretation of RX/TX descriptors under ring wrap and timestamp traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rtsn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.c

## Purpose
`sh_eth.c` is the legacy Renesas SuperH/R-Car Ethernet platform driver. It supports multiple EtherC/E-DMAC/GETHER variants using per-SoC capability tables, register-offset maps, bitbang MDIO, DMA descriptor rings, NAPI RX, interrupt-driven TX completion, TSU multicast/VLAN filtering, ethtool diagnostics, runtime PM, and optional MagicPacket wake-on-LAN.

## Important APIs, Types, And Functions
The driver state is `struct sh_eth_private` from `sh_eth.h`; hardware capability data is `struct sh_eth_cpu_data`. Register abstraction is through `sh_eth_write()`, `sh_eth_read()`, `sh_eth_modify()`, and TSU equivalents. SoC data instances include `r7s72100_data`, `r8a7740_data`, `rcar_gen1_data`, `rcar_gen2_data`, `r8a77980_data`, `r7s9210_data`, and several SH platform IDs. Main lifecycle functions are `sh_eth_drv_probe()`, `sh_eth_open()`, `sh_eth_close()`, `sh_eth_drv_remove()`, `sh_eth_suspend()`, and `sh_eth_resume()`. Data-plane functions include `sh_eth_ring_init()`, `sh_eth_ring_format()`, `sh_eth_dev_init()`, `sh_eth_start_xmit()`, `sh_eth_interrupt()`, `sh_eth_poll()`, `sh_eth_rx()`, and `sh_eth_tx_free()`. TSU functions manage CAM entries and VLAN filters.

## Control Flow
Probe enables runtime PM, gets IRQ and MMIO, selects platform/OF data, resolves register offsets, fills default SoC values, configures netdev feature flags and ops, reads or generates MAC address, maps optional TSU resources, initializes TSU once for shared dual-port blocks, initializes MDIO, adds NAPI, and registers the netdev. Open gets runtime PM, enables NAPI, requests IRQ, allocates coherent descriptor rings and SKB arrays, initializes hardware registers and descriptors, connects/starts PHY, and starts the TX queue. IRQ handling masks status with `EESIPR`, schedules NAPI for RX, reclaims TX descriptors, handles EMAC link/MagicPacket events, and records error counters. NAPI clears RX interrupt status, processes RX descriptors under budget, refills buffers, restarts RX DMA if needed, completes NAPI, and restores RX interrupts. Close disables queue/IRQs/NAPI, exits hardware, disconnects PHY, frees IRQ and rings, and drops runtime PM.

## State And Persistence
State is volatile and per-netdev. Ring indices `cur_rx`, `dirty_rx`, `cur_tx`, and `dirty_tx` monotonically count descriptors modulo configurable ring sizes. `irq_enabled` prevents NAPI from restoring masks during close or ring resize. `is_opened` gates hardware counter reads. TSU state is partly in hardware CAM/POST registers and `vlan_num_ids`; only one VLAN filter can be active, and adding more disables hardware VLAN filtering. Wake-on-LAN state is `wol_enabled` and device wakeup enablement. SoC tables persist for the module lifetime and are mutated once by `sh_eth_set_default_cpu_data()`.

## Dependencies And Integration Points
The driver integrates with platform resources, OF match data, legacy platform IDs, phylib, OF MDIO, MDIO bitbang, NAPI, DMA API, ethtool register/stat/ring/WoL hooks, VLAN filtering, runtime PM, and the exported platform data type from `<linux/sh_eth.h>`. Device tree properties include `phy-mode`, optional MAC address, `phy-handle`, and Renesas link-policing booleans. TSU resources may be shared across two ports.

## Risks
The SoC capability table is high risk: register offsets, feature flags, and interrupt masks must match silicon. `sh_eth_set_default_cpu_data()` mutates shared static `sh_eth_cpu_data`, so defaults are global after first probe. RX/TX DMA ownership relies on memory barriers before/after descriptor status bits. `sh_eth_tsu_del_entry()` treats `i == 0` as not found due to `if (i)`, which is suspicious because entry 0 is valid. Ring resizing while running must correctly serialize IRQ, NAPI, hardware stop, and ring free/reinit. TSU dual-port sharing requires only port 0 to request/init shared resources. Legacy software byte swapping and direct physical-to-virtual use require architecture assumptions. WoL restore closes and reopens the device, so resume paths must tolerate failures.

## Test Signals
Test probe for each OF/platform ID, register dump length/content, open/close loops, traffic at 10/100/1000 where supported, TX timeout recovery, NAPI budget and RX ring refill failure, ethtool ring resize while running, RX checksum enable/disable, multicast/promiscuous/allmulti transitions, VLAN add/delete including multiple VID behavior, TSU shared dual-port behavior, MDIO reads/writes under runtime PM, suspend/resume with and without WoL, and link change handling for `no_psr`/`no_ether_link` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.h

## Purpose
`sh_eth.h` is the private hardware and state header for the SuperH/R-Car Ethernet driver. It defines register IDs, ring limits, packet buffer sizing, descriptor layouts, register bit masks, TSU constants, SoC capability flags, and the private per-device state consumed by `sh_eth.c`.

## Important APIs, Types, And Constants
The first enum is the canonical register index list used by offset tables and ethtool dumps; new register indices must be inserted before `SH_ETH_MAX_REGISTER_OFFSET`. Register-family IDs are `SH_ETH_REG_GIGABIT`, `SH_ETH_REG_FAST_RCAR`, `SH_ETH_REG_FAST_SH4`, and `SH_ETH_REG_FAST_SH3_SH2`. Descriptor definitions are `struct sh_eth_txdesc` and `struct sh_eth_rxdesc`, with status, length, address, and padding fields. `struct sh_eth_cpu_data` captures per-SoC reset hooks, speed/duplex hooks, initial register values, interrupt masks, and feature booleans. `struct sh_eth_private` stores platform device, capability table, register offsets, MMIO/TSU mappings, rings, SKB arrays, locks, ring indices, NAPI, PHY/MDIO, link state, TSU port/VLAN state, and WoL/open flags.

## Control Flow Role
This header drives conditional control flow in `sh_eth.c`. Capability bits choose register programming, interrupt masks, ethtool dump contents, TSU/VLAN operations, checksum support, link handling, byte swapping, and WoL support. Descriptor bit definitions define ownership transfer between CPU and E-DMAC. Register enum ordering also controls the ABI of ethtool register dumps.

## State And Persistence
The descriptor structs are DMA-shared state for rings allocated at open or ring resize. `sh_eth_private` is netdev-private runtime state and is not persistent across driver remove. `sh_eth_cpu_data` instances are static module data; they become effectively shared immutable configuration after default fields are filled, although the defaulting helper mutates them.

## Dependencies And Integration Points
The header is private to the Renesas driver and expects Linux kernel networking, platform, DMA, NAPI, phylib, ethtool, and MDIO APIs included by the C file. It is indirectly tied to public platform data in `<linux/sh_eth.h>`, hardware manuals for all supported SoCs, and ethtool register-dump consumers that depend on stable register indices.

## Risks
Changing register enum order can break ethtool dump interpretation. Incorrect descriptor alignment or bit definitions can break DMA ownership. Capability flags are densely packed and easy to misuse across SoCs. Ring size constants gate ethtool validation and memory allocation behavior. `SH_ETH_RX_ALIGN` varies by architecture config, so buffer alignment assumptions differ by build target. Static `sh_eth_cpu_data` mutability should be considered before adding per-instance dynamic defaults.

## Test Signals
Build tests should cover OF and non-OF configurations, CPU/architecture variants affecting `SH_ETH_RX_ALIGN`, and all platform ID tables. Runtime signals include successful descriptor DMA, ethtool register dumps with valid maps, SoC-specific feature paths, TSU CAM/VLAN behavior, RX checksum support, and ring parameter boundary validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/sh_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Kconfig

## Purpose
This Kconfig file exposes the Rocker switch driver configuration menu. It defines the vendor gate `NET_VENDOR_ROCKER` and the actual driver option `ROCKER`.

## Important APIs, Types, And Functions
There is no executable code. `NET_VENDOR_ROCKER` is a boolean menu selector defaulting to `y`; disabling it hides Rocker device questions. `ROCKER` is a tristate option named "Rocker switch driver (EXPERIMENTAL)".

## Control Flow
Kconfig control flow is simple: the `ROCKER` option is visible only inside `if NET_VENDOR_ROCKER`. When enabled, it allows built-in or module compilation depending on `y` or `m`.

## State And Persistence
Configuration state persists in the kernel `.config`, not in runtime code. `CONFIG_ROCKER` drives Makefile inclusion and module availability.

## Dependencies And Integration Points
`ROCKER` depends on `PCI`, `NET_SWITCHDEV`, and `BRIDGE`, and selects `CRC32`. These dependencies indicate the driver is a PCI switchdev/bridge integration driver rather than a simple Ethernet MAC.

## Risks
If dependencies are incomplete, the driver may compile without required switchdev/bridge APIs. If `NET_VENDOR_ROCKER` defaults or prompts are changed, defconfig visibility changes. The help text marks the driver experimental but does not enforce experimental config gating.

## Test Signals
Kconfig tests include `CONFIG_ROCKER=m`, `CONFIG_ROCKER=y`, and disabled dependency combinations. Build output should include `rocker.ko` for module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Makefile

## Purpose
This Makefile wires `CONFIG_ROCKER` to the Rocker driver object and defines the component objects that make up `rocker.o`.

## Important APIs, Types, And Functions
There are no C APIs. `obj-$(CONFIG_ROCKER) += rocker.o` adds the driver to the kernel build when the Kconfig option is enabled. `rocker-y := rocker_main.o rocker_tlv.o rocker_ofdpa.o` links the main PCI/netdev logic, TLV helpers, and OF-DPA world implementation into the single driver object.

## Control Flow
Build control is entirely Kbuild-driven. If `CONFIG_ROCKER=y`, objects are linked into the kernel. If `CONFIG_ROCKER=m`, they become the `rocker` module. If unset, none are built.

## State And Persistence
Build state is generated by Kbuild. No runtime persistence exists here.

## Dependencies And Integration Points
This file integrates with the parent Ethernet vendor build and Kconfig. The listed object names reveal the code organization expected by `rocker.h`: a core layer, TLV encoding/decoding, and an OF-DPA implementation.

## Risks
Adding new Rocker source files requires updating `rocker-y`; missing entries can compile headers but omit behavior. Object order can matter if initcall or link-time symbol assumptions are introduced.

## Test Signals
Build `CONFIG_ROCKER=y` and `CONFIG_ROCKER=m`, verify all three component objects compile and link, and confirm module metadata produces `rocker.ko` in module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker.h

## Purpose
`rocker.h` is the private cross-module interface for the Rocker switch driver. It defines core software state for DMA descriptors, rings, ports, the PCI switch device, command callbacks, and the pluggable "world" operations used by the OF-DPA implementation.

## Important APIs, Types, And Functions
`struct rocker_desc_info` describes one mapped descriptor payload and its TLV length. `struct rocker_dma_ring_info` tracks ring size, head/tail, mapped descriptors, descriptor metadata, and ring type. `struct rocker_port` binds a netdev to its parent switch, port numbers, TX/RX NAPI instances, and per-port DMA rings. `struct rocker` stores PCI device, BAR address, MSI-X table, port array/count, switch ID, command/event rings, FIB notifier, world ops, ordered workqueue, and private world state. Exported internal functions include `rocker_cmd_exec()`, `rocker_port_set_learning()`, and `rocker_port_dev_lower_find()`. `struct rocker_world_ops` is the main behavioral vtable.

## Control Flow
The core Rocker code calls world ops for device init/fini, per-port lifecycle, port open/stop, switchdev bridge attributes, VLAN/FDB objects, master link/unlink, neighbor updates, MAC/VLAN learn events, and IPv4 FIB add/delete/abort notifications. Command execution uses caller-provided prepare/process callbacks to encode/decode TLV descriptors.

## State And Persistence
State is in memory and tied to the PCI device lifetime. Descriptor/ring objects mirror hardware DMA queues. Port `wpriv` and device `wpriv` hold world-specific state sized by `rocker_world_ops`. FIB notifier and ordered workqueue preserve asynchronous control-plane work while loaded.

## Dependencies And Integration Points
The header depends on Linux netdevice, notifier, neighbour, and switchdev APIs, plus `rocker_hw.h` for hardware ABI. It connects `rocker_main.c`, `rocker_tlv.c`, and `rocker_ofdpa.c`; `rocker_ofdpa_ops` is declared as the provided world implementation.

## Risks
The world-ops contract is broad; missing callbacks or mismatched ownership rules can leave switchdev state inconsistent. DMA ring metadata must remain synchronized with `rocker_hw.h` descriptor formats. Command callbacks must agree on TLV layout and lifetime. FIB notifier callbacks require careful failure/abort semantics.

## Test Signals
Useful coverage includes PCI probe/remove, port creation/open/stop, command execution with success and hardware errors, bridge join/leave, STP/learning changes, VLAN and FDB add/delete, neighbor update/destroy, FIB route add/delete/abort, and lower-device lookup under stacked netdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_hw.h

## Purpose
`rocker_hw.h` defines the hardware ABI for the Rocker PCI switch device. It contains device IDs, BAR/register layout, MSI-X vector allocation, DMA ring registers and descriptor structures, TLV command/event/RX/TX schemas, OF-DPA flow and group encodings, and general switch control registers.

## Important APIs, Types, And Constants
Return-code constants mirror errno-like hardware results. `PCI_DEVICE_ID_REDHAT_ROCKER`, `ROCKER_PCI_BAR0_SIZE`, and `ROCKER_FP_PORTS_MAX` describe device identity and size bounds. MSI-X macros map command, event, test, and per-port TX/RX vectors. DMA definitions include `enum rocker_dma_type`, ring register offsets, size limits/defaults, `struct rocker_desc`, and `ROCKER_DMA_DESC_COMP_ERR_GEN`. `struct rocker_tlv` is the packed TLV header. The many TLV enums define command types, port settings/statistics, events, RX flags, TX offload/frags, and OF-DPA flow fields. OF-DPA table/group enums and `ROCKER_GROUP_*` macros encode group IDs.

## Control Flow Role
This header has no code paths but dictates all command and data-plane protocol between driver and device. Core code programs DMA rings through the register macros, consumes events using event TLVs, builds TX/RX metadata TLVs, and programs OF-DPA flows/groups using command TLVs. Group ID macros are used by the OF-DPA layer to derive hardware group identifiers from VLAN, port, and index data.

## State And Persistence
DMA descriptors and TLV buffers are hardware-shared runtime state. Register offsets represent MMIO state in BAR0. Group IDs and flow cookies may persist in the device forwarding tables until explicitly deleted or device reset. No host-side durable persistence is defined.

## Dependencies And Integration Points
The header depends on Linux types and bit macros through included kernel headers in users. It integrates tightly with `rocker.h`, `rocker_main.c`, `rocker_tlv.c`, and `rocker_ofdpa.c`, and externally with PCI, switchdev, bridge, neighbour, and FIB subsystems.

## Risks
This file is an ABI contract: changing enum values, TLV IDs, descriptor layout, register offsets, or group encoding breaks compatibility with the Rocker device/emulator. `struct rocker_desc` uses fixed-width fields and expected alignment. The `ROCKER_GROUP_VLAN_GET()` macro references `ROCKER_GROUP_VLAN_ID_MASK`/`SHIFT`, while the file defines `ROCKER_GROUP_VLAN_MASK`/`SHIFT`; that should be checked because it may be a latent macro-name defect unless provided elsewhere. TX fragment and ring-size limits must match the device. TLV length/type parsing must defend against malformed hardware data.

## Test Signals
Tests should exercise PCI BAR size checks, reset/control registers, MSI-X vector count for multiple port counts, DMA ring reset/head/tail/credit handling, command TLV round trips, event TLV parsing for link and MAC/VLAN events, RX checksum/offload flags, TX checksum/TSO/fragments up to `ROCKER_TX_FRAGS_MAX`, OF-DPA flow add/mod/del/stats, group ID encode/decode, and build coverage of all macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_hw.h -->
