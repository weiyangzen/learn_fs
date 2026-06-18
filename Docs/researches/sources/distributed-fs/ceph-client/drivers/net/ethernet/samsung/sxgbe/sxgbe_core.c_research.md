# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_core.c

Purpose: implements SXGBE MAC core operations: core initialization, MAC address programming, TX/RX enable, version/feature reads, speed selection, EEE LPI controls, RX checksum offload, RX queue enable/disable, and MAC interrupt status handling.

Important APIs: `sxgbe_get_core_ops()` returns a static `struct sxgbe_core_ops`. Key callbacks include `core_init`, `host_irq_status`, `set_umac_addr`, `get_umac_addr`, `enable_rx`, `enable_tx`, `get_controller_version`, `get_hw_feature`, `set_speed`, `set_eee_mode`, `reset_eee_mode`, `set_eee_timer`, `set_eee_pls`, `enable_rx_csum`, `disable_rx_csum`, `enable_rxqueue`, and `disable_rxqueue`.

Control flow: `sxgbe_core_init()` sets TX jabber disable and RX jumbo/ACS bits. IRQ status reads `SXGBE_CORE_INT_STATUS_REG` and, for LPI interrupts, reads `SXGBE_CORE_LPI_CTRL_STATUS` to derive entry/exit status flags. MAC address setters split a six-byte address into high/low registers. Enable functions read-modify-write TX/RX config bits. EEE functions set LPI enable/automate bits, PLS, and timers. Feature/version accessors read register offsets.

State and persistence: state is primarily hardware register state under `ioaddr`. No private static mutable state exists.

Dependencies and integration: depends on `sxgbe_reg.h` register offsets/bit masks, Linux MMIO helpers, netdevice/PHY includes, and the operation table consumed by main/probe paths.

Risks: several callbacks are placeholders (`dump_regs`, `pmt`). RX queue enable/disable masks shift by queue number but write unshifted enable/disable values, which should be validated against register layout. Speed setting directly shifts a caller-supplied value. LPI status read clears hardware bits, so callers must account for destructive reads.

Test signals: register write/read traces during probe, MAC address set/get round trips, TX/RX enable toggles, EEE enable/disable/timer/PLS behavior, LPI interrupt counters, feature register decoding, and queue enable across all supported RX queues.
