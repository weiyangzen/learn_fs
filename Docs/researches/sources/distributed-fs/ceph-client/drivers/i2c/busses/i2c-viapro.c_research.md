# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viapro.c

## Purpose

`i2c-viapro.c` is a legacy SMBus host driver for many VIA south bridges. It exposes the controller as an SMBus-only I2C adapter using direct I/O port transactions discovered from PCI configuration space.

## Important APIs, Types, and Functions

Global state includes `vt596_smba`, `SMBHSTCFG`, `vt596_features`, `vt596_pdev`, and a single static adapter. `vt596_transaction()` starts an SMBus command, polls status, maps timeout/collision/no-response errors, and clears status. `vt596_access()` implements SMBus quick, byte, byte-data, word-data, process-call, block, and optional I2C block transactions.

## Control Flow

PCI probe discovers or forcibly programs the SMBus base address, checks ACPI/resource ownership, optionally enables the controller with dangerous module parameters, detects I2C block capability by device/revision, sets adapter metadata, registers it, then intentionally returns `-ENODEV` so other drivers can still bind to the PCI device. Module exit unregisters the PCI driver and manually removes the adapter if one was created.

## State and Persistence Behavior

The driver is a singleton with persistent I/O base and feature flags. Module parameters `force` and `force_addr` can alter hardware enable and base-address config. No runtime cache exists. Status is polled synchronously for each SMBus transaction.

## Dependencies and Integration Points

It depends on PCI IDs, ACPI region checks, I/O port reservation, SMBus algorithm callbacks, and hwmon class scanning. It is intentionally non-owning with respect to the PCI device after probe.

## Risks

`force` and especially `force_addr` can conflict with firmware/resource assignments. Returning `-ENODEV` after successful adapter registration is unusual and depends on global cleanup at module exit. SMBus status polling is busy-sleep based and assumes status bits are clearable by writing them back. Singleton state cannot represent multiple controllers.

## Test Signals

Validate supported PCI IDs and base-register variants, ACPI conflict rejection, forced enable/address paths, all SMBus protocol sizes, optional I2C block functionality per revision, timeout/collision/no-response mapping, intentional PCI probe failure with adapter still registered, and module-exit cleanup.
