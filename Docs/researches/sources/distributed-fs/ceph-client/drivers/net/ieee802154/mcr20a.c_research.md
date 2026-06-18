# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.c

## Purpose
`mcr20a.c` is a SPI mac802154 driver for NXP MCR20A 802.15.4 transceivers. It combines regmap-backed direct/indirect register access with raw async SPI packet-buffer transfers and implements channel, CCA, TX power, address filtering, RX, TX, and IRQ sequencing.

## Important APIs, types, and functions
`struct mcr20a_local` stores SPI, hw, DAR/IAR regmaps, prepared SPI messages for TX, RX, register, and IRQ status flows, plus `is_tx` and current `tx_skb`. Register policy is in `mcr20a_dar_*()` and `mcr20a_iar_*()`. Core functions include `mcr20a_xmit()`, `mcr20a_start()`, `mcr20a_stop()`, `mcr20a_set_channel()`, address/CCA/txpower/promiscuous setters, `mcr20a_irq_isr()`, and chained async completion handlers.

## Control flow
Probe resets the chip with `rst_b`, allocates hw/private data, initializes SPI message templates, creates DAR/IAR regmaps, sets phy capabilities, runs `mcr20a_phy_init()`, requests an initially disabled IRQ, and registers hw. Start enables IRQ, unmasks sequence interrupts, and starts RX. TX first forces IDLE, then IRQ sequence completion writes the packet buffer, sets TX sequence, waits for TX IRQ, completes mac802154 transmit, and restarts RX. RX IRQ reads frame length, then packet data plus LQI, strips FCS, and injects an skb.

## State and persistence
State is volatile: cached regmaps, prepared SPI message structs, current TX skb, `is_tx`, programmed address filters, and hardware sequence state. No file or firmware persistence is performed.

## Dependencies and integration points
The driver integrates with SPI, regmap, GPIO reset, IRQ trigger type, mac802154/cfg802154, skbuff, and constants from `mcr20a.h`.

## Risks and test signals
Risks are concentrated in async SPI message reuse, IRQ disable/enable ordering, `is_tx` races, RX length minus FCS underflow if invalid length handling is wrong, ignored regmap errors in filter setters, and CCA ED setters returning success for unsupported levels. Test signals include register access policy tests, probe failure unwinding, start/stop IRQ state, TX with and without ACK, RX length/LQI paths, channel PLL programming, CCA mode/threshold mapping, promiscuous filtering, and removal during idle/TX/RX.
