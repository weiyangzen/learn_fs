# sources/distributed-fs/ceph-client/drivers/nfc/fdp/fdp.h

Purpose: Declares the private interface between the FDP core NCI driver and its I2C physical transport.

Important APIs, types, and functions: `struct fdp_i2c_phy` stores the `i2c_client`, power GPIO, registered `nci_dev`, hard-fault state, and next expected read size. The header declares `fdp_nci_probe()` and `fdp_nci_remove()`.

Control flow: The I2C driver allocates/fills `fdp_i2c_phy`, then calls `fdp_nci_probe()` with transport callbacks, framing head/tail room, clock values, and optional vendor config. The core returns an `nci_dev` pointer that later feeds IRQ receive handling and remove.

State and persistence behavior: The struct records volatile transport state. `hard_fault` suppresses future writes after transport failure, and `next_read_size` tracks the two-step FDP I2C framing protocol.

Dependencies and integration points: Includes NFC NCI core declarations and GPIO consumer APIs. It couples `i2c.c` and `fdp.c` but is not a public kernel subsystem header.

Risks: The struct name is I2C-specific, so adding new transports would require refactoring or a more generic PHY type. `uint16_t` is used instead of kernel `u16`, but only in private state.

Test signals: Compile the core and I2C modules together, verify exported symbols resolve, and exercise probe/remove paths that set and consume `phy->ndev`.
