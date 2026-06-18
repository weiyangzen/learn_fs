# sources/distributed-fs/ceph-client/drivers/misc/ocxl/ocxl_internal.h

Purpose: central internal header for the OCXL driver, defining shared function, AFU, file, context, fault, and process-element data structures plus cross-file prototypes.

Important APIs and types: `struct ocxl_fn` tracks PCI function device state, BAR use, function config, AFU list, PASID/ACTAG ranges, and link handle. `struct ocxl_afu` carries AFU config, context accounting, IDR/mutex state, MMIO addresses, IRQ offsets, and private data. `struct ocxl_file_info` binds a cdev/device/bin attribute to an AFU. `struct ocxl_context` contains PASID state, mapping, wait queue, XSL error tracking, IRQ IDR, and TID. `struct ocxl_process_element` defines the 128-byte SPA hardware layout.

Control flow and integration: prototypes connect file registration, PASID/ACTAG allocation, config discovery/update, link PE update, context mmap/detach, sysfs registration, and AFU IRQ helpers. `ocxl_pci_driver` is exported to module init. The header coordinates implementations across `pci.c`, `link.c`, `mmio.c`, `sysfs.c`, context/file/config code, and AFU IRQ support.

State and persistence: all structures are kernel-resident live driver state. The header encodes locking ownership with named mutexes/IDRs but does not implement locking itself.

Dependencies: includes Linux PCI, cdev, list, and public `<misc/ocxl.h>`. It is private to the driver and should change in lockstep with all OCXL source files.

Risks and test signals: ABI-sensitive risks include `struct ocxl_process_element` layout, PASID/context counters, IDR lifetime, and mismatched prototypes. Compile-time checks in `link.c` validate process-element size; tests should exercise AFU registration/unregistration, context lifecycle, sysfs attributes, IRQ allocation/free, and public export consumers.
