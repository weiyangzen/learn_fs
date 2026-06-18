# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-control-scb.c

## Purpose
Small platform driver for the PolarFire SoC control SCB syscon. It instantiates an MFD child named `mpfs-tvs`.

## Important APIs, Types, And Functions
Uses `struct mfd_cell`, `devm_mfd_add_devices()`, OF match table, and `module_platform_driver()`. The only runtime function is `mpfs_control_scb_probe()`.

## Control Flow
When a device compatible with `microchip,mpfs-control-scb` probes, the driver adds the `mpfs-tvs` child device with `PLATFORM_DEVID_NONE`.

## State And Persistence
No private state is allocated. Child registration is devm-managed by the parent device.

## Dependencies And Integration Points
Integrates with platform bus, OF matching, syscon/MFD infrastructure, and the eventual `mpfs-tvs` child driver.

## Risks
Probe has no fallback or optional child handling; if `devm_mfd_add_devices()` fails, the syscon child is unavailable. The driver assumes its parent syscon/regmap setup is already represented by device tree and MFD/syscon infrastructure.

## Test Signals
Probe success should create an `mpfs-tvs` platform child under a `microchip,mpfs-control-scb` device.
