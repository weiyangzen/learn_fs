<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pptt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pptt.c

## Purpose
`pptt.c` parses the ACPI Processor Properties Topology Table and uses it to describe CPU topology, cache hierarchy, cache properties, cache IDs, processor containers, package/cluster IDs, and heterogeneous core groupings. It is used by cacheinfo and architecture topology code when firmware supplies PPTT data.

## Important APIs, Types, and Functions
Public functions include `acpi_get_cache_info()`, `cache_setup_acpi()`, `acpi_pptt_cpu_is_thread()`, `find_acpi_cpu_topology()`, `find_acpi_cpu_topology_package()`, `find_acpi_cpu_topology_cluster()`, `find_acpi_cpu_topology_hetero_id()`, `acpi_pptt_get_cpus_from_container()`, `find_acpi_cache_level_from_id()`, and `acpi_pptt_get_cpumask_from_cache_id()`. Key internals are bounds-checked fetch helpers, cache walkers, processor-node search, cache property updates, topology-tag search, and lazy `acpi_get_pptt()`.

## Control Flow and State
The parser lazily maps the PPTT once and intentionally keeps it for runtime CPU hotplug/topology queries. Subtable fetches validate reference offsets, lengths, and table bounds. Processor-node search walks all subtables, matches ACPI processor UID, validates processor entry length including private resource references, and verifies leaf status. Cache queries walk private cache resources and parent processor nodes, count levels, detect split I/D levels, and update cacheinfo fields only when PPTT validity flags are set. Topology helpers walk parent pointers until a requested level, package flag, identical flag, or root is reached. Container/cache-ID helpers iterate possible CPUs and build cpumasks.

## State and Persistence
Persistent state is the cached PPTT table pointer and checked flag. Cacheinfo updates persist in per-CPU cacheinfo structures, including `fw_token`, size/line/sets/associativity/attributes/type/id. No firmware state is modified.

## Dependencies and Integration Points
The file depends on ACPI table structures, ACPI processor UID mapping, Linux cacheinfo, CPU masks, and topology consumers. It integrates with CPU hotplug paths and architectures that ask ACPI for cache and package/cluster/heterogeneity IDs.

## Risks and Test Signals
Risks include malformed relative offsets, zero-length subtables, duplicate cache level/type ambiguity, PPTT revision-dependent semantics for leaf and cache ID fields, CPU UID mismatches, and generated pointer-difference IDs changing with table layout. Test signals are warnings for missing or malformed PPTT, accurate cache level/split counts, cacheinfo overrides matching firmware, package/cluster sibling masks, thread flag detection on revision 2+, cache ID lookup on revision 3+, CPU hotplug topology stability, and fallback behavior when PPTT is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pptt.c -->
