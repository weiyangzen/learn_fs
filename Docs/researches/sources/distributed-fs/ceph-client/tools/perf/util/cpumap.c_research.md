# sources/distributed-fs/ceph-client/tools/perf/util/cpumap.c

Purpose: converts recorded CPU map data into libperf CPU maps, formats maps, builds aggregation maps, and discovers CPU/NUMA topology ids from sysfs.

Important APIs/functions: cpumap record decoding, `perf_cpu_map__empty_new`, `cpu_map__new_data`, formatting functions, `cpu_map__online`, `cpu_aggr_map__new`, max CPU/node helpers, CPU-to-node setup, topology id accessors, aggregation id constructors, and `aggr_cpu_id` helpers.

Control flow: decodes explicit entries, masks, or ranges into `perf_cpu_map`; builds aggregation maps by calling a supplied id getter, removing duplicates, trimming, and sorting; reads sysfs topology ids and possible/present CPU/node ranges; fills CPU-to-node map by walking node directories.

State and persistence: static globals cache max possible CPU, max present CPU, max node count, `cpunode_map`, and online CPU map.

Dependencies and integration: libperf cpumap internals, Linux bitmap helpers, sysfs helpers, dirent traversal, debug logging, and event record data. Used by stat aggregation, record header decoding, CPU selection, and topology reporting.

Risks: CPU ids are constrained to `INT16_MAX`. Sysfs failures lead to defaults. `cpu__get_node` requires prior setup and lacks bounds checks. `cpu_map__online` is thread unsafe.

Test signals: record types, 32/64-bit masks, endian variants, dummy CPU `-1`, sparse ranges, sysfs fallback, NUMA setup, aggregation duplicate removal/sorting, and formatting.
