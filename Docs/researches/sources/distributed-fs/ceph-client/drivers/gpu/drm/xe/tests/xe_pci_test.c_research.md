# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_pci_test.c

## Purpose

`xe_pci_test.c` is a KUnit suite that validates Xe graphics/media IP descriptors and PCI platform descriptors for basic consistency.

## Important APIs, Types, and Functions

- `check_graphics_ip()` validates graphics engine masks and fuse-register availability.
- `check_media_ip()` validates media engine masks.
- `check_platform_desc()` validates descriptor bounds such as DMA mask, GT count, VA bits, and VM levels.
- Suite: `xe_pci_test_suite`.

## Control Flow

Parameterized KUnit cases iterate graphics IPs, media IPs, and PCI IDs using generators from `xe_pci.c`. Each test extracts the descriptor and asserts masks only contain allowed engine classes and platform descriptor numeric fields are nonzero/in-range.

## State and Persistence Behavior

The suite is read-only over static descriptor tables and has no persistent runtime state.

## Dependencies and Integration Points

It depends on `xe_pci_test.h`, IP/PCI parameter generators, Xe platform descriptors, and hardware engine mask definitions. It provides low-cost guard coverage for descriptor table edits.

## Risks and Edge Cases

- These checks are structural, not exhaustive; invalid but structurally plausible descriptors can pass.
- Adding a new engine class requires updating allowed masks.
- Descriptor generator coverage depends on `xe_pci.c` arrays and PCI ID tables.

## Test Signals

Passing tests indicate descriptor fields are present and engine masks remain in expected graphics/media domains. Failures usually point to descriptor table drift or missing platform metadata.
