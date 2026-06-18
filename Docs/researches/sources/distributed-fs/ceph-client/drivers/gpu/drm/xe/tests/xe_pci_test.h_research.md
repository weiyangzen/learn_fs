# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.h

## Purpose

`xe_pci_test.h` declares the fake PCI data structure and KUnit parameter/helper functions shared by Xe PCI-related tests and fake device setup.

## Important APIs, Types, and Functions

- `struct xe_pci_fake_data` with SR-IOV mode, platform, subplatform, step info, graphics version, and media version.
- Fake initialization: `xe_pci_fake_device_init`.
- Parameter helpers: `xe_pci_fake_data_gen_params`, `xe_pci_fake_data_desc`, `xe_pci_graphics_ip_gen_param`, `xe_pci_media_ip_gen_param`, `xe_pci_id_gen_param`, and `xe_pci_live_device_gen_param`.

## Control Flow

There is no executable code. Test suites include this header to request fake devices or parameterized live/static descriptor iteration.

## State and Persistence Behavior

The header stores no state. `struct xe_pci_fake_data` instances are passed through `test->priv` or parameter values to drive fake device initialization.

## Dependencies and Integration Points

It includes Linux types, KUnit, platform type headers, SR-IOV types, and step types. It is used by fake KUnit helpers, PCI descriptor tests, WA/RTP tests, SR-IOV tests, and live test parameterization.

## Risks and Edge Cases

- The fake data structure is a cross-test contract; adding platform dimensions requires coordinated updates in initializers and descriptors.
- Function prototypes must stay exported when used across test modules.

## Test Signals

Compile coverage across all dependent tests is the main signal. Runtime signals come from successful fake device creation and live device parameter iteration.
