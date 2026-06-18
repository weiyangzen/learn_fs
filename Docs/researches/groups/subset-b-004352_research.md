# subset-b-004352 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.c

## Purpose
Implements the Linux `b44` Fast Ethernet driver for Broadcom 44xx/47xx 10/100 devices exposed through SSB and, when enabled, PCI-hosted SSB. It owns MAC/PHY setup, DMA descriptor rings, NAPI RX/TX completion, ethtool controls, multicast filtering, wake-on-LAN programming, suspend/resume, and module registration.

## Important APIs, Types, and Functions
The driver registers an `ssb_driver` (`b44_ssb_driver`) and optional PCI host bridge driver, and exposes a `net_device` via `b44_netdev_ops`. Core lifecycle functions are `b44_init_one`, `b44_remove_one`, `b44_open`, `b44_close`, `b44_suspend`, and `b44_resume`. Hardware access is wrapped by `br32`/`bw32`, `b44_wait_bit`, MDIO helpers (`__b44_readphy`, `__b44_writephy`, phylib and mii-lib adapters), reset helpers (`b44_chip_reset`, `b44_init_hw`, `b44_halt`), ring helpers (`b44_alloc_consistent`, `b44_init_rings`, `b44_alloc_rx_skb`, `b44_recycle_rx`, `b44_free_rings`), and packet paths (`b44_start_xmit`, `b44_interrupt`, `b44_poll`, `b44_rx`, `b44_tx`). Ettool coverage includes link settings, pause, ring sizes, statistics, message level, and WOL.

## Control Flow
Probe allocates the netdev, powers the SSB bus, sets the required 30-bit DMA mask, reads SPROM invariants, initializes MII/phylib state, registers the netdev, resets the chip, and optionally registers an external PHY. Open allocates coherent or fallback DMA rings, enables NAPI, fills RX descriptors, initializes hardware, requests the shared IRQ, starts a one-second timer for PHY/stat polling, enables interrupts, starts external phylib if present, and starts the TX queue. Interrupt handling masks device interrupts, stores the interrupt status, acknowledges hardware, and schedules NAPI. NAPI first reclaims TX, handles RX FIFO overflow by fast reset, receives packets up to budget, and performs full reset on error bits before re-enabling interrupts. TX maps an skb into one descriptor, handles the chip's 30-bit DMA limitation with a GFP_DMA bounce skb, posts `B44_DMATX_PTR`, and stops the queue when descriptors are exhausted. RX reads the device consumer pointer, syncs the DMA buffer, validates `struct rx_header`, either hands up the mapped skb or copies small/forced-copybreak frames, recycles/refills the ring, updates `B44_DMARX_PTR`, and passes packets to the stack.

## State and Persistence
Persistent runtime state is in `struct b44`: descriptor producer/consumer indices, DMA ring addresses, skb/mapping arrays, flags for link/pause/PHY/DMA quirks/WOL, MII bus state, timer, NAPI object, interrupt mask/status, and accumulated 64-bit hardware stats. Hardware state lives in SSB/MAC registers, CAM entries, MIB counters, descriptor tables, PHY registers, and WOL pattern tables. The driver uses `bp->lock` for register/ring state, `u64_stats_sync` for stats snapshots, timer state for periodic link/stat polling, and device wakeup state for WOL.

## Dependencies and Integration Points
Depends on SSB core APIs, optional PCI host support, DMA mapping, NAPI/netdevice, phylib and mii-lib, fixed PHY fallback for boards with integrated switches, ethtool, `b44.h` register definitions, `linux/brcmphy.h`, and BCM47xx NVRAM for the WAP54G workaround. It integrates with Kconfig/Makefile through `CONFIG_B44`, `CONFIG_B44_PCI`, and `CONFIG_BCM47XX`, and with userspace through netdev, ethtool, MII ioctls, WOL, and network statistics.

## Risks and Test Signals
Important risks are 30-bit DMA handling regressions, descriptor ownership/order bugs, missing descriptor sync on ring-hack paths, RX recycle/refill leaks, reset sequencing around PHY powerdown, external PHY/fixed PHY attachment failures, CAM multicast limits, WOL pattern programming, and races between IRQ, NAPI, timer, suspend/resume, and close. Test signals include module probe/remove on PCI and SSB variants, DHCP/ping/iperf RX/TX under load, forced TX timeout recovery, RX FIFO overflow recovery, ethtool ring/pause/link-setting changes, multicast/promiscuous mode, MII ioctl behavior, suspend/resume with and without WOL, netpoll builds, DMA mapping error injection, and hardware stat consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.h

