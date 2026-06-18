# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/veristat.c

## Purpose

`veristat.c` is a command-line tool for measuring, replaying, sorting, filtering, and comparing BPF verifier statistics for BPF object files. It can load each program from one or more objects, collect verifier duration/state/instruction/stack/JIT-size/memory metrics, emit table or CSV output, replay saved CSV, and compare a baseline CSV against a comparison CSV with absolute and percentage deltas.

## Important APIs, Types, and Functions

Core data types are `enum stat_id`, `enum stat_variant`, `struct verif_stats`, `struct verif_stats_join`, `struct stat_specs`, `struct filter`, `struct rvalue`, `struct field_access`, and `struct var_preset`. Key functions include `parse_arg`, `append_filter`, `append_file`, `parse_stat`, `parse_verif_log`, `guess_prog_type_by_ctx_name`, `fixup_obj_maps`, `fixup_obj`, `create_stat_cgroup`, `process_prog`, `append_var_preset`, `set_global_vars`, `process_obj`, `parse_stats_csv`, `handle_comparison_mode`, `output_prog_stats`, `handle_verif_mode`, `handle_replay_mode`, and `main`. It uses libbpf, BTF, libelf, cgroup v2 memory accounting, argp, and optional `bpftool` dumps.

## Control Flow

Startup parses argp options into global `env`, resolves default output/sort specs, and selects comparison, replay, or live verification mode. Live mode optionally creates `/sys/fs/cgroup/veristat-accounting-<pid>` for memory peak accounting, opens each BPF ELF object, disables pinning, normalizes map sizes, applies BTF global-variable presets, prepares the object, clones each program with verifier log options, parses verifier log tail lines, fetches JIT info, optionally dumps xlated/JIT code, sorts results, and emits output. Replay parses one CSV and uses the normal output path. Comparison parses two CSVs, validates matching columns, sorts by file/program key, joins mismatched rows with missing sides, applies comparison filters, and emits A/B/diff columns.

## State and Persistence Behavior

Most state is process-local in `env`: input filenames, filters, stat arrays, presets, cgroup paths, and output specs. External state includes temporary loaded BPF programs, optional cgroup v2 accounting directory, open memory.peak fd, and possible `bpftool` subprocess output. Cleanup closes BPF objects/program fds, destroys the stat cgroup, frees allocations, and restores libbpf print callbacks.

## Dependencies and Integration Points

The tool integrates with selftests BPF object output, libbpf object/program/map APIs, BTF datasec/global variable metadata, verifier log format, cgroup v2 `memory.peak`, ELF object detection, and CI workflows that track verifier performance regressions. `veristat.cfg` provides a default object glob set for complex selftest objects.

## Risks and Test Signals

Risks include verifier log format drift, CSV parser limitations around commas/escaping, cgroup v2 unavailability, BTF preset resolution edge cases, assumptions in freplace context-type guessing, map-size fixups hiding object bugs, and command injection exposure if untrusted program IDs reach the `bpftool` command path. Signals include successful object skip/load accounting, stable CSV round-trips, comparison joins with missing rows, filter correctness for name/stat filters, memory-peak availability, BTF global preset application including arrays/enums, and accurate parsing of verifier duration/processed/stack lines.
