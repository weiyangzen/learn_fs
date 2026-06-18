# sources/distributed-fs/ceph-client/drivers/vfio/pci/nvgrace-gpu/main.c

Purpose: provides a VFIO PCI driver for NVIDIA Grace Hopper/Blackwell GPU PFs whose coherent device memory is described outside normal BAR sizing. It exposes usable and reserved GPU memory to guests through emulated 64-bit BAR regions and custom mmap/read/write behavior.

Important APIs and types: `struct mem_region`, `struct nvgrace_gpu_pci_core_device`, VFIO ops for open/close/ioctl/read/write/mmap/get_region_info, config-space BAR emulation, pfn address-space registration, P2P dmabuf physical range reporting, ACPI property parsing, device-ready polling, and reset tracking.

Control flow: probe first waits for C2C/HBM readiness through BAR0, reads ACPI memory properties, selects either enhanced ops or core fallback ops, detects the MIG hardware bug via NVIDIA DVSEC, partitions memory into `usemem` and optional `resmem`, and registers the VFIO device. Open enables VFIO core, initializes fake BAR values, maps BAR0, and registers PFN address spaces. Mmap routes fake BAR offsets to PFNMAP VMAs whose faults insert PFNs after runtime power and readiness checks. Read/write either emulate config BAR registers or map device memory with `memremap()`/`ioremap_wc()` and copy data.

State and persistence: in-memory state records physical address, actual length, rounded BAR size, emulated BAR value, kernel mapping, pfn address space, reset-readiness flag, and whether the old MIG workaround is needed. Mappings are lazily created and freed on close.

Dependencies and integration: uses VFIO PCI core, iommufd physical attach ops, pfn address-space helpers, runtime PM, PCI P2PDMA provider APIs, ACPI device properties, PCI config-space emulation, and memory-failure PFN mapping support.

Risks: fake BAR sizes are rounded up while real memory may be smaller, so reads beyond real memory must return all ones and writes must be dropped. First access after reset must be serialized against readiness polling to avoid RAS noise. Incorrect `resmem` cache attributes or pfn offset translation can break guest mappings.

Test signals: probe with and without ACPI properties, GH MIG-bug and GB fixed paths, config BAR read/write emulation, sparse region info, mmap faults including huge PFNMAP if enabled, read/write past actual but within reported BAR size, reset-done followed by first access, and P2P dmabuf range queries.
