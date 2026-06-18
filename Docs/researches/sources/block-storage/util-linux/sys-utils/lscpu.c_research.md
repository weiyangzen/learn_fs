# File Research: sources/block-storage/util-linux/sys-utils/lscpu.c

`lscpu.c` is the main program and output layer for the `lscpu(1)` CPU architecture reporting utility.

Key behavior:
- Owns `struct lscpu_cxt` creation, path initialization, full data-gathering sequence, output mode dispatch, and cleanup.
- Defines CPU table columns, cache table columns, virtualization labels, hypervisor labels, dispatch modes, and polarization strings.
- Supports summary, extended table, parsable table, cache table, ARM implementer/model lookup, raw, JSON, byte sizes, physical IDs, sysroot snapshots, and hierarchical summaries.
- Formats per-CPU table cells for CPU ID, topology IDs, NUMA node, cache-sharing IDs, polarization, address, configured/online state, microcode, MHz values, and model name.
- Formats cache table rows for one-cache size, total system cache size, type, level, ways, policies, line partitions, sets, and coherency size.
- Builds the default summary from architecture, CPU masks, CPU type details, virtualization, caches, NUMA, and vulnerabilities.
- Coordinates data collection in order: CPU lists, cpuinfo, architecture, arch extras, vulnerabilities, NUMA, topology, ARM decode, virtualization.
- Uses environment variables `LSCPU_COLUMNS` and `LSCPU_CACHES_COLUMNS` for default custom columns.

Important dependencies:
- All companion `lscpu-*` modules and shared `lscpu.h`.
- `libsmartcols` for summary/table/JSON/raw output.
- util-linux sysfs/path, cpuset, parsing, annotation, and localization helpers.

Risk notes:
- Output defaults depend on gathered data, so missing sysfs/procfs attributes change column sets.
- Parsable output has a compatibility mode that treats cache columns specially with historical comma formatting.
- JSON type handling is adjusted when values are missing and rendered as `-`.
- Hierarchical summary defaults to TTY detection unless explicitly set.
