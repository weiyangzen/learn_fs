# sources/control-plane/mayastor/io-engine/tests/nexus_children_add_remove.rs

Purpose: tests local uring-backed nexus child add/remove policies and remote replica add/remove under active I/O and concurrent qpair handle conditions.

Important APIs/types/functions: local tests use `nexus_create`, `nexus_lookup_mut`, `share_nvmf`, `remove_child`, `add_child`, and `destroy`. Compose tests use gRPC v1 `PoolBuilder`, `ReplicaBuilder`, `NexusBuilder`, `test_fio_to_nexus`, and Fio builders. Constants define pool/replica/nexus sizes.

Control flow: `remove_children_from_nexus` creates a two-child uring nexus, shares it, removes one child, verifies removing the last child fails, adds back an unsynced child, verifies removing the last healthy child fails, then destroys. `nexus_add_child` creates a two-child nexus, shares it, adds a third uring child, and destroys. `nexus_remove_child_with_io` creates two remote replicas and a published nexus, removes one child after a delay while fio runs for 10 seconds, and expects both tasks to complete. `nexus_channel_get_handles` creates three replicas across two remote and one local-to-nexus pool, then loops 20 times concurrently adding replica 0 and removing replica 2, restores original state, and asserts two children, reproducing/guarding qpair async/sync connect races.

State and persistence: local temp files `/tmp/disk1.img`..`disk3.img`; compose malloc pools/replicas; published NVMf nexus state. No durable metadata beyond test lifetime.

Dependencies and integration points: uring bdev provider, NVMf sharing, nexus child policy, rebuild/unsync state, fio workload, gRPC v1 storage builders, qpair/connection handling.

Risks and edge cases: uring support and fixed temp files. Concurrent add/remove test has explicit sleeps and can be timing-sensitive. Local tests share one Mayastor instance on reactor mask `0x2`.

Test signals: strong coverage for preventing removal of last/last-healthy child, dynamic child changes while shared, child removal during live I/O, and qpair handle race regressions.
