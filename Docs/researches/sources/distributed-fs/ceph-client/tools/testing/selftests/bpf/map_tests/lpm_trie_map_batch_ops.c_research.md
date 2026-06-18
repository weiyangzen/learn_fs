# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/lpm_trie_map_batch_ops.c

Purpose: validates batch update, lookup, and delete operations on LPM trie maps using IPv4 `/32` keys. It checks that batched traversal returns every inserted entry and that batched deletion drains the map for multiple step sizes.

Important APIs/types/functions: `struct test_lpm_key` combines a prefix field and `struct in_addr`. `map_batch_update` prepares `192.168.1.N` keys and values and calls `bpf_map_update_batch`. `map_batch_verify` validates returned key/value pairs by formatting the IPv4 address and comparing the final octet with the stored value. `test_lpm_trie_map_batch_ops` creates the map and drives lookup/delete loops with `bpf_map_lookup_batch`, `bpf_map_delete_batch`, and `bpf_map_get_next_key`.

Control flow: the test creates a no-prealloc LPM trie with ten entries. For each step size from 1 to 9, it repopulates the map, zeroes result arrays, walks batches until `ENOENT`, verifies that all entries were visited, deletes the same keys in batches of the current step, then confirms the map is empty by expecting `bpf_map_get_next_key(NULL)` to fail with `ENOENT`.

State and persistence behavior: state is only a transient BPF map plus heap arrays for keys, values, and visitation. Batch cursor state is the userspace `__u64 batch` token passed as in/out batch. No state persists after the map FD is closed and arrays are freed.

Dependencies and integration points: uses libbpf batch APIs, `test_maps.h`, IPv4 conversion via `inet_pton`/`inet_ntop`, and standard allocation. Exported `test_lpm_trie_map_batch_ops` is invoked by the map test runner.

Risks: `map_batch_verify` treats the returned order as arbitrary but assumes every address encodes an integer 1..10; malformed output could index `visited` incorrectly if the kernel returned an unexpected lower byte. The test does not cover prefixes other than `/32` or mixed prefix lengths, leaving more complex trie-order batch behavior to other tests.

Test signals: errors are surfaced through `CHECK`. Successful completion means every step size returned exactly ten entries, key/value pairs matched the encoded IPv4 address, batched delete removed all entries, and the final empty-map probe returned `ENOENT`.