## Purpose
Defines the `b44` hardware contract consumed by `b44.c`: MAC, DMA, MDIO, CAM, wake filter, and MIB register offsets; descriptor and RX-header layouts; statistics layout; board flags; and the private per-device state structure.

## Important APIs, Types, and Functions
There are no callable functions. Important data definitions are `struct dma_desc`, `struct rx_header`, `struct ring_info`, `struct b44_hw_stats`, and `struct b44`. Macro groups define `B44_DEVCTRL`, interrupt status/mask bits, DMA TX/RX control and status fields, EMAC RX/TX/MDIO/CAM registers, descriptor control bits (`DESC_CTRL_*`), RX status/error bits, MII auxiliary registers, MIB counter registers, `B44_STAT_REG_DECLARE`, board flags, PHY sentinel addresses, and driver flags such as `B44_FLAG_EXTERNAL_PHY`, `B44_FLAG_RX_RING_HACK`, and `B44_FLAG_WOL_ENABLE`.

## Control Flow
This header has no runtime control flow. It shapes control flow in `b44.c` by encoding which register bits are polled, masked, written, or interpreted in reset, MDIO, RX/TX, WOL, and ethtool paths. `B44_STAT_REG_DECLARE` is deliberately used both for string generation and `struct b44_hw_stats` layout, so the C file can iterate hardware MIB counters into a matching software layout.

## State and Persistence
The header describes three layers of state. Hardware state is represented by register offsets and bit masks. DMA-visible state is represented by little-endian descriptor and RX header structures, including the chip-specific RX header placed before packet data. Software state is represented by `struct b44`, which persists ring pointers, DMA addresses, indices, NAPI/timer objects, PHY and MII bus handles, flags, counters, and the owning `ssb_device`/`net_device`.

## Dependencies and Integration Points
Includes `linux/brcmphy.h` for Broadcom pseudo-PHY constants and references kernel networking, DMA, MII, NAPI, timer, SSB, and sk_buff types through declarations used by `b44.c`. The register definitions are local to the `b44` driver but must remain synchronized with the hardware and with the implementation's assumptions about descriptor size, 4096-byte DMA table alignment, MIB counter order, and PHY address meanings.

## Risks and Test Signals
The main risk is hardware ABI drift: a wrong bit mask, endian-sensitive field, descriptor length, flag value, or counter order can cause silent packet loss, bad resets, wrong ethtool stats, or unsafe DMA. Test signals are compile coverage for all `CONFIG_B44*` combinations, exercising RX/TX and error paths on real 44xx/47xx hardware, comparing ethtool stats against MIB activity, validating WOL and CAM programming, and checking that descriptor rings remain 4096-byte aligned with correct wrap/EOT behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/b44.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.c

## Purpose
Implements the platform driver for the Broadcom BCM4908 internal Gigabit Ethernet MAC. It provides a single netdev backed by UMAC registers and two DMA channels/rings, with NAPI-based RX and TX cleanup and device-tree probing.

## Important APIs, Types, and Functions
Private types are `struct bcm4908_enet_dma_ring_bd`, `struct bcm4908_enet_dma_ring_slot`, `struct bcm4908_enet_dma_ring`, and `struct bcm4908_enet`. Register access helpers are `enet_read`, `enet_write`, `enet_maskset`, UMAC wrappers, and `bcm4908_enet_set_mtu`. DMA helpers allocate/free rings (`bcm4908_enet_dma_alloc`, `bcm4908_dma_alloc_buf_descs`, `bcm4908_enet_dma_free`), reset/init/uninit channels, allocate RX frags, enable/disable rings, and mask/ack ring interrupts. Network entry points are `bcm4908_enet_open`, `bcm4908_enet_stop`, `bcm4908_enet_start_xmit`, `bcm4908_enet_poll_rx`, `bcm4908_enet_poll_tx`, `bcm4908_enet_change_mtu`, `bcm4908_enet_probe`, and `bcm4908_enet_remove`.

