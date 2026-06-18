# sources/distributed-fs/ceph-client/drivers/char/agp/amd64-agp.c

## Purpose
This file implements AGPGART support for AMD Opteron/Athlon64 on-CPU GARTs and external AGP bridges such as AMD 8151, VIA, SiS, ULi, and NVIDIA nForce3.

## Important APIs, Types, and Functions
Key functions are `amd64_insert_memory()`, `amd64_fetch_size()`, `amd64_configure()`, `amd_8151_configure()`, `amd64_cleanup()`, `agp_aperture_valid()`, `fix_northbridge()`, `cache_nbs()`, `amd8151_init()`, `uli_agp_init()`, `nforce3_agp_init()`, `agp_amd64_probe()`, `agp_amd64_remove()`, `agp_amd64_resume()`, and non-static `agp_amd64_init()`. The bridge driver is `amd_8151_driver`.

## Control Flow
Probe enforces one bridge, verifies AGP capability, allocates a bridge, applies AMD 8151 revision quirks, reads mode, validates/fixes each AMD northbridge aperture, optionally shadows aperture settings into NVIDIA or ULi bridge registers, then registers the bridge. Configuration writes the generic GATT table address into every AMD northbridge GART and flushes all GARTs. Memory insertion validates type/range/empty PTEs, flushes CPU caches once, converts physical pages into AMD GART PTE format, writes entries, and flushes GARTs.

If no supported bridge matches and `agp_try_unsupported` or boot `agp=try_unsupported` is allowed, init dynamically adds IDs for any AGP-capable PCI device on systems with AMD64 northbridges.

## State and Persistence Behavior
State includes a requested aperture memory resource, `agp_bridges_found`, generic GATT table state, and AMD northbridge GART registers. Cleanup disables GART translation on all northbridges and releases aperture resources during module exit/remove.

## Dependencies and Integration Points
It depends on x86 AMD northbridge helpers, e820/aperture validation, generic AGP backend, AMD GART/IOMMU helpers, PCI dynamic IDs, and chipset-specific shadow registers for ULi/nForce3.

## Risks
Aperture validation is critical because a bad aperture can conflict with PCI mappings or exceed 32-bit bridge limits. Multiprocessor systems must program all northbridges coherently. `agp_amd64_remove()` releases a region using `virt_to_phys(gatt_table_real)` and aperture size, while `agp_aperture_valid()` requested `aper`; resource accounting needs scrutiny. Unsupported dynamic IDs can bind to bridges with untested quirks. Built-in interaction with `gart_iommu_aperture` changes init/exit behavior.

## Test Signals
Test AMD64 systems with AMD 8151, VIA, ULi, nForce3, and unsupported-bridge paths; validate aperture conflict detection, all-node GART programming, memory bind/unbind, suspend/resume reconfiguration, dynamic-ID fallback, and coexistence with GART IOMMU aperture setup.
