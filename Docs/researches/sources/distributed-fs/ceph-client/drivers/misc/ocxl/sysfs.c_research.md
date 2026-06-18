# sources/distributed-fs/ceph-client/drivers/misc/ocxl/sysfs.c

Purpose: creates per-AFU sysfs attributes and a binary global-MMIO file, including mmap support for the AFU global MMIO area.

Important APIs and functions: attribute show/store functions cover `global_mmio_size`, `pp_mmio_size`, `afu_version`, `contexts`, and `reload_on_reset`. `global_mmio_read()`, `global_mmio_fault()`, and `global_mmio_mmap()` implement the `global_mmio_area` bin attribute. Exported internal APIs are `ocxl_sysfs_register_afu()` and `ocxl_sysfs_unregister_afu()`.

Control flow: registration creates scalar device files, initializes `attr_global_mmio`, and creates the bin file. The mmap path validates requested pages, marks the VMA `VM_IO | VM_PFNMAP`, uses noncached protection, and inserts PFNs from `global_mmio_start` in the fault handler. Unregister removes all scalar files and the bin file.

State and persistence: sysfs files reflect live `struct ocxl_afu` state. Writes to `reload_on_reset` call OCXL config space setters, altering device behavior rather than stored driver state.

Dependencies and integration points: uses the file-layer `struct ocxl_file_info`, PCI config helpers, sysfs/bin_attribute APIs, and VM PFN insertion. The global MMIO pointer and physical start are supplied by AFU discovery.

Risks and test signals: `global_mmio_read()` does not clamp `count` to remaining size after validating `off`, so a large read near the end can overrun the mapped MMIO range. Mmap boundary checks should cover offsets, zero-size MMIO, and SIGBUS beyond range. `reload_on_reset` should be tested on hardware with and without the capability.