## Control Flow
Probe devm-allocates the netdev, maps MMIO, obtains named RX and optional TX IRQs, sets a 32-bit coherent DMA mask, allocates fixed 200-entry TX/RX descriptor rings and slot arrays, reads the MAC address from OF or generates a random one, installs netdev ops, adds RX and TX NAPI instances, and registers the netdev. Open requests RX and optional TX IRQs, initializes UMAC for 1000 Mbps with auto config and link-up status, resets DMA state RAM, allocates all RX buffers, initializes ring base pointers, enables UMAC TX/RX, enables DMA master, enables NAPI/interrupts, marks carrier on, and starts the queue. The IRQ handler selects TX or RX ring based on IRQ number, disables and acknowledges ring interrupts, and schedules that ring's NAPI. TX checks descriptor availability, maps skb data, writes one SOP/EOP/CRC descriptor with OWN, kicks the TX channel, and advances the write pointer. RX consumes descriptors whose OWN bit is clear, allocates a replacement buffer before unmapping the completed one, validates length and SOP/EOP, builds an skb from the frag, strips FCS, submits it to the stack, updates stats, and re-enables interrupts when budget is not exhausted. Stop disables queue/carrier/NAPI, disables DMA rings, frees RX buffers, and releases IRQs.

## State and Persistence
Driver state is in `struct bcm4908_enet` and each ring: MMIO base, IRQs, netdev/device pointers, descriptor memory, DMA addresses, slots, read/write indices, NAPI objects, and ring config/state-RAM offsets. RX slots own page fragments until consumed or freed; TX slots own skbs until completion. Hardware state is persistent across open while the device is running: UMAC command/max-frame registers, GMAC status, DMA controller config, channel config, interrupt masks/status, state RAM base descriptors, and descriptor OWN/WRAP/SOP/EOP bits.

## Dependencies and Integration Points
Depends on platform device and OF matching (`brcm,bcm4908-enet`), `of_get_ethdev_address`, DMA mapping, NAPI/netdevice, interrupt APIs, `bcm4908_enet.h` register definitions, and shared `unimac.h` command/max-frame definitions. Build integration is via `CONFIG_BCM4908_ENET` and `bcm4908_enet.o`.

## Risks and Test Signals
Risks include fixed 32-bit descriptor address truncation, descriptor wrap off-by-one behavior because the code intentionally keeps one slot empty, missing error handling for `bcm4908_enet_dma_init` in open, optional TX IRQ handling with polling fallback, RX replacement allocation failures, DMA unmap length mismatches, stop calling `free_irq` on an absent TX IRQ, and link state being forced rather than PHY-driven. Test signals include probe from DT with/without `tx` IRQ and MAC address, sustained RX/TX traffic, queue stop/wake behavior, NAPI budget exhaustion, MTU changes, RX allocation failure paths, DMA mapping failure injection, IRQ masking/ack behavior, and remove/open/stop leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.h

## Purpose
Provides the BCM4908 ENET register map and descriptor control/status bit definitions used by `bcm4908_enet.c`.

## Important APIs, Types, and Functions
This header is macro-only. It defines top-level ENET control, MIB, GMAC status, FIFO flush, flow control, DMA controller, DMA channel config, DMA channel state RAM, and DMA descriptor control/status fields. Key fields include `ENET_DMA_CTRL_CFG_MASTER_EN`, per-channel interrupt status/mask bits (`BUFF_DONE`, `DONE`, `NO_DESC`, `RX_ERROR`), descriptor `DMA_CTL_STATUS_OWN`, `SOP`, `EOP`, `WRAP`, `APPEND_CRC`, and the buffer length mask/shift.

## Control Flow
There is no executable control flow. The implementation uses these constants to select the RX and TX channel blocks, reset DMA state, program descriptor base pointers, mask/ack interrupts, force GMAC status, flush FIFOs, and encode/decode descriptors in the RX/TX NAPI paths.

## State and Persistence
The header describes persistent hardware state in MMIO registers and DMA descriptor words. Descriptor state is shared between software and hardware: software sets OWN, length, WRAP, SOP/EOP, and address fields; hardware clears OWN and writes completion length/status. Channel state RAM persists ring base and current descriptor information while DMA is active.

## Dependencies and Integration Points
Consumed directly by `bcm4908_enet.c` and indirectly tied to `unimac.h` for the UMAC sub-block. It must match the BCM4908 hardware manual and the driver's assumption that channel 0 is RX, channel 1 is TX, and descriptor addresses fit in 32 bits.

## Risks and Test Signals
Risks are incorrect offsets or descriptor bit definitions causing DMA stalls, lost interrupts, false link/speed status, or corrupt skb lengths. Test signals are compile coverage, descriptor dumps under RX/TX load, interrupt status/mask validation, DMA no-descriptor recovery, and comparing register values against known-good bootloader or vendor driver programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.c

