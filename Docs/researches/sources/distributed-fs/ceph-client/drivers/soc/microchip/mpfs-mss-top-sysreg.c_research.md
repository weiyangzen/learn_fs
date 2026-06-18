# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-mss-top-sysreg.c

## Purpose
Platform/MFD wrapper for the PolarFire SoC MSS top sysreg block. It creates an `mpfs-reset` child and populates OF children.

## Important APIs, Types, And Functions
Uses `mpfs_mss_top_sysreg_probe()`, `devm_mfd_add_devices()`, `devm_of_platform_populate()`, and an OF match for `microchip,mpfs-mss-top-sysreg`.

## Control Flow
On probe, the driver registers one MFD cell named `mpfs-reset`. If that succeeds, it populates child platform devices described below the sysreg node in device tree.

## State And Persistence
No private state. Child devices are devm-managed or OF-populated under the parent.

## Dependencies And Integration Points
Integrates with platform bus, MFD core, OF platform population, and Microchip reset/sysreg child drivers.

## Risks
Failure to create the reset child aborts OF child population. The file assumes sysreg register access is provided by the broader syscon infrastructure rather than handled here.

## Test Signals
Probe should register `mpfs-reset` and any DT child devices under `microchip,mpfs-mss-top-sysreg`.
