# sources/distributed-fs/ceph-client/drivers/net/ethernet/korina.c

## Purpose
`korina.c` implements the IDT RC32434/Korina on-chip Ethernet controller as a platform driver. It manages MAC registers, separate RX and TX DMA register blocks, fixed-size descriptor rings, MII management, periodic media polling, NAPI RX processing, TX completion interrupts, and Device Tree platform binding.

## Important APIs, Types, And Functions
Hardware layout is described by `struct eth_regs`, `struct dma_reg`, and `struct dma_desc`. Runtime state is `struct korina_private`, containing mapped MAC/DMA registers, coherent RX/TX rings, skb and DMA-address arrays, ring indexes, chain status, IRQs, NAPI, MII state, media timer, restart work, and clock-derived MDIO frequency.

Key functions are `korina_probe()`, `korina_open()`, `korina_close()`, `korina_init()`, `korina_alloc_ring()`, `korina_free_ring()`, `korina_send_packet()`, `korina_tx()`, `korina_rx()`, `korina_poll()`, RX/TX DMA IRQ handlers, `korina_mdio_read()`, `korina_mdio_write()`, `korina_check_media()`, and `korina_restart_task()`. Integration surfaces are `korina_netdev_ops`, `netdev_ethtool_ops`, `korina_driver`, and `korina_match`.

## Control Flow
Probe allocates an Ethernet device with devres, loads or randomizes the MAC address, enables an optional `mdioclk`, maps named resources `emac`, `dma_rx`, and `dma_tx`, allocates coherent descriptor rings with `dmam_alloc_coherent()`, initializes locks/NAPI/MII, registers the netdev, and sets up the media timer and restart work.

Open calls `korina_init()` before IRQ registration. Initialization aborts any running DMA, resets the Ethernet logic, allocates and initializes rings, starts RX DMA at descriptor zero, unmasks DMA interrupts, programs address filters and MAC timing, configures MII clocking, enables RX, checks media, enables NAPI, and starts the queue. RX IRQ masks DONE/HALT/ERR and schedules NAPI; `korina_poll()` processes complete descriptors, replaces buffers, sends good packets with GRO, refreshes descriptors, restarts halted RX DMA, and unmasks IRQs after NAPI completes. TX maps a packet into the next descriptor, updates the chain or next-descriptor pointer depending on DMA activity, and TX IRQ cleanup frees completed skbs, updates stats, wakes the queue, and starts deferred chains.

## State And Persistence
Ring indexes and chain state (`rx_next_done`, `tx_next_done`, `tx_chain_head`, `tx_chain_tail`, `tx_chain_status`, `tx_count`, `tx_full`) persist for each open instance. The media timer polls link once per second through MII helpers and updates full-duplex MAC state. Restart work is scheduled on TX timeout and reconstructs rings and hardware state. The driver does not use persistent nonvolatile state beyond the configured MAC address and PHY settings exposed through MII/ethtool.

## Dependencies And Integration Points
The driver depends on platform resources, optional clocks, Device Tree compatible `idt,3243x-emac`, named MMIO resources, Linux DMA mapping, NAPI, MII library, ethtool link settings, timers, workqueues, and optional netpoll. It assumes fixed RX buffer size `KORINA_RBSIZE` and fixed 64-entry RX/TX rings.

## Risks
`korina_alloc_ring()` can leak already allocated RX skbs or DMA mappings if allocation or mapping fails mid-loop before `korina_free_ring()` sees fully initialized state. The RX DMA abort loop busy-waits for HALT while only updating the watchdog timestamp. `korina_restart_task()` disables IRQs and returns immediately on failed `korina_init()`, which can leave the interface in a partially disabled state. The driver supports only default-size receive buffers, so MTU above 1500 is not supported. The MDIO wait helper appears to poll for the busy bit being set rather than cleared, so hardware behavior should be verified carefully before modifying it.

## Test Signals
Probe tests should cover DT resources and optional clock absence/presence. Runtime tests should exercise open/close, RX flood, TX ring-full behavior, TX timeout restart, multicast/promiscuous/all-multicast filters, MII ioctl and ethtool link setting changes, DMA error IRQs, allocation failure during ring setup and RX replacement, and removal while the timer/work paths are active.
