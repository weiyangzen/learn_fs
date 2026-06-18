# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Makefile

## Purpose
This Makefile builds the ST21NFCA HCI core module and I2C transport module.

## Important build objects
- `st21nfca_hci-objs = core.o dep.o se.o vendor_cmds.o` combines HCI core logic, NFC-DEP handling, secure-element support, and vendor commands.
- `st21nfca_i2c-objs = i2c.o` builds the I2C physical layer.

## Control flow and integration
The I2C module calls exported core symbols. The core object group ensures DEP, SE, and vendor hooks are linked into the HCI device implementation.

## State, dependencies, and risks
There is no runtime state. Build risks are missing exports and mismatches between the configured LLC name in I2C and HCI core allocation.

## Test signals
Build tests should compile core-only and I2C-enabled combinations as both module and built-in, with modpost checking exported symbols.
