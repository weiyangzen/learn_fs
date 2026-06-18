<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c

## Purpose
`test_map_in_map_user.c` loads the map-in-map BPF object, populates inner and outer maps, triggers the syscall probe, and validates map lookup results for array-of-array, hash-of-array, and hash-of-hash cases.

## Important APIs, Types, And Functions
Important functions are `check_map_id()`, `populate_map()`, `test_map_in_map()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_object__find_program_by_name()`, `bpf_program__attach()`, `bpf_object__find_map_fd_by_name()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_map_get_info_by_fd()`, and `connect()`.

## Control Flow
`main()` opens `<argv[0]>.bpf.o`, loads it, resolves seven map fds, attaches `trace_sys_connect`, then calls `test_map_in_map()`. The test picks a random port key, populates inner maps and outer maps with map fds, checks outer maps expose the expected inner map ids, constructs `dead:beef::*:<testid>` IPv6 addresses, calls `connect(-1, ...)` to trigger BPF, and compares both result maps to the magic value.

## State And Persistence
State is all inside the loaded BPF object maps and the libbpf link. Results are deleted after each case. No pinned state survives process exit.

## Dependencies And Integration Points
It depends on libbpf, map-in-map kernel support, syscall tracing, and the companion BPF object. The invalid `connect()` is an intentional trigger path and should fail with `EBADF`.

## Risks And Edge Cases
The test uses `assert()` for most failures and returns zero on some setup failures for sample compatibility. Random key selection is masked to low 8 bits, avoiding broad coverage. Endianness of `sin6_port` is treated consistently with the BPF side for this test rather than as a real network port.

## Test Signals
The program should print `Array of Array: Pass`, `Hash of Array: Pass`, and `Hash of Hash: Pass`; result map mismatches print both values and exit with failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map_user.c -->
