# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bloom_filter_map.c

Purpose: validates bloom filter map creation constraints, update/lookup behavior, BPF-side bloom checking, and use as an inner map.

Important APIs/types/functions: `test_fail_cases` creates invalid bloom filter maps and invalid update flag combinations. `test_success_cases` creates a valid bloom filter with `BPF_F_ZERO_SEED | BPF_F_NUMA_NODE`. `setup_progs` loads `bloom_filter_map.skel.h`, fills random-data and bloom maps. `test_inner_map` creates a bloom filter inner map and stores it in an outer map. `check_bloom` attaches the checker program and triggers via `SYS_getpgid`.

Control flow: run negative creation/update tests, run simple create/update/lookup success test, load skeleton and random values, fill both random-data and bloom maps, test bloom filter as inner map, delete the inner map reference, then attach the main checker and trigger it.

State and persistence behavior: random values are heap allocated and stored in BPF maps; bloom filter maps hold probabilistic membership state. Inner map FD is closed after outer map cleanup. Skeleton maps are destroyed at the end.

Dependencies and integration points: bloom filter map kernel support, generated skeleton, syscall trigger, libbpf map create/update/lookup/delete APIs, and NUMA flags.

Risks: bloom filters can have false positives; the paired BPF program should account for intended behavior. Negative tests rely on exact `-EINVAL` for invalid flags. Random values are generated with `rand()` but only used within the same run.

Test signals: invalid cases return failures or `-EINVAL`; success path update/lookup succeeds; BPF checker and inner-map checker leave `skel->bss->error == 0`; inner map delete succeeds.
