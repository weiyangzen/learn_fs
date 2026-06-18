# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/i2c.c

## Purpose
`i2c.c` is the I2C physical layer for ST_NCI chips. It resets/enables the controller, transfers NDLC-framed NCI packets over I2C, services IRQs, and starts the shared NDLC/core stack.

## Important APIs, types, and functions
- `struct st_nci_i2c_phy` stores the I2C client, NDLC pointer, IRQ active flag, reset GPIO, and secure-element presence flags.
- `st_nci_i2c_enable()` toggles reset low/high with delays and enables IRQ when appropriate.
- `st_nci_i2c_disable()` disables IRQ.
- `st_nci_i2c_write()` sends an skb over I2C and retries once for standby errors.
- `st_nci_i2c_read()` reads a 4-byte NDLC/NCI prefix, validates declared length up to 250, allocates an skb, and reads the payload.
- The threaded IRQ reads frames only when powered and passes valid skbs to `ndlc_recv()`.

## Control flow
Probe checks I2C functionality, gets reset GPIO, reads `ese-present` and `uicc-present` properties, calls `ndlc_probe()` with I2C phy ops and headroom/tailroom, then registers a threaded IRQ. Runtime open from the NCI core calls through NDLC to `enable`; IRQs deliver received frames into the NDLC state machine; writes originate from NDLC send queue.

## State and persistence
Runtime state includes reset GPIO level, `irq_active`, NDLC powered/hard-fault state, and secure-element presence booleans read from firmware/ACPI/device tree. No persistent data is written.

## Dependencies and integration points
Dependencies include I2C, GPIO, ACPI GPIO mapping, OF matching, threaded IRQs, `ndlc_probe()`, and ST_NCI secure-element status. Compatible strings include `st,st21nfcb-i2c`, `st,st21nfcb_i2c`, and `st,st21nfcc-i2c`; ACPI IDs include `SMO2101` and `SMO2102`.

## Risks
The length field is read from bytes 2-3 after an initial 4-byte read and trusted for allocation/payload read. IRQ is initially considered active before `devm_request_threaded_irq()` succeeds. `st_nci_i2c_disable()` may be called even if IRQ was not enabled, so IRQ active state must stay coherent. Read errors are mostly dropped in IRQ context and not always promoted to `hard_fault`.

## Test signals
Test reset timing, IRQ enable/disable during open/close, standby write/read retries, invalid length, short payload read, device properties for SE discovery, ACPI/OF matching, and remove cleanup through `ndlc_remove()`.
