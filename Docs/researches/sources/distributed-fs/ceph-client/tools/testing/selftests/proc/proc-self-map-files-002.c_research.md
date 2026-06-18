# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-002.c

Purpose: extends the map_files parser test to a low virtual address near `vm.mmap_min_addr`, catching boundary parsing and leading-zero behavior at small addresses.

Important APIs and functions: same `pass()` and `fail()` readlink helpers as the first test. Uses `mmap(MAP_FIXED)` in page increments below 1 MiB until a low address mapping succeeds.

Control flow: open `/dev/zero`, scan low addresses for a successful fixed one-page mapping, compute its canonical start/end, then require exact lookup success and malformed lookup `ENOENT`.

State and persistence: transient low-address mapping only.

Dependencies and integration: depends on system `mmap_min_addr` policy allowing some mapping below 1 MiB. Failure to map any low address is reported as test failure, not skip.

Risks and test signals: hardened systems may reject all requested low mappings. Semantic failures indicate map_files parser accepting noncanonical or overflowed address strings.
