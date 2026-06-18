# sources/distributed-fs/ceph-client/drivers/nfc/nxp-nci/Kconfig

Purpose: Declares build configuration for the generic NXP NCI core driver and its I2C transport.

Important entries: `NFC_NXP_NCI` is a tristate depending on `NFC_NCI` and builds the generic NCI core for NXP chips such as PN547, PN548, and PN7150 families. `NFC_NXP_NCI_I2C` is a tristate depending on `NFC_NXP_NCI && I2C` and builds the I2C transport module.

Control flow: This file contributes no runtime flow; it controls which modules and dependencies Kbuild exposes.

State and persistence: Kconfig selections persist only in kernel build configuration. No runtime state.

Dependencies and integration points: Integrates with the kernel NFC NCI stack and I2C subsystem. The help text warns that this kernel NCI driver is not for NXP libnfc userspace stacks.

Risks: The I2C option depends on the core instead of selecting it, so users must enable both or rely on menu dependency visibility. Test signals include `m`, `y`, and disabled builds for both symbols, dependency pruning when `NFC_NCI` or `I2C` is unavailable, and module name verification for `nxp_nci` and `nxp_nci_i2c`.