## Purpose
Implements Broadcom BCM63xx Ethernet support for two related platform devices: the internal Ethernet MAC (`bcm63xx_enet`) and the integrated Ethernet switch CPU-facing netdev (`bcm63xx_enetsw`). It manages shared DMA register windows, MAC/switch MMIO, MDIO, PHY or forced-link setup, descriptor rings, NAPI RX/TX, MIB statistics, ethtool controls, and module registration of the shared, MAC, and switch platform drivers.

## Important APIs, Types, and Functions
Register access is split across `enet_*` MAC helpers, `enetsw_*` switch helpers, and shared DMA helpers (`enet_dma_*`, `enet_dmac_*`, `enet_dmas_*`). MDIO paths include `do_mdio_op`, MAC MDIO adapters, switch MDIO adapters, and MII ioctl wrappers. Shared packet machinery includes `bcm_enet_refill_rx`, `bcm_enet_receive_queue`, `bcm_enet_tx_reclaim`, `bcm_enet_poll`, `bcm_enet_isr_dma`, and `bcm_enet_start_xmit`. MAC-specific lifecycle and controls are `bcm_enet_probe`, `bcm_enet_open`, `bcm_enet_stop`, `bcm_enet_remove`, `bcm_enet_hw_preinit`, link adjustment, multicast/MAC address, MTU, and `bcm_enet_ethtool_ops`. Switch-specific lifecycle and controls are `bcm_enetsw_probe`, `bcm_enetsw_open`, `bcm_enetsw_stop`, `bcm_enetsw_remove`, `swphy_poll_timer`, switch MII ioctl, switch stats, and `bcm_enetsw_ethtool_ops`. `bcm_enet_shared_probe` maps the shared DMA windows before either functional driver can probe.

## Control Flow
Module init registers three platform drivers. The shared driver maps three shared DMA resource windows into `bcm_enet_shared_base`; MAC and switch probes defer until that is present. MAC probe allocates a netdev, maps MAC registers, enables MAC and optional internal PHY clocks, loads platform data for DMA channels/PHY/link/pause/MAC address, preinitializes hardware for MDIO, registers an MII bus or calls board MII setup, initializes timers/work, clears MIB counters, installs netdev/ethtool ops, and registers the netdev. MAC open connects phylib when present, requests MAC/RX/TX IRQs, allocates RX/TX coherent descriptor rings and skb arrays, fills RX descriptors, programs ring base/state, configures MTU, burst and flow-control thresholds, enables MAC/DMA, enables MIB and packet interrupts, enables NAPI, starts PHY or forced link, and starts the queue. The DMA IRQ masks RX/TX interrupts and schedules NAPI; NAPI acknowledges interrupts, reclaims TX, receives RX packets, refills descriptors, kicks RX DMA, completes NAPI, and unmasks interrupts. Stop reverses the sequence, disables interrupts/DMA/MAC, cancels MIB work and RX refill timer, force-reclaims TX, frees RX buffers/rings, frees IRQs, disconnects PHY, and resets BQL.

For switch devices, probe uses platform switch port data, maps the switch block, enables the switch clock, sets switch-specific burst/buffer offsets, and registers a netdev using the shared RX/TX machinery. Switch open requests RX and optional TX IRQs, allocates rings, disables all ports, resets switch MIBs, forces the CPU port up, enables forwarding/jumbo, configures DMA and interrupts, applies bypass-link port overrides, marks carrier on, starts the queue, and starts a one-second software PHY polling timer. The timer polls used ports over internal/external switch MDIO, derives speed/duplex from advertised/LPA values including gigabit status, and updates switch port override/control registers.

## State and Persistence
All runtime state is held in `struct bcm_enet_priv`: MMIO base, IRQs, DMA channels and masks, descriptor memory, RX/TX indices/counts, RX frag sizing, skb arrays, NAPI object, clocks, PHY/MII state, forced link/pause settings, MIB accumulation, timers/work, platform device/netdev pointers, switch port configuration, and shared-DMA feature flags. Hardware state persists in MAC/switch registers, shared DMA controller/state RAM, descriptor ownership bits, MIB counters, MDIO-accessed PHY registers, switch port override/control registers, and flow-control thresholds. `copybreak` is a module parameter affecting RX copy versus build-skb behavior.

