# sources/distributed-fs/ceph-client/arch/m68k/emu/nfeth.c

Purpose: ARAnyM NatFeat Ethernet driver exposing up to eight emulated Ethernet interfaces to Linux networking.

Important APIs and data: NatFeat command enum (`XIF_*`), `struct nfeth_private`, `nfeth_open()`, `nfeth_stop()`, `recv_packet()`, `nfeth_interrupt()`, `nfeth_xmit()`, `nfeth_tx_timeout()`, `nfeth_netdev_ops`, `nfeth_probe()`, `nfeth_init()`, and `nfeth_cleanup()`.

Control flow and state: init gets `ETHERNET`, reads API version and interrupt level, requests a shared IRQ, then probes units by asking for MAC addresses. Open starts the emulator receiver and queue; stop stops both. IRQ handler obtains a unit bitmask, receives pending packets into skbs, acknowledges each unit bit, and passes packets to `netif_rx`. Transmit pads short Ethernet frames and calls `XIF_WRITEBLOCK`.

Dependencies and integration: NatFeat base, Linux netdevice/etherdevice APIs, physical buffer addressing, and ARAnyM Ethernet ABI.

Risks and test signals: RX/TX NatFeat return values are mostly ignored; malformed packet lengths can stress allocation; request_irq uses the handler address as `dev_id`. Test multiple units, ifup/ifdown, RX/TX packet counters, short-frame padding, interrupt masks, and cleanup after partial probe failure.
