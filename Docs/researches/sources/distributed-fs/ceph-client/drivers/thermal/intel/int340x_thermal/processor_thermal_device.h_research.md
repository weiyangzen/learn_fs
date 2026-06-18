# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_device.h

## Purpose

`processor_thermal_device.h` centralizes PCI IDs, feature flags, shared structures, mailbox command constants, and cross-module function prototypes for the Processor Thermal Device family.

## Important APIs, Types, and Functions

It defines `struct power_config`, `struct proc_thermal_device`, and `struct rapl_mmio_regs`. Feature flags include RAPL, FIVR, DVFS, workload request/hint, DLVR, power floor, MSI support, PTC, and SoC power slider. It declares RAPL, RFIM, workload, mailbox, power-floor, core add/remove, PM, MMIO, PTC, and slider functions. When MMIO RAPL is disabled, inline stubs return success/no-op.

## Control Flow

There is no executable flow except configuration-dependent inline stubs. The header controls which feature modules can be called from the PCI/core drivers and how driver data is shared.

## State and Persistence Behavior

The header defines in-memory state layout only. `struct proc_thermal_device` is the common persistent runtime object stored as PCI or device driver data.

## Dependencies and Integration Points

It depends on `linux/intel_rapl.h` and forward declarations/types from PCI and INT340x users. It is the internal ABI among the processor thermal modules and imports/export namespaces in those modules.

## Risks and Test Signals

Risks include mismatched feature bit interpretation between PCI ID tables and feature modules, duplicate PCI IDs with different naming, and build-configuration drift around RAPL stubs. Test signals are allmodconfig/allyesconfig builds, namespace import checks, and probe coverage for each feature-mask combination.
