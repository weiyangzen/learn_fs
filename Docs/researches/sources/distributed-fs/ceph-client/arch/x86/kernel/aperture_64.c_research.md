# sources/distributed-fs/ceph-client/arch/x86/kernel/aperture_64.c

## Purpose
`aperture_64.c` is early boot firmware-replacement and validation code for the AMD64 GART/AGP aperture. It detects broken or missing BIOS aperture setup, scans AGP bridges and AMD northbridges before the PCI subsystem is fully initialized, reserves or allocates a low-memory aperture hole, fixes northbridge aperture registers, and protects kdump/vmcore from reading RAM remapped as a GART aperture.

## Important APIs, Types, and Functions
- Global aperture policy: `gart_iommu_aperture`, `gart_iommu_aperture_disabled`, `gart_iommu_aperture_allowed`, `fallback_aper_order`, `fallback_aper_force`, and `fix_aperture`.
- Core exclusion state: `aperture_pfn_start`, `aperture_page_count`, `gart_mem_pfn_is_ram()`, `gart_oldmem_pfn_is_ram()`, and `exclude_from_core()`.
- Allocation/discovery helpers: `allocate_aperture()`, `find_cap()`, `read_agp()`, and `search_agp_bridge()`.
- Command-line parser: `gart_fix_e820`.
- Early kexec/kdump guard: `early_gart_iommu_check()`.
- Main aperture setup: `gart_iommu_hole_init()`.

## Control Flow
`early_gart_iommu_check()` runs before normal PCI and verifies any already-enabled GART aperture. It scans AGP bridges, reads AMD northbridge aperture base/order/enable state, detects inconsistent nodes, reserves enabled aperture RAM in e820 when requested, and disables GART on all northbridges if no valid AGP bridge owns the aperture.

`gart_iommu_hole_init()` later performs the main fixup. It skips if no AMD GART is present, aperture fixup is disabled, or early PCI access is unavailable. It optionally reads the AGP bridge aperture, walks AMD northbridge ranges, disables GART translation before reconfiguration, records that GART IOMMU should initialize through `x86_init.iommu.iommu_init = gart_iommu_init`, validates each node's aperture base/size, and decides whether firmware setup is usable. If fixup is needed, it uses the AGP aperture or allocates aligned low memory via memblock, excludes the range from core/vmcore, programs all northbridge aperture registers without enabling translation yet, and calls `set_up_gart_resume()` so `amd_gart_64.c` can restore the settings after suspend.

## State and Persistence Behavior
The file mutates e820 reservations, memblock allocations, nosave ranges, vmcore/kcore PFN filters, northbridge PCI config registers, and `x86_init.iommu.iommu_init`. Allocated aperture memory is intentionally lost to normal RAM use. `fallback_aper_order` and command-line flags persist as boot policy.

## Dependencies and Integration Points
It depends on early PCI config access, AMD northbridge detection (`early_is_amd_nb()` and `amd_nb_bus_dev_ranges`), AGP capability parsing, GART register definitions, e820/memblock, kdump/vmcore/kcore callbacks, suspend nosave regions, IOMMU initialization in `amd_gart_64.c`, and x86 init hooks.

## Risks
- Allocating the aperture over RAM permanently removes that RAM from normal use and must be low enough for 32-bit DMA use.
- Incorrect e820 reservation can cause kexec/kdump memory corruption when the first kernel leaves GART enabled.
- The loops directly program PCI config before full PCI enumeration; bad detection can disable or misconfigure real hardware.
- Aperture size/order must match across all northbridges; inconsistent firmware triggers fixup or panic if allocation fails.

## Test Signals
- Boot affected AMD64 systems with broken/missing aperture firmware and memory above 4 GiB.
- Test `gart_fix_e820=0/1`, `iommu=memaper`, `iommu=noaperture`, and fallback aperture sizing.
- Run kexec/kdump and verify vmcore does not read the GART aperture region.
- Suspend/resume with GART fixup and confirm `amd_gart_64.c` restores aperture registers.
