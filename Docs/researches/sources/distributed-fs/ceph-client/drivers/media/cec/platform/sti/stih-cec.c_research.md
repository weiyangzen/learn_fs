# sources/distributed-fs/ceph-client/drivers/media/cec/platform/sti/stih-cec.c

## Purpose
This is the STMicroelectronics STiH4xx CEC platform driver. It registers a CEC adapter over a memory-mapped transceiver with separate TX/RX byte arrays and status registers.

## Important APIs, Types, and Functions
`struct stih_cec` stores adapter, device, clock, MMIO base, IRQ status, and notifier. CEC callbacks are `stih_cec_adap_enable`, `stih_cec_adap_log_addr`, and `stih_cec_adap_transmit`. Completion helpers `stih_tx_done` and `stih_rx_done` translate hardware status to CEC core calls.

## Control Flow
Probe parses the HDMI phandle, maps registers, requests a threaded IRQ, gets `cec-clk`, allocates/registers notifier and adapter, and stores drvdata. Enable programs clock divider and timing thresholds, enables TX/RX arrays, configures control bits, clears address/status, and enables interrupts. Transmit writes message bytes to TX array and starts auto-SOM/EOM transmission. Hard IRQ snapshots/clears status; thread reports TX completion or received message.

## State and Persistence
Hardware holds logical address table, timing configuration, TX/RX byte arrays, and status. Driver stores only a last IRQ status snapshot and adapter/notifier resources. No persistent storage exists.

## Dependencies and Integration Points
DT compatible is `st,stih-cec`. The driver uses platform resources, clock API, threaded IRQs, CEC core, and notifier connector metadata.

## Risks and Test Signals
The driver does not call `clk_prepare_enable`; it reads rate only, so platform clock enable assumptions should be validated. Logical address invalid clears all addresses, otherwise addresses are ORed. Test TX ACK/NACK/error/arbitration status, RX min/max error suppression, zero-length RX, multi-logical-address programming, and interrupt status clearing.