## Dependencies and Integration Points
Depends on BCM63xx platform data from `<bcm63xx_dev_enet.h>`, register and DMA definitions from `<bcm63xx_regs.h>`, `<bcm63xx_io.h>`, and `<bcm63xx_iudma.h>`, platform devices, clocks, DMA mapping, interrupts, NAPI/netdevice, phylib and mii-lib, ethtool, CRC/multicast support, VLAN sizing, and `bcm63xx_enet.h`. Build integration is via `CONFIG_BCM63XX_ENET`; platform driver names are `bcm63xx_enet_shared`, `bcm63xx_enet`, and `bcm63xx_enetsw`.

## Risks and Test Signals
Risks include shared-resource probe ordering, platform-data mismatches for DMA masks/channel widths/descriptor shifts, RX refill OOM timer races, descriptor ownership/barrier mistakes, TX reclaim racing xmit, `bcm_enet_set_ringparam` accepting unchecked zero or huge ring sizes, no DMA mapping error checks in several TX/RX paths, MIB work racing shutdown, switch PHY polling stale link state, switch stats register mapping mistakes, and different behavior between SRAM and non-SRAM DMA engines. Test signals include boot/probe on MAC-only and switch SoCs, traffic through internal MAC and switch CPU port, ring-size changes while running, copybreak variations, MTU boundary tests, forced-link and phylib link changes, pause/autoneg settings, multicast/promiscuous programming, MII ioctls, MIB overflow interrupts and ethtool stats, RX allocation failure recovery, DMA IRQ masking/unmasking, switch port link up/down polling, bypass-link port configuration, and remove/stop leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.h

## Purpose
Defines constants and private state for the BCM63xx Ethernet MAC/switch driver. It centralizes default ring sizes, DMA burst limits, MTU limits, MIB counter indexes for MAC and switch blocks, the software MIB accumulator, and `struct bcm_enet_priv`.

## Important APIs, Types, and Functions
The header has no functions. Important constants are `BCMENET_DEF_RX_DESC`, `BCMENET_DEF_TX_DESC`, `BCMENET_DMA_MAXBURST`, `BCMENETSW_DMA_MAXBURST`, `BCMENET_TX_FIFO_TRESH`, and `BCMENET_MAX_MTU`. It enumerates MAC MIB indexes (`ETH_MIB_*`) and switch MIB indexes (`ETHSW_MIB_*`). `struct bcm_enet_mib_counters` stores accumulated or sampled statistics for both MAC and switch paths. `struct bcm_enet_priv` is the main driver-private object for both `bcm63xx_enet` and `bcm63xx_enetsw`.

## Control Flow
There is no direct runtime control flow. The layout of `struct bcm_enet_priv` drives the C file's lifecycle: probe initializes platform/clock/PHY/DMA fields, open allocates and programs ring fields, NAPI mutates RX/TX indices and counts, ethtool reads/writes ring/pause/link fields, timers use `rx_timeout` and `swphy_poll`, and remove/stop free resources based on pointers and flags stored here.

## State and Persistence
The private state covers MMIO base, IRQs, coherent descriptor DMA addresses and sizes, RX/TX descriptor rings, ring counters and cursor indices, RX buffer sizing and fragment pointers, timers, locks, PHY/MII state, forced link and pause settings, MIB counters, workqueue/mutex protection for stats, MAC/PHY clocks, device references, hardware MTU, switch-vs-MAC mode, switch port map/link cache, DMA channel masks, SRAM capability, channel width, and descriptor shift. The MIB register constants describe persistent hardware counters that are read and folded into software counters.

## Dependencies and Integration Points
Includes kernel types plus MII, mutex, PHY, and platform-device APIs, and BCM63xx-specific `bcm63xx_regs.h`, `bcm63xx_io.h`, and `bcm63xx_iudma.h`. It also depends on platform data types such as `struct bcm63xx_enetsw_port` and `ENETSW_MAX_PORT` from BCM63xx headers. It is consumed by `bcm63xx_enet.c` only, but it defines the shared contract between the MAC and switch halves of that file.

## Risks and Test Signals
Risks are structural: incorrect field types or MIB indexes can corrupt stats or descriptor control; wrong defaults can break low-memory devices; mismatched `dma_desc_shift` assumptions can set wrong wrap/SOP/EOP bits; and switch port array sizing must match platform data. Test signals are all BCM63xx build variants, MAC and switch probe/open/stop, ethtool stats/ring output, MIB counter rollover tests, RX/TX descriptor wrap tests, MTU boundary checks, and switch port polling with all valid `ENETSW_MAX_PORT` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm63xx_enet.h -->
