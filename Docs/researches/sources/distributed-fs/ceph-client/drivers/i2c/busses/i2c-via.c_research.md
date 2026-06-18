# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-via.c

## Purpose

`i2c-via.c` supports a legacy VIA VT82C586B south bridge GPIO-based I2C bus. It exposes one bit-banged adapter using PM I/O registers for line direction/output/input.

## Important APIs, Types, and Functions

Global state includes `pm_io_base`, a single static adapter, and static `i2c_algo_bit_data`. `bit_via_setscl()` and `bit_via_setsda()` emulate open-drain behavior by changing GPIO direction: high is input/pull-up, low is output. `vt586b_probe()` discovers the PM base from PCI config revision-dependent registers and registers the bit bus.

## Control Flow

PCI probe allows only one host, reads the revision, selects the correct base config register, masks the I/O base, reserves six bytes, initializes direction/output low, sets the parent device, and calls `i2c_bit_add_bus()`. Removal deletes the adapter, releases the region, and clears `pm_io_base`.

## State and Persistence Behavior

The driver relies on global singleton state and direct port I/O. It does not cache device registers or support PM save/restore. The output data bits are initialized low and never changed; high is represented only by input direction.

## Dependencies and Integration Points

It depends on PCI matching for `PCI_DEVICE_ID_VIA_82C586_3`, I/O port reservation, and `i2c-algo-bit`. It advertises `I2C_CLASS_HWMON`.

## Risks

The singleton design cannot handle multiple devices. Direct GPIO direction manipulation assumes external pull-ups and non-open-drain pins. The I/O base masking and revision table are legacy hardware-specific. No ACPI resource conflict check is performed before requesting ports.

## Test Signals

Validate PCI detection across revisions, I/O region collision handling, SCL/SDA idle high and low-driving behavior, bit-banged read/write transactions, singleton rejection for a second device, and clean resource release.
