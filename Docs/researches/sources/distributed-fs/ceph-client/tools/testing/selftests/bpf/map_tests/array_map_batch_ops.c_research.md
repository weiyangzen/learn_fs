# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/array_map_batch_ops.c

Purpose: validates batch update and lookup operations for array and per-CPU array BPF maps.

Important APIs and functions: `map_batch_update()` fills keys/values and calls `bpf_map_update_batch`; `map_batch_verify()` checks key/value relationships and visited coverage; `__test_map_lookup_and_update_batch(is_pcpu)` creates map, allocates buffers, and performs lookup-batch loops with varying step sizes. Public test entry `test_array_map_batch_ops()` runs normal and per-CPU variants after detecting possible CPUs.

Control flow: for each step from 1 to max_entries - 1, the test repopulates the map, clears buffers, repeatedly calls `bpf_map_lookup_batch` using the returned batch cursor, verifies total count and values, and counts successful step sizes.

State and persistence: map fd lives for each test case and is closed at end. Heap buffers hold keys, visited flags, and values; per-CPU values are laid out as `max_entries * nr_cpus` `__s64`s.

Dependencies and integration points: uses libbpf map create/batch APIs, `test_maps.h` `CHECK` macro, and `libbpf_num_possible_cpus`.

Risks: pointer arithmetic on `void *values` in lookup call depends on compiler extension; fixed `max_entries=10` gives focused but small coverage; failures continue through `CHECK` semantics rather than immediate returns.

Test signals: prints `test_array_map_batch_ops:PASS` and `test_array_percpu_map_batch_ops:PASS` when both variants pass.
