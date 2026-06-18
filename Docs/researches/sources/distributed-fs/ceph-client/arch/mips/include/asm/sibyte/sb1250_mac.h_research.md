# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_mac.h

Purpose: defines Ethernet MAC register bitfields shared by SB1250-compatible SiByte MAC blocks. It supports MAC configuration, enable/reset, DMA control, FIFO thresholds, frame timing, VLAN, interrupt/status, debug counters, address filters, packet-type filters, receive channel selection, and MII/MDIO control.

Important APIs/types/functions: the API is macro families for `MAC_CFG`, `MAC_ENABLE`, reset info, `MAC_TXD_CTL`, FIFO threshold registers, frame configuration, VLAN tag, status/interrupt mask, FIFO pointers/EOP counts, exact/hash/mask address filter registers, source address, packet type config, address-filter control, RX channel select, and MDIO pins. Enumerants cover speed, bypass modes, flow-control commands, IFG defaults per speed, slot/min/max frame sizes, and jumbo frame maximums.

Control flow: drivers program configuration and frame timing, set filters and addresses, enable RX/TX paths, configure DMA thresholds, handle MAC status interrupts by channel, and bit-bang or drive MDIO to access PHYs. Status-channel offset macros allow common ISR logic across RX/TX channel groups.

State and persistence: MAC configuration, filters, VLAN, thresholds, and MDIO output state persist in hardware. Status, FIFO pointers, counters, and interrupt bits reflect live device state.

Dependencies and integration: depends on `sb1250_defs.h`; many fields are feature-gated for pass2/pass3/112x/BCM1480. It integrates with DMA descriptors from `sb1250_dma.h`, MAC register addresses from `sb1250_regs.h`/`bcm1480_regs.h`, PHY/MDIO code, and network drivers.

Risks and test signals: wrong feature gating can expose fields unavailable on older silicon. RX/TX status bits share positions with different meanings, so ISR code must apply the correct channel context. The FIFO pointer getters for RX use TX masks in this header, a compatibility risk for any debug code depending on those helpers. Test signals include Ethernet link bring-up at 10/100/1000, RX/TX with checksum/VLAN/flow control, multicast/hash/exact filter tests, interrupt-per-channel tests, MDIO PHY access, and compile coverage across feature masks.
