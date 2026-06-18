# sources/distributed-fs/ceph-client/drivers/net/can/sun4i_can.c

Purpose: Platform SocketCAN driver for Allwinner SUN4I/SUN7I/R40/D1 CAN controllers using direct MMIO registers.

Important APIs, types, and functions: `struct sun4ican_priv` stores CAN core state, MMIO base, clock, optional reset control, command-register lock, and acceptance-filter offset. Netdev operations are open/close/start_xmit. Helpers handle reset/normal modes, bit timing, start/stop, error counters, RX parsing, error reporting, IRQ handling, and platform probe/remove.

Control flow: Probe gets quirk data, resources, allocates a one-echo-slot CAN netdev, initializes bit timing/ctrlmode support, and registers. Open requests IRQ, deasserts reset, enables clock, starts controller, and starts queue. Start enters reset mode, accepts all filters, clears counters, enables interrupts, applies modes/timing, then enters normal. ISR handles TX complete, drains RX, reports errors, clears interrupts, and caps loop count.

State and persistence behavior: Runtime state is register state plus CAN state, clock/reset enablement, and a spinlock protecting command writes. No persistent configuration beyond device-tree data and userspace CAN settings.

Dependencies and integration points: Uses platform/OF APIs, clocks, resets, MMIO `readl/writel`, SocketCAN helpers, CAN error SKBs, ethtool timestamp info, echo SKB, and IRQ handling.

Risks: Hardware mode timing can timeout. Overrun recovery resets the controller inside error handling. The IRQ cap prevents livelock but may leave pending work in storms.

Test signals: Each compatible quirk including D1 filter offset, open/close reset/clock sequencing, standard/extended TX/RX, RTR, loopback/listen-only/3-samples, bus error/off reporting, RX overrun recovery, and interrupt storm cap logging.
