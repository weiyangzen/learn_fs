# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_get_next_key.c

Purpose: stress/regression test for concurrent `bpf_map_get_next_key` on an LPM trie. The stated success condition is absence of kernel panic or userspace crash while many threads repeatedly iterate from the same key.

Important APIs/types/functions: `struct test_lpm_key` stores prefix and data; `struct get_next_key_ctx` shares start/stop flags, the map FD, key, and loop count. `get_next_key_fn` busy-waits for start and repeatedly calls `bpf_map_get_next_key`. `abort_get_next_key` unblocks and joins already-created threads on setup failure. Entry point is `test_lpm_trie_map_get_next_key`.

Control flow: create a no-prealloc LPM trie whose `max_entries` covers all possible prefix lengths for the data field, insert prefixes from 0 to max prefix length, copy the final key into the shared context, spawn up to eight threads, release them by setting `ctx.start`, and join after each thread performs 65,536 calls or sees stop.

State and persistence behavior: shared state is a single mutable context with non-atomic bool flags and a read-only key/map FD after setup. The map contents remain constant during the stress phase. All state is process-local and the map FD is closed at the end.

Dependencies and integration points: uses pthreads, libbpf map APIs, `test_maps.h`, and the map test runner via `test_lpm_trie_map_get_next_key`.

Risks: because return values from `bpf_map_get_next_key` inside worker threads are intentionally ignored, semantic regressions in returned keys are not detected. The `start`/`stop` flags are plain bools, which is acceptable for this stress pattern but not a strict synchronization model. The test assumes enough thread resources to create eight workers.

Test signals: setup uses `CHECK` for map creation, element insertion, and thread creation. Once setup succeeds, the main signal is all worker joins returning without process failure, followed by `PASS`.
