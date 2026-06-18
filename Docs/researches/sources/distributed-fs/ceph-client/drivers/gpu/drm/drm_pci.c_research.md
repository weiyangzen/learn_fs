# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pci.c

## Purpose

`drm_pci.c` contains the PCI bus-id helper for DRM masters. It formats a unique legacy DRM device identifier from PCI domain, bus, slot, and function values.

## Important APIs, Types, and Functions

- `drm_get_pci_domain()` returns the PCI domain, except on most non-alpha architectures it preserves historical pre-1.4 DRM interface behavior by returning 0 when `dev->if_version < 0x10004`.
- `drm_pci_set_busid()` allocates and stores `master->unique` as `pci:%04x:%02x:%02x.%d` and fills `master->unique_len`.

## Control Flow

`drm_pci_set_busid()` casts `dev->dev` to `struct pci_dev`, calls `drm_get_pci_domain()`, formats the string with `kasprintf(GFP_KERNEL)`, returns `-ENOMEM` on allocation failure, and records the string length on success.

## State and Persistence

The only state mutation is `master->unique` and `master->unique_len`. The allocated string is owned by the DRM master lifecycle and must be freed by the existing DRM core cleanup path.

## Dependencies and Integration Points

It depends on Linux PCI helpers, DRM auth/master state, and the DRM interface-version compatibility contract. It is used by legacy userspace identity paths that query the DRM master unique string.

## Risks and Edge Cases

- The helper assumes the DRM device is backed by a PCI device; calling it for non-PCI devices would make `to_pci_dev()` invalid.
- The domain compatibility branch is a user ABI constraint and should not be simplified without considering old userspace.
- Allocation failure is the only expected runtime error.

## Test Signals

Test interface versions below and above `0x10004`, alpha versus non-alpha builds if practical, correct formatting for domain/bus/slot/function, and `kasprintf` failure injection.
