# sources/distributed-fs/ceph-client/drivers/net/can/xilinx_can.c

Purpose: implements the SocketCAN network driver for Xilinx AXI CAN, Zynq CANPS, AXI CANFD 1.0, and AXI CANFD 2.0 platform devices. It binds OF compatibles to per-IP capability data, maps controller registers, configures clocks/reset/runtime PM, registers a `struct net_device` via `alloc_candev()`/`register_candev()`, and translates between Xilinx message RAM/FIFO formats and Linux CAN/CAN-FD sk_buffs.

Important APIs, types, and functions:
- `struct xcan_priv` embeds `struct can_priv`, TX queue counters, NAPI, endian-specific MMIO accessors, clocks, optional PHY, reset control, variant data, and ECC statistics.
- `xcan_chip_start()` resets to config mode, programs bit timing, enables interrupts, filter state, loopback, and controller start.
- `xcan_start_xmit_fifo()` and `xcan_start_xmit_mailbox()` select FIFO or serialized mailbox TX; `xcan_write_frame()` encodes classic/CAN-FD frames.
- `xcan_rx_poll()`, `xcan_rx()`, and `xcanfd_rx()` drain RX via NAPI and decode hardware frames into SocketCAN skbs.
- `xcan_err_interrupt()` handles bus-off, warning/passive transitions, bus errors, overflow, arbitration lost, RXMNF, and optional ECC counters.
- `xcan_probe()` performs OF/platform setup, endianness detection, runtime PM, NAPI, CAN registration, and CANFD capability wiring.

Control flow: probe allocates and registers a CAN netdev; open powers the transceiver, resumes PM, requests IRQ, resets/configures the chip, enables NAPI and queue; IRQ handles state/TX/error conditions and masks RX before scheduling NAPI; NAPI drains RX and reenables RX interrupts; close and suspend stop queues, interrupts, hardware, clocks, and PHY power.

State and persistence behavior: Runtime state is held in `xcan_priv` and SocketCAN core state. TX echo state uses `tx_head`/`tx_tail` and is cleared on reset. ECC counters accumulate for the driver lifetime through `u64_stats_t`; hardware ECC counters are reset after interrupt reads. No state persists across probe/removal.

Dependencies and integration points: Linux platform/OF, MMIO, IRQ, NAPI/netdev, SocketCAN, ethtool, reset, clocks, runtime PM, optional PHY transceiver, and u64 stats. DT must provide compatible, MMIO/IRQ, clock names, TX/RX depth properties, and optional `xlnx,has-ecc`.

Risks: endian auto-detection depends on reset status; FIFO TX completion is race-sensitive and capped to two frames; mailbox TX is serialized to preserve order; ECC handling has a small read/reset race; missing DT depths are fatal; bus-off relies on CAN restart via `do_set_mode`.

Test signals: probe each compatible/endian mode, loopback and real-bus classic/CAN-FD traffic, FIFO/mailbox TX stress, RX NAPI quota/overflow/RXMNF tests, bus error and bus-off injection, runtime/system suspend-resume, and ethtool ECC counter validation.
