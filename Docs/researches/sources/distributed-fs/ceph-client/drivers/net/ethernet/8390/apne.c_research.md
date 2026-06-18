# sources/distributed-fs/ceph-client/drivers/net/ethernet/8390/apne.c

Purpose: Amiga 1200 PCMCIA NE1000/NE2000-compatible Ethernet driver using the exported normal 8390 core. It handles Amiga PCMCIA tuple parsing/configuration, fixed I/O window setup, IRQ wrapping, card probing, remote-DMA data movement, and module lifetime.

Important APIs, types, and functions: major paths are `apne_probe()`, `apne_probe1()`, `apne_reset_8390()`, `apne_get_8390_hdr()`, `apne_block_input()`, `apne_block_output()`, `apne_interrupt()`, `init_pcmcia()`, `apne_module_init()`, and `apne_module_exit()`. It fills `ei_status` callbacks and then calls `NS8390_init()`.

Control flow: module init probes only on Amiga with PCMCIA present and a card inserted. It disables PCMCIA IRQs, validates the network function tuple, programs PCMCIA config/offset, requests I/O region `0x300`, resets the card, reads the station-address PROM through 8390 remote DMA, detects 8-bit versus 16-bit access and NE/Ctron variants, requests `IRQ_AMIGA_PORTS`, initializes `struct ei_device`, registers the netdev, and re-enables PCMCIA IRQs. The interrupt wrapper validates/acks Gayle PCMCIA interrupt state around `ei_interrupt()`.

State and persistence: global `apne_owned` prevents multiple claims and `apne_dev` stores the module device. Per-device state is in `struct ei_device`: word width, TX/RX pages, callbacks, and debug level. PCMCIA hardware configuration persists until module exit resets the card.

Dependencies and integration points: depends on Amiga hardware macros, Gayle/PCMCIA helpers, ISA-style port I/O, the exported `ei_*` core, `request_region()`, and `IRQ_AMIGA_PORTS`.

Risks: comments note early returns after tuple/config failures leave PCMCIA IRQ disabled. The driver uses fixed I/O base `0x300` and one global device. Remote-DMA operations depend on `ei_status.dmaing` discipline and 20 ms RDC timeouts. Manual config blocks are compile-time only.

Test signals: Amiga PCMCIA tuple detection, successful config-byte programming, reset ACK, valid MAC read, NE1000/NE2000 word-width detection, registered netdev, IRQ ack/reenable behavior, TX RDC completion, RX ring wrap handling, and clean module unload restoring IRQ/card state.
