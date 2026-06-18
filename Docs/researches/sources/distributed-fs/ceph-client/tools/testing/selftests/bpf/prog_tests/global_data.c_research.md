
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data.c

## Purpose

`global_data.c` validates libbpf global data map relocation for `.bss`, `.data`, and `.rodata` numbers, strings, structs, and read-only enforcement.

## Important APIs, Types, and Functions

The test loads `test_global_data.bpf.o` as `BPF_PROG_TYPE_SCHED_CLS`, runs it with `bpf_prog_test_run_opts()`, locates result maps by name, and uses `bpf_map_lookup_elem()`. It also queries internal map aliases `test_glo.rodata` and `.rodata` and attempts `bpf_map_update_elem()`.

## Control Flow and Data Flow

After program run, helper functions validate numeric, string, and struct result maps against hard-coded expected relocations. The read-only subtest confirms the internal `.rodata` map is discoverable by both generated and ELF names and rejects updates with `EPERM`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is internal global-data maps and result maps produced by the BPF object. Dependencies include libbpf datasec support, scheduler classifier test-run, and global data relocation. Integration points are internal map naming, relocation emission, and read-only map enforcement. Risks are layout drift in the paired BPF object or result map names. Test signals are exact scalar/string/struct matches, `.rodata` alias equality, and failed `.rodata` update.
