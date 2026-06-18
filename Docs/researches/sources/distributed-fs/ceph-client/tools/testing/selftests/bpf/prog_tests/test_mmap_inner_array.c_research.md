<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c

Purpose: verifies that an inner array map can be mmaped from user space and later referenced through an outer map by a BPF program.

Important APIs/types/functions: generated `mmap_inner_array` skeleton, `mmap()` on `inner_array` fd, `mmap_inner_array__attach()`, `bpf_map__update_elem()` on `outer_map`, BSS flags `pid_match`, `outer_map_match`, `done`, and data `match_value`.

Control flow: load skeleton, mmap one page from the inner array map, attach BPF, set target pid, wait briefly and confirm pid matched but outer map not yet configured and mmaped value remains zero. Then insert the inner-map fd into the outer map keyed by pid, wait again, and confirm the program matched the outer map and wrote the expected value.

State and persistence: one shared mmap region and skeleton BSS/data fields. The mmap is unmapped and skeleton destroyed.

Dependencies and integration: requires mmapable BPF array map semantics, map-in-map update support, and generated skeleton. Integrated as `test_mmap_inner_array`.

Risks: timing uses `usleep(1)` and assumes the attached program is triggered often enough. Map-in-map fd lifetime and mmap visibility are the main kernel contracts under test.

Test signals: before and after assertions distinguish pid match, outer map match, completion, and exact mmaped value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_mmap_inner_array.c -->
