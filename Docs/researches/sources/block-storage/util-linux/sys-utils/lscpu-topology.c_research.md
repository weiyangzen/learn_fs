# File Research: sources/block-storage/util-linux/sys-utils/lscpu-topology.c

`lscpu-topology.c` reads CPU topology, frequency, cache, and selected per-CPU status attributes from sysfs and `/proc/sysinfo`.

Key behavior:
- Builds unique core, socket, book, and drawer CPU-set maps per CPU type.
- Skips CPUs that are not fully online when hotplug state information is available.
- Reads s390 software topology from `/proc/sysinfo` and falls back to sysfs-derived ratios otherwise.
- Reads per-CPU physical topology IDs: core, socket/package, book, and drawer.
- Reads s390 polarization, physical address, and configured status attributes.
- Reads max/min/current CPU frequency from cpufreq sysfs.
- Reads standard cache topology from `cpuN/cache/indexM`, including type, level, ID, size, sharing map, allocation/write policy, line size, set count, and associativity.
- Provides a SPARC fallback for cache files such as `l1_icache_size`.
- Sorts caches by name and exposes helpers for total cache size and per-CPU cache lookup.

Important dependencies:
- `path_cxt` sysfs access helpers.
- CPU-set allocation and operations.
- Shared CPU and CPU-type structures.

Risk notes:
- Cache identity is based on type, level, and kernel cache ID; if ID is unavailable, it synthesizes one from sharing maps.
- SPARC fallback assumes caches are private when no sharing map exists.
- Topology ratios such as cores per socket are derived from counts and can be zero or misleading on unusual virtualized systems.
