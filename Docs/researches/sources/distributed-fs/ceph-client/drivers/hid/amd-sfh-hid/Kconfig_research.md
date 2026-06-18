# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/Kconfig

## Purpose

This Kconfig file exposes AMD Sensor Fusion Hub support as a HID transport. The driver presents AMD MP2/SFH sensors as HID sensor devices.

## Important APIs, Types, and Functions

The sole symbol is `AMD_SFH_HID`, a tristate "AMD Sensor Fusion Hub" option. It depends on `X86_64`, `PCI`, and `ACPI`, and depends on `HID`. It selects `AMD_PMF` when `ACPI` is enabled so SFH 1.1 platform information can integrate with AMD platform management.

## Control Flow

When the parent HID Kconfig sources this file, the menu offers `AMD_SFH_HID` only if the platform dependencies hold. Selecting it enables the `amd-sfh-hid/` Makefile target and links the PCI, HID, descriptor, and SFH 1.1 implementation objects.

## State and Persistence Behavior

State is build-time only. At runtime, the resulting `amd_sfh` module binds AMD MP2 PCI IDs and creates HID devices for discovered sensors.

## Dependencies and Integration Points

This option integrates with PCI enumeration, ACPI system firmware, HID core, and AMD PMF. The downstream C code relies on x86-specific CPU family checks and AMD PCI device IDs.

## Risks and Test Signals

The dependency set must prevent builds on unsupported architectures while allowing module builds on supported AMD laptops. Useful test signals are `CONFIG_AMD_SFH_HID=m/y` builds on x86_64, configurations without `AMD_PMF`, and runtime probe logs on MP2 and MP2 1.1 devices.
