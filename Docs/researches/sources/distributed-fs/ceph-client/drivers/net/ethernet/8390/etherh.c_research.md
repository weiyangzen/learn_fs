# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/etherh.c

Purpose: Acorn expansion-card driver for I-cubed EtherH and ANT EtherM NS8390 Ethernet boards. It embeds `lib8390.c`, maps ecard MEMC/IOC resources, handles card-specific register spacing and DMA windows, supports 10BASE-T/BNC media selection, and exposes ethtool link settings.

Important APIs, types, and functions: `struct etherh_priv` stores mapped control/data windows and media state; `struct etherh_data` describes per-product offsets, supported media, and ring pages. Key paths are `etherh_probe()`, `etherh_remove()`, `etherh_open()`, `etherh_close()`, `etherh_setif()`, `etherh_getifstat()`, `etherh_reset()`, `etherh_block_input()`, `etherh_block_output()`, `etherh_get_header()`, `etherh_set_link_ksettings()`, and ecard IRQ enable/disable ops.

Control flow: module init prepares EtherH/EtherM register offset tables and registers an ecard driver. Probe requests ecard resources, allocates a netdev with extra private data, maps MEMC and optionally IOCFAST, configures IRQ control, obtains MAC from ecard chunks or system serial, fills `struct ei_device` callbacks/pages, resets and initializes the 8390 stopped, then registers the netdev. Open requests IRQ, optionally auto-detects TP versus BNC, sets media, resets, and opens the core.

State and persistence: per-device state includes mapped control byte shadow, product ID, supported media mask, chosen `if_port`, automedia flag, ecard IRQ data, and standard 8390 state. The control-port shadow persists across media/IRQ changes.

Dependencies and integration points: depends on ARM Acorn ecard APIs, MEMC/IOC mappings, ethtool, netdevice, and the included 8390 core. Product tables cover ANT EtherM and EtherLan 500/600/600A.

Risks: EtherM MAC generation from system serial can fail or produce assumptions external to the card. Some cards lack hard reset; `etherh_reset()` mainly stops the chip and optionally toggles media. Remote-DMA transfer paths rely on exact offsets and 16-bit word mode. Auto-media uses short delays and hardware heartbeat/status bits.

Test signals: ecard probe/remove, MAC acquisition, IRQ enable/disable via ecard ops, TP/BNC selection through ifmap and ethtool, automedia fallback, TX/RX with ring wrap, RDC timeout recovery, and correct register offset tables for EtherH versus EtherM.
