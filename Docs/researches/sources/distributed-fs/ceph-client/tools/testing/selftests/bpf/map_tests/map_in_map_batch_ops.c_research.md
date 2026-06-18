# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/map_tests/map_in_map_batch_ops.c

Purpose: verifies batch operations on map-in-map outer maps, covering `ARRAY_OF_MAPS` and `HASH_OF_MAPS` with inner array and hash maps. It validates that batch lookup and lookup-delete return map IDs that correspond to real inner maps and that array holes are handled correctly.

Important APIs/types/functions: `get_map_id_from_fd` reads `bpf_map_info.id`; `create_inner_maps` creates ten inner maps and stores each map's ID as its value; `create_outer_map` uses `bpf_map_create_opts.inner_map_fd`; `validate_fetch_results` reopens inner maps by ID and checks their contents; `fetch_and_validate` wraps `bpf_map_lookup_batch` and `bpf_map_lookup_and_delete_batch`; `_map_in_map_batch_ops` drives each map type combination.

Control flow: inner maps are created and initialized first. The outer map is created from the first inner map template, then populated with keys that differ for array and hash cases. The optional `has_holes` branch changes the final array key to leave key 1 absent. Batch lookup is run with batch sizes 5 and 10. For hash-of-maps, lookup-and-delete is also tested because array-of-maps cannot delete elements the same way.

State and persistence behavior: BPF map IDs outlive individual FDs while references remain in the outer map. Validation temporarily opens inner maps by ID and closes those FDs after lookup. The file carefully closes all original inner map FDs and the outer map FD at the end of each scenario.

Dependencies and integration points: depends on libbpf map create, info, update, batch, and map-id APIs plus `test_maps.h`. Exports `test_map_in_map_batch_ops_array` and `test_map_in_map_batch_ops_hash`.

Risks: the fetch loop retries on `ENOSPC` by increasing step size and resetting total, which handles hash batch short reads but can mask inefficient cursor behavior. Validation assumes each inner map has one key/value and that the value equals its map ID. It does not verify exact returned outer keys beyond total count and inner map identity.

Test signals: `CHECK` failures identify map creation, update, lookup, delete, open-by-ID, and inner value mismatch. PASS lines are emitted for each outer/inner combination including array holes.
