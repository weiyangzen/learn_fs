# sources/distributed-fs/ceph-client/tools/perf/tests/cpumap.c

Purpose: `cpumap.c` validates CPU map serialization, parsing, printing, merging, intersection, equality, and synthetic event decoding.

Important APIs and state: processors for synthetic CPU map events validate mask, explicit CPU list, and CPU range encodings. Test helpers use `perf_cpu_map__new`, `perf_event__synthesize_cpu_map`, `cpu_map__new_data`, `cpu_map__snprint`, `perf_cpu_map__merge`, `perf_cpu_map__intersect`, and `perf_cpu_map__equal`. The suite has multiple named test cases under `"CPU map"`.

Control flow: synthesis tests build maps that should choose mask, explicit CPUs, or range forms and validate the generated data. Print tests assert canonical string output. Merge and intersect tests build maps from strings and compare count and formatted result. Equality tests verify self-equality, inequality across empty/any/single/pair maps, and equality after merge/intersect transformations.

State and persistence: state is allocated CPU map objects with reference-count assertions; objects are put before exit. No files or kernel events are needed.

Dependencies, integration, risks, and tests: it depends on libperf cpumap internals and synthetic event layout. Risks include fragile expectations if canonical formatting changes. Test signals are exact map sizes, CPU values, strings, and reference counts.
