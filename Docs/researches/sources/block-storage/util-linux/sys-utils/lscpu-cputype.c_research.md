# File Research: sources/block-storage/util-linux/sys-utils/lscpu-cputype.c

`lscpu-cputype.c` parses CPU type data, architecture data, CPU lists, NUMA maps, vulnerabilities, and architecture-specific extras for `lscpu`.

Key behavior:
- Defines field pattern tables for `/proc/cpuinfo` CPU-type, per-CPU, and cache lines across many architectures.
- Parses `/proc/cpuinfo` into `struct lscpu_cputype` and `struct lscpu_cpu` objects.
- Deduplicates CPU types by vendor, model, model name, and stepping, then reassigns CPUs to canonical type objects.
- Parses extra cache descriptors from `/proc/cpuinfo`, especially for s390 shared caches not represented in sysfs topology.
- Reads architecture name from `uname()` and derives 32-bit/64-bit operation modes from platform macros, CPU flags, ISA strings, and live architecture names.
- Reads CPU possible/present/online masks from sysfs and creates the per-CPU array.
- Reads dispatching, frequency boost, s390 machine type, and PowerPC RTAS physical topology data when available.
- Reads CPU vulnerability files from sysfs, normalizes names, and sorts them.
- Reads NUMA node directories and cpumaps from sysfs.

Important dependencies:
- `lscpu.h` structures and path constants.
- util-linux `path_cxt`, cpuset, string, allocation, and numeric parsing helpers.
- Optional `librtas` for PowerPC processor module information.

Risk notes:
- The parser assumes field pattern arrays stay sorted because it uses `bsearch()`.
- `lookup()` implements “first one wins” semantics for matched fields.
- `/proc/cpuinfo` varies heavily by architecture, so new kernel fields require carefully adding sorted patterns.
- Some data, especially vulnerabilities and NUMA maps, may be absent and is treated as optional.
