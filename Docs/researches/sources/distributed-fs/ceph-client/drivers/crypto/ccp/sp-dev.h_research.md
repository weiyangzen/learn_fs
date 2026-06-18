# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.h

## Purpose

`sp-dev.h` defines the common Secure Processor device model, version-data structures, feature flags, and cross-file APIs for CCP and PSP subdevices.

## Important APIs, Types, And Functions

Key structures are `ccp_vdata`, `sev_vdata`, `tee_vdata`, `platform_access_vdata`, `psp_vdata`, `sp_dev_vdata`, and `sp_device`. It defines cache attributes, platform feature bits, the `PSP_FEATURE()` macro, bus init/exit prototypes, common SP lifecycle/IRQ helpers, and conditional CCP/PSP stubs for disabled configs.

## Control Flow

The header has no executable control flow, but its vdata pointers drive whether `sp_init()` creates CCP and/or PSP subdevices and which MMIO offsets those subdevices use.

## State And Persistence Behavior

`struct sp_device` persists per bound device and carries bus-specific data, MMIO base, IRQ state, master-selection callbacks, and CCP/PSP subdevice pointers.

## Dependencies And Integration Points

It is included by SP core, PCI/platform frontends, PSP, SEV, TEE, and CCP code. It abstracts hardware generation differences through static vdata tables.

## Risks And Test Signals

Risks include incorrect register offsets in vdata, function-pointer misuse when configs are disabled, and structure field assumptions across bus frontends. Compile matrix coverage and probe tests for all supported PCI IDs/ACPI/OF matches are key.
