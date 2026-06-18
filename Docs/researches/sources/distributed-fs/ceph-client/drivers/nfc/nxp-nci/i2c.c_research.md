# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/i2c.c

Purpose: Implements the I2C physical layer for the NXP NCI core driver, including GPIO mode switching, IRQ-driven NCI/FW reads, and I2C writes.

Important APIs and functions: `struct nxp_nci_i2c_phy` stores I2C client, NCI device, enable/firmware GPIOs, and hard fault. PHY ops are `nxp_nci_i2c_set_mode()` and `nxp_nci_i2c_write()`. Read paths are `nxp_nci_i2c_nci_read()` and `nxp_nci_i2c_fw_read()`. Probe/remove are `nxp_nci_i2c_probe()` and `nxp_nci_i2c_remove()`.

Control flow: Probe verifies I2C functionality, maps ACPI GPIO names, gets enable and optional firmware GPIOs, calls `nxp_nci_probe()` with max payload 32, and requests a threaded IRQ. Mode switching drives firmware and enable GPIOs and clears hard fault when returning cold. IRQ handling locks the common `info_lock`, selects NCI or firmware read format based on current mode, marks fatal `-EREMOTEIO` as hard fault, and dispatches to `nci_recv_frame()` or `nxp_nci_fw_recv_frame()`.

State and persistence: Runtime state includes GPIO output values, `hard_fault`, and the common mode in `nxp_nci_info`. No durable persistence.

Dependencies and integration points: Integrates with Linux I2C, GPIO consumer API, ACPI/OF matching, NCI core, and NXP firmware download callbacks.

Risks: IRQ reads use header-provided lengths; malformed payload lengths become protocol errors. A hard fault blocks writes until cold mode reset. Remove calls `nxp_nci_remove()` before `free_irq()`, so IRQ serialization relies on normal teardown ordering. Test signals include GPIO mode transitions, optional firmware GPIO absence, NCI read with zero/nonzero payload, FW read framing, hard fault propagation, I2C standby retry, and ACPI/OF/id-table probing.
