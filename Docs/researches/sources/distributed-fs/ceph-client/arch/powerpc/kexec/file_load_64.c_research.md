# sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load_64.c

## Purpose
Implements 64-bit PowerPC architecture support for `kexec_file_load`: loader registration, excluded ranges, crashdump segments, purgatory symbols, FDT sizing and mutation, usable-memory restrictions, PCI DMA node updates, and cleanup.

## Important APIs, Types, And Functions
Defines `kexec_file_loaders`, `arch_check_excluded_range`, `load_crashdump_segments_ppc64`, `setup_purgatory_ppc64`, `kexec_extra_fdt_size_ppc64`, `setup_new_fdt_ppc64`, `arch_kexec_kernel_image_probe`, and `arch_kimage_file_post_load_cleanup`. Internal helpers manage `struct umem_info`, usable-memory buffers, dynamic reconfiguration memory, backup segments, elfcorehdr segments, CPU node sizing, property copying, and PCI DMA properties.

## Control Flow
Image probing first gathers excluded memory ranges and delegates to generic loader probing. For kdump, helpers allocate a dummy backup segment for the first 64K, build an ELF core header segment with optional hotplug headroom, and add usable-memory properties to memory nodes and dynamic LMBs so the capture kernel uses only crashkernel memory. FDT setup updates CPU nodes, direct/DMA64 PCI window properties for LPAR, memory reserve map entries, backup reservations, crash usable-memory restrictions, and PLPKS password data. Purgatory setup calls the common helper, sets `run_at_load` for crash kernels, writes backup/OPAL symbols, and reports errors.

## State And Persistence
Mutates `struct kimage` architecture fields: exclude ranges, backup buffer/start, ELF headers, FDT pointer, and purgatory symbols. It also mutates the loaded FDT blob by adding properties and reservations. Cleanup frees all architecture allocations and delegates to generic cleanup.

## Dependencies And Integration Points
Depends on generic kexec-file loaders, crash memory range helpers, libfdt, Open Firmware live tree, DRMEM/LMB APIs, pseries firmware features, IOMMU PCI DMA properties, PLPKS, OPAL device-tree properties, and common helpers in `file_load.c`.

## Risks And Edge Cases
Usable-memory property construction must correctly intersect crash ranges with memory nodes and dynamic LMBs; existing `linux,drconf-usable-memory` rejects kdump load. FDT extra-size estimation must cover hotplug CPU nodes, usable-memory data, reserved ranges, and PLPKS data. Backup/elfcorehdr segment ownership and cleanup must avoid leaks. LPAR PCI DMA properties must match live firmware state.

## Test Signals
`kexec_file_load` and kdump tests with static and dynamic memory, LPAR PCI devices, OPAL systems, PLPKS availability, CPU hotplug, memory hotplug, crashkernel ranges, FDT inspection, excluded-range placement failures, and cleanup paths should cover this file.
