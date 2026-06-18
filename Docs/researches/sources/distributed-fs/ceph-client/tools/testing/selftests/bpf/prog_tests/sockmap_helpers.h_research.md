<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h

Purpose: `sockmap_helpers.h` layers sockmap-specific convenience wrappers on top of `socket_helpers.h`. It standardizes failing wrappers for BPF map operations, BPF program attach/detach, pthread creation/join, scalar compound literals, and adding two sockets to a sockmap.

Important APIs/types/functions: `xbpf_map_delete_elem`, `xbpf_map_lookup_elem`, `xbpf_map_update_elem`, `xbpf_prog_attach`, `xbpf_prog_detach2`, `xpthread_create`, and `xpthread_join` mirror the socket wrappers and report selftest failures. `add_to_sockmap()` inserts `fd1` at key `0` and `fd2` at key `1` with `BPF_NOEXIST`. `u32(v)` and `u64(v)` provide addressable compound-literal keys/values.

Control flow: the macros call the underlying libbpf/syscall API, set `errno` where needed for pthread return codes, report failures, and return the raw result. `add_to_sockmap()` performs two updates and returns the second update result when the first succeeds.

State and persistence: the header keeps no state. It operates on caller-owned map/program/socket FDs.

Dependencies: depends on `socket_helpers.h`, libbpf/BPF syscall wrappers made visible through the including translation unit, pthreads for thread wrappers, and selftest failure macros.

Integration points: used by sockmap and kTLS tests to simplify map update and attach error handling while preserving selftest diagnostics.

Risks: like other assertion wrappers, failures are reported but callers must still respect return values. `add_to_sockmap()` assumes integer keys `0` and `1` and 64-bit socket FD values, matching sockmap selftest map definitions but not arbitrary maps.

Test signals: indirect; users should see clear selftest failures for map/attach/pthread errors, and `add_to_sockmap()` should populate two map entries without overwriting existing keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sockmap_helpers.h -->
