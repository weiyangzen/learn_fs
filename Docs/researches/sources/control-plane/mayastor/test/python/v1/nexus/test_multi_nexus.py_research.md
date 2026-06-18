# sources/control-plane/mayastor/test/python/v1/nexus/test_multi_nexus.py

Purpose: stress-style v1 nexus tests that create many replicas/nexuses across nodes and run raw, filesystem, and SPDK fio while killing a child node.

Important APIs and control flow: constants create 15 nexuses and destroy 7 replicas in restart tests. `create_replicas_on_all_nodes` creates one aio pool per node, then 15 replicas per node while checking used-space deltas and list counts. `test_restart` kills/restarts `ms1`, reconnects, reimports the pool, verifies replica persistence, destroys 7 replicas, restarts again, and validates remaining count. `create_nexuses` builds published nexuses on `ms1` from replicas on `ms2`/`ms3`. Async tests connect NVMe devices or use SPDK fio and kill `ms3` during I/O.

State, dependencies, and integration: state includes `/tmp/<node>.img`, imported pools, persisted replicas, published NVMf devices, mounts under `/mnt<dev>`, and container lifecycle. Dependencies include fio helpers, NVMe CLI helpers, asyncio, pytest-asyncio, and `v1.mayastor`.

Risks and test signals: cleanup of `/mnt/dev` looks generic and may not match all mount paths. Killing nodes mid-fixture can complicate teardown. Signals cover persistence after restart and I/O survival during child-node loss.
