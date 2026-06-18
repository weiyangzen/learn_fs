# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pci.h

## Purpose
Declares the i915 PCI driver registration helpers and PCI BAR/resource validation helper.

## Important APIs, types, and functions
Forward declares `struct pci_dev`; exports `i915_pci_register_driver()`, `i915_pci_unregister_driver()`, and `i915_pci_resource_valid()`.

## Control flow
No runtime flow in the header.

## State and persistence
No header state. The implementation owns the static `pci_driver` and ID table.

## Dependencies and integration points
Used by module init/exit and probe support code.

## Risks
Registration helpers must remain paired by module init unwind. Resource validation semantics are shared with probe code.

## Test signals
Build coverage, module load/unload, and probe BAR validation paths.
