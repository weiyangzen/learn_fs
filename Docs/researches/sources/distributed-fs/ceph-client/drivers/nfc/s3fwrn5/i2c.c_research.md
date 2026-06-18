# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/i2c.c

## Purpose
`i2c.c` is the S3FWRN5 I2C physical layer. It owns GPIOs, optional clock enablement, IRQ-driven reads, I2C writes, and mode-specific frame extraction before handing frames to the shared S3FWRN5 core.

## Important APIs, types, and functions
- `struct s3fwrn5_i2c_phy` wraps `struct phy_common`, the I2C client, optional clock, and `irq_skip`.
- `s3fwrn5_i2c_set_mode()` uses common power control and suppresses the next IRQ after mode transition.
- `s3fwrn5_i2c_write()` sends sk_buff data with a standby retry on `-EREMOTEIO`.
- `s3fwrn5_i2c_read()` reads either an NCI control header or firmware header, then reads the declared payload and passes the skb to `s3fwrn5_recv_frame()`.
- `s3fwrn5_i2c_probe()` acquires `en` and `wake` GPIOs, enables an optional clock, calls `s3fwrn5_probe()`, and registers a threaded IRQ.

## Control flow
On probe, the physical object starts in COLD with IRQ skip enabled. The common core controls mode/wake through `i2c_phy_ops`. IRQ thread validates context, locks the common mutex, skips one IRQ after power transitions, then reads only in NCI or FW mode. Reads are two-stage: header first, payload second. Remove delegates to `s3fwrn5_remove()`.

## State and persistence
Runtime state includes mode/wake GPIO values, optional clock enablement managed by devm, IRQ skip, and the common NCI device pointer. There is no persistent storage.

## Dependencies and integration points
This file integrates with I2C, GPIO descriptor API, optional clocks, threaded IRQs, NCI header definitions, S3FWRN5 firmware header definitions, and the shared core. Device tree compatible is `samsung,s3fwrn5-i2c`.

## Risks
The read path uses NCI control-header length even though data/notification packet header formats can differ; correctness depends on the chip interrupting for control-like frames or common header compatibility. Payload lengths are trusted after the header read. `irq_skip` may drop a legitimate first frame if a device asserts IRQ immediately after a mode transition. Standby retry only handles `-EREMOTEIO`.

## Test signals
Test probe with missing GPIOs, optional clock failures, standby write retry, short header read, short payload read, IRQ during COLD mode, firmware-mode frame routing, and removal after IRQ registration failure.
