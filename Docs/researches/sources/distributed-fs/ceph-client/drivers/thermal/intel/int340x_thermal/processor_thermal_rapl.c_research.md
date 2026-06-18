# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_rapl.c

## Purpose

`processor_thermal_rapl.c` registers an Intel RAPL powercap interface backed by Processor Thermal Device MMIO registers instead of MSRs.

## Important APIs, Types, and Functions

It defines MMIO masks and `rpi_mmio[]` primitive metadata for power limits, energy, locks, time windows, thermal spec, throttled time, and policy. `rapl_mmio_default` maps package and DRAM domain registers relative to `mmio_base`. `rapl_mmio_read_raw()` and `rapl_mmio_write_raw()` implement raw RAPL accessors. Exports are `proc_thermal_rapl_add()` and `proc_thermal_rapl_remove()`.

## Control Flow

Add populates the global `rapl_mmio_priv` register pointers from the device MMIO base, registers a powercap control type named `intel-rapl-mmio`, checks for an existing package 0 domain, and adds package 0. Remove finds and removes package 0, then unregisters the powercap control type.

## State and Persistence Behavior

`rapl_mmio_priv` is static global state. RAPL limits and counters are hardware register state; the driver persists only mapping metadata and the powercap control-type registration.

## Dependencies and Integration Points

It depends on the Intel RAPL core namespace, powercap framework, and processor thermal MMIO mapping. The common MMIO add path invokes it when `PROC_THERMAL_FEATURE_RAPL` is set.

## Risks and Test Signals

Risks include package-0-only registration, global state unsuitable for multiple instances, missing locking around read-modify-write raw writes, and drift from RAPL primitive expectations. Test signals include powercap tree creation, package/DRAM domain attributes, duplicate add returning `-EEXIST`, remove idempotence, and register read/write validation on RAPL-capable PCI IDs.
