# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci.c

## Purpose

`xe_pci.c` provides fake PCI/platform data generation, parameter descriptions, IP and PCI ID parameter generators, fake Xe device initialization, and live Xe device iteration for KUnit tests.

## Important APIs, Types, and Functions

- Fake platform data: `cases`, `xe_pci_fake_data_gen_params`, and `xe_pci_fake_data_desc`.
- Lookup/description helpers for platform, subplatform, step, SR-IOV mode, graphics IP, and media IP.
- IP/PCI generators: `xe_pci_graphics_ip_gen_param`, `xe_pci_media_ip_gen_param`, and `xe_pci_id_gen_param`.
- Fake init stubs: `fake_read_gmdid`, `fake_xe_info_probe_tile_count`, and `xe_pci_fake_device_init`.
- Live generator: `xe_pci_live_device_gen_param`.

## Control Flow

Fake initialization chooses a PCI ID descriptor matching requested fake data, validates subplatform, installs static stubs for GMDID reads and tile-count probing, initializes early and full Xe info, and sets requested SR-IOV mode. Parameter generators iterate static arrays, bridge pre-GMDID and GMDID IP lists, and stop before sentinel PCI IDs.

## State and Persistence Behavior

Fake init mutates a test-owned `struct xe_device` info and SR-IOV mode fields and uses KUnit static stubs tied to the test. Live iteration takes and releases device references through `driver_find_next_device`/`put_device`.

## Dependencies and Integration Points

It depends on KUnit visibility/static stubs, Xe PCI ID tables, platform/subplatform descriptors, GMDID/IP tables, SR-IOV mode strings, step conversion helpers, and `xe_info_init_early`/`xe_info_init`. It is foundational for most fake and live tests.

## Risks and Edge Cases

- Fake data must remain representative of real platform descriptors or unit tests can pass with unrealistic devices.
- `test->priv` is used both as input fake data and later as device pointer; helper ordering matters.
- Live device iteration depends on the global Xe PCI driver and real device availability.

## Test Signals

Signals include fake init success for all listed platforms/subplatforms, meaningful KUnit parameter names, correct GMDID/step injection, PCI ID generator coverage, and live test enumeration on systems with Xe devices.
