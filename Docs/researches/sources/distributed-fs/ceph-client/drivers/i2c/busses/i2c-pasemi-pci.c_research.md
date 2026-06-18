# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-pci.c

## Purpose
Provides the PCI wrapper for PA Semi PWRficient SMBus controllers. It claims the PCI I/O BAR, maps it, initializes shared PA Semi SMBus state, and delegates adapter setup to `i2c-pasemi-core.c`.

## Important APIs, Types, And Functions
`pasemi_smb_pci_probe()` is the only probe path. It allocates `struct pasemi_smbus`, checks BAR0 is I/O space, sets the 100 kHz clock divisor, marks the hardware revision as PCI legacy, requests the I/O region, maps the BAR with `pcim_iomap()`, sets the HWMON class, and calls `pasemi_i2c_common_probe()`.

## Control Flow
The PCI driver matches device ID `0x1959:0xa003`. On probe it validates resources, initializes state, calls the common core, and stores driver data. There is no explicit remove hook because devm/pcim cleanup and devm adapter registration handle teardown.

## State And Persistence
State is the allocated `struct pasemi_smbus` tied to the PCI device. It persists for the device lifetime only. No durable state exists.

## Dependencies And Integration Points
Depends on PCI core, I/O port resource management, `pcim_iomap()`, I2C core through the shared PA Semi implementation, and HWMON class scanning expectations.

## Risks
Only 100 kHz is selected even though a 400 kHz divider constant exists, so higher-speed capability is unused here. Probe requires BAR0 I/O space and fails on memory BAR variants. Lack of an IRQ request means the shared core remains in polling mode unless changed by future glue.

## Test Signals
Probe the matching PCI device, verify BAR claim/map failures return expected errors, confirm adapter appears as HWMON-class I2C, run SMBus transactions through the shared core, and hot-unplug/unbind to validate managed cleanup.
