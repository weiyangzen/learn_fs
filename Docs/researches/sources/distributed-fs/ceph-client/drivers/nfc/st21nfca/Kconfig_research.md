# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Kconfig

## Purpose
This Kconfig fragment defines the ST21NFCA HCI core and its I2C transport.

## Important symbols
- `NFC_ST21NFCA` is a hidden tristate core option selecting `CRC_CCITT` for HCI LLC frame CRC handling.
- `NFC_ST21NFCA_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC`, selects the core, and builds `st21nfca_i2c`.

## Control flow and integration
The core is HCI-based rather than NCI-based and is used by the I2C physical layer with the SHDLC LLC. The I2C driver registers a `nfc_hci_dev` through `st21nfca_hci_probe()`.

## State, dependencies, and risks
Kconfig state is compile-time only. Missing `CRC_CCITT` would break frame validation; missing `NFC_SHDLC` would break the selected LLC path.

## Test signals
Config tests should cover dependency pruning, module and built-in builds, and that enabling I2C selects the HCI core and CRC support.
