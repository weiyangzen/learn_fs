# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_iosf.h

## Purpose

`intel_soc_dts_iosf.h` declares the shared data structures and APIs for Intel SoC DTS sensors accessed through IOSF sideband registers.

## Important APIs, Types, and Functions

It defines `SOC_MAX_DTS_SENSORS` as 2 and `SOC_MAX_DTS_TRIPS` as 2. `enum intel_soc_dts_interrupt_type` distinguishes none, APIC, MSI, SCI, and SMI. `struct intel_soc_dts_sensor_entry` stores ID, saved status, thermal zone, and backpointer. `struct intel_soc_dts_sensors` stores TjMax, locks, interrupt type, and sensor entries. Prototypes expose init, exit, and interrupt handler.

## Control Flow

The header contains no executable flow. It defines how platform-specific callers instantiate and interact with the IOSF DTS core.

## State and Persistence Behavior

The defined structures represent runtime state. Saved register status is used by the implementation to restore hardware state during exit.

## Dependencies and Integration Points

It depends on `linux/thermal.h` and is included by standalone SoC DTS and legacy processor thermal PCI code.

## Risks and Test Signals

Risks are structural coupling with the implementation and callers assuming exactly two sensors/trips. Test signals include compile coverage for APIC and MSI callers and runtime init/exit using the saved-state fields.
