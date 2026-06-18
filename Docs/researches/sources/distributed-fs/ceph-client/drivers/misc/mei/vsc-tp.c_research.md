# sources/distributed-fs/ceph-client/drivers/misc/mei/vsc-tp.c

## Purpose
This SPI driver implements the Intel VSC transport layer. It manages ACPI-described GPIOs, reset and wake handshakes, packet framing, CRC/sequence validation, IRQ-driven events, ROM transfers, and creation of a child platform device consumed by `platform-vsc.c`.

## Important APIs, types, and functions
Private types are `vsc_tp_packet_hdr`, `vsc_tp_packet`, and `vsc_tp`. Exported APIs are `vsc_tp_xfer()`, `vsc_tp_rom_xfer()`, `vsc_tp_reset()`, `vsc_tp_need_read()`, `vsc_tp_register_event_cb()`, `vsc_tp_intr_enable()`, `vsc_tp_intr_disable()`, and `vsc_tp_intr_synchronize()`. Driver callbacks include `vsc_tp_probe()`, `vsc_tp_remove()`, `vsc_tp_isr()`, and `vsc_tp_event_work()`.

## Control flow and state
Probe allocates transport and packet buffers, registers ACPI GPIO mappings, gets wakeup/reset GPIOs, initializes wait queues and locks, requests a falling-edge threaded IRQ, finds the single ACPI child, and registers platform device `intel_vsc` with the transport pointer as platform data. Normal transfer builds a sync/cmd/len/seq packet, appends CRC, wakes firmware, performs SPI transfers until a complete response is reconstructed, validates CRC and sequence, rejects ACK/NACK/BUSY command responses, and releases wake. ROM transfer uses fixed-size big-endian SPI blocks and polls GPIO readiness.

## State and persistence behavior
State is in-memory: SPI pointer, child platform device, GPIO descriptors, sequence counter, packet buffers, IRQ assertion count, event callback/context, and locks. Reset toggles firmware reset GPIO, waits for ROM boot, returns wake GPIO to inactive, and clears assertion count. No persistent storage is used.

## Dependencies and integration points
It depends on ACPI, GPIO descriptors, SPI core, IRQs, CRC32, wait queues, workqueues, and platform-device registration. It integrates upward through exported `VSC_TP` APIs and downward through ACPI IDs `INTC1009`, `INTC1058`, `INTC1094`, and `INTC10D0`.

## Risks and test signals
Risks include packet reassembly edge cases, CRC complement calculation, sequence wrap/validation, wake GPIO timing, IRQ enable/disable balance, child platform lifetime during shutdown, and callback races. Test signals include ACPI probe, GPIO acquisition, IRQ event delivery, ROM firmware download, normal read/write transfers, CRC/sequence fault rejection, reset behavior, and remove/shutdown cleanup.
