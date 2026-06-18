# sources/distributed-fs/ceph-client/drivers/media/cec/platform/seco/seco-cec.c

## Purpose
This driver supports SECO x86 boards with an embedded microcontroller that exposes HDMI CEC and optionally RC5 IR over a Braswell SMBus I/O-port interface.

## Important APIs, Types, and Functions
`struct secocec_data` stores device, platform device, CEC adapter, notifier, optional RC device, input phys string, and IRQ. `smb_word_op` performs low-level SMBus word transactions through fixed I/O ports. CEC callbacks are `secocec_adap_enable`, `secocec_adap_log_addr`, and `secocec_adap_transmit`. Interrupt handlers call `secocec_rx_done`, `secocec_tx_done`, and optional `secocec_ir_rx`.

## Control Flow
Probe finds the related HDMI PCI device using DMI, requests the SMBus I/O region, validates ACPI/GPIO IRQ, checks firmware version, requests a threaded IRQ, allocates/registers the CEC adapter and notifier, and optionally registers RC input. Enabling clears status and enables CEC interrupts. Transmit writes payload length, opcode, data words, and header byte to fire the message. IRQ reads high-level status, then CEC status, dispatches RX/TX completions, handles IR, and clears status bits.

## State and Persistence
The microcontroller stores logical address, pending TX/RX data, CEC status, enable bits, firmware version, and IR data. Driver state is volatile. No persistent configuration is written, though firmware version must be at least `SECOCEC_LATEST_FW`.

## Dependencies and Integration Points
The driver depends on ACPI ID `CEC00001`, DMI match for UDOO x86, PCI device lookup for connector binding, GPIO-to-IRQ, I/O-port SMBus access, CEC notifier, and optional `CONFIG_CEC_SECO_RC` RC-core support.

## Risks and Test Signals
Fixed SMBus I/O ports and request/release discipline are high risk. Payload packing uses pairs of data bytes and assumes valid CEC length. In `secocec_rx_done`, odd payload lengths can index `payload_msg[i + 1]` beyond the logical payload. Test firmware rejection, SMBus timeout/error handling, IRQ clearing, RX overflow/error, TX NACK/error, suspend/resume interrupt enable state, and optional IR decoding.
