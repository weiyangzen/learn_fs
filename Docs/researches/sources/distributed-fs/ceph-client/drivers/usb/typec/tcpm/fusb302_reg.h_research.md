# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302_reg.h

## Purpose

`fusb302_reg.h` defines the FUSB302 register map, bit masks, status values, and TX FIFO token constants used by `fusb302.c`.

## Important APIs, Types, and Functions

The header defines register addresses for device ID, switches, measure, controls, masks, power, reset, status, interrupts, and FIFOs. Bit masks describe CC pull-up/down, VCONN, measurement selection, PD auto-GoodCRC, power/data role bits, toggle modes, retry counts, interrupt masks/statuses, BC levels, and FIFO states. `enum fusb302_txfifo_tokens` defines SOP sync, reset, PACKSYM, JAMCRC, EOP, TXON, and TXOFF tokens for PD message serialization.

## Control Flow

There is no executable flow. The constants drive every register read/write and FIFO command sequence in the FUSB302 driver.

## State and Persistence Behavior

The header has no state. It names volatile hardware state and command encodings.

## Dependencies and Integration Points

It is included directly by `fusb302.c`. The definitions must match the FUSB302 data sheet and the TCPM driver's expectations for CC and PD state transitions.

## Risks and Test Signals

Risks include incorrect bit masks for multi-bit fields, token ordering assumptions in TX FIFO framing, and stale constants for silicon variants. Test signals are register-level driver tests for CC setup, toggling, interrupt masks, PD reset, FIFO TX/RX, and device ID reads.
