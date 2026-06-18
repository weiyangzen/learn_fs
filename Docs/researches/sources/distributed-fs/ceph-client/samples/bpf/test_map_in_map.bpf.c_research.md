<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c

## Purpose
`test_map_in_map.bpf.c` is the kernel-side half of a map-in-map self-test. It verifies that BPF programs can look up inner maps from array-of-maps and hash-of-maps outer maps, then perform both regular and inline inner-map lookups.

## Important APIs, Types, And Functions
Maps include `port_a`, `port_h`, `reg_result_h`, `inline_result_h`, `a_of_port_a`, `h_of_port_a`, and `h_of_port_h`. Helpers are `do_reg_lookup()`, `do_inline_array_lookup()`, `do_inline_hash_lookup()`, and syscall program `trace_sys_connect` attached to `ksyscall/connect`.

## Control Flow
The syscall program reads a user `sockaddr_in6` from `connect()`, filters for destination prefix `dead:beef`, uses the last IPv6 word as a test-case id, reads the port as the key, selects the matching outer map, looks up the inner map, performs a generic lookup, performs the expected inline array/hash lookup, and writes both results to result maps.

## State And Persistence
Persistent state is the set of BPF maps and their contents populated by userspace. Result maps store the latest regular and inline lookup return values at key zero.

## Dependencies And Integration Points
It depends on BTF/vmlinux, libbpf CO-RE macros, syscall tracing attachment, user memory reads, map-in-map verifier support, and the companion userspace file that populates maps and triggers `connect()`.

## Risks And Edge Cases
The program intentionally uses invalid `connect(-1, ...)` calls as triggers, so it must filter carefully. Inline helpers validate inner map identity and return `-EINVAL` if the verifier or map population did not preserve expected inner-map type. User pointer reads can fail and are reported through result maps.

## Test Signals
For test cases array-of-array, hash-of-array, and hash-of-hash, both `reg_result_h` and `inline_result_h` should equal the userspace magic value after the trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/test_map_in_map.bpf.c -->
