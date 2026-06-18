# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Makefile

## Purpose
This Makefile builds the ST NCI shared module and optional I2C/SPI transport modules.

## Important build objects
- `st-nci-objs = ndlc.o core.o se.o vendor_cmds.o` combines the low-level transport state machine, NCI glue, secure-element support, and vendor command handlers.
- `st-nci_i2c-objs = i2c.o` and `st-nci_spi-objs = spi.o` build physical links.

## Control flow and integration
Transport modules call into exported NDLC and core symbols from the shared module. The object grouping ensures secure-element and vendor-command hooks are present whenever the core is selected.

## State, dependencies, and risks
There is no runtime state. Build risks are missing exports or mismatched module symbol names, especially because the module name uses a hyphen while transport object names use underscore forms.

## Test signals
Build all combinations as modules and built-ins, and run modpost to catch missing exported symbols between physical and shared modules.
