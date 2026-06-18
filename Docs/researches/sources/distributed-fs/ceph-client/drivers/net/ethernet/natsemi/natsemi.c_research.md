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
