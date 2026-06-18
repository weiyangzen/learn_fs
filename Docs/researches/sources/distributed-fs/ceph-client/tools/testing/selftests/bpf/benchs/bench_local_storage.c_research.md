# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_local_storage.c

Purpose: defines three benchmark-harness entries for task local-storage lookup cost: sequential cache lookup, interleaved hot-map lookup, and a prepopulated hash-map control. It compares `BPF_MAP_TYPE_TASK_STORAGE` against ordinary hash maps through an array-of-maps populated from user space.

Important APIs and functions: `bench_local_storage_argp` parses `--nr_maps` and `--hashmap_nr_keys_used`; `validate()` enforces one producer, no consumers, `MAX_NR_MAPS`, and `HASHMAP_SZ`; `prepopulate_hashmap()` fills hash maps; `__setup()` opens/loads the skeleton, builds inner maps with BTF metadata, updates the map-in-map, and attaches `get_local`; setup variants select hash map versus local storage and sequential versus interleaved rodata flags. `producer()` repeatedly triggers the attached BPF program with `getpgid`.

Control flow: benchmark setup initializes libbpf, opens `local_storage_bench.skel.h`, configures rodata, loads the skeleton, creates requested maps, updates the map array, and attaches the selected BPF program. During execution, one producer loops forever; `measure()` atomically swaps BSS counters into `bench_res`.

State and persistence: all benchmark state is process-local except kernel BPF maps and links created for the run. BSS counters `hits` and `important_hits` are reset on each measurement. Created map fds are inserted into the map-in-map and then owned by the benchmark process/skeleton lifetime.

Dependencies and integration points: depends on the generic `bench.h` runner, libbpf map creation/update APIs, generated `local_storage_bench` skeleton, BTF type IDs for map creation, and reporting helpers `local_storage_report_progress/final`.

Risks: `HASHMAP_SZ` prepopulation is expensive and can dominate setup for large runs; `bpf_map_create()` fds are not explicitly closed after insertion; BTF mismatch between inner-map template and created maps would fail load/update; benchmark validity depends on synchronized constants with the BPF side.

Test signals: successful runs print local-storage throughput/latency summaries and reject unsupported producer/consumer counts before load. Useful regressions show up as attach/load failures, map update failures, or changes in `hits` versus `important_hits`.
