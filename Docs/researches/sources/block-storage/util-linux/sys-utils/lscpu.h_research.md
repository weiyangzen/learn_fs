# File Research: sources/block-storage/util-linux/sys-utils/lscpu.h

`lscpu.h` is the shared interface and data model for all `lscpu` implementation files.

Key contents:
- Debug mask declarations for init, misc, gather, type, CPU, and virtualization domains.
- Sysfs/procfs path constants for CPU, node, DMI, ACPI PPTT, and Xen hypervisor features.
- `struct lscpu_cache` describing cache identity, type/name, policies, size, geometry, and shared CPU map.
- `struct lscpu_cputype` describing vendor/model/family strings, BIOS strings, topology counts, sibling maps, flags, frequency fields, s390/PowerPC-specific fields, and ISA.
- `struct lscpu_cpu` describing one logical CPU, including type reference, frequency fields, topology IDs, polarization, address, and configured state.
- `struct lscpu_arch`, `struct lscpu_virt`, `struct lscpu_vulnerability`, DMI structs, virtualization enums, output mode enums, and helper macros.
- Function declarations for CPU/type lifetime, parsing, topology, caches, architecture, virtualization, ARM/RISC-V formatting, DMI, memory chunks, and NUMA/vulnerability reads.

Important dependencies:
- util-linux core headers for allocation, cpuset, path handling, string parsing, I/O, bit operations, debug, and localization.

Risk notes:
- This header couples all `lscpu` modules around mutable shared structs.
- Reference-counted CPU and CPU-type ownership must be respected across modules.
- Field additions require coordinated updates in parsing, output, freeing, and architecture-specific decode paths.
