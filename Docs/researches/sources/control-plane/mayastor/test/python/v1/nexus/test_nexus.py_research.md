# sources/control-plane/mayastor/test/python/v1/nexus/test_nexus.py

Purpose: broad v1 nexus integration tests for mirrored nexus creation, failover, ENOSPC, NVMe controller metadata, reservation keys, and multi-child failure states.

Important APIs and control flow: fixtures create pools on `ms1`/`ms2`, replicas, a nexus on `ms3`, and optionally a second preempting nexus on `ms0`. `test_enospace_on_volume` uses `Volume` with two pool URIs and expects `RESOURCE_EXHAUSTED`. Async tests run fio or SPDK fio while killing `ms2`, then assert nexus/child states. `test_nexus_cntlid` connects with NVMe CLI and checks controller ID plus ONCS bits. `test_nexus_resv_key` connects directly to a child URI and validates reservation report fields. Skipped preempt-key test documents intended reservation preemption behavior.

State, dependencies, and integration: state spans pools, replicas, NVMf shares, published nexus devices, NVMe host connections, container failure, and reservation registrations. Dependencies include `v1.hdl`, `v1.volume`, fio helpers, NVMe CLI helpers, generated v1 protobuf modules, and asyncio.

Risks and test signals: some assertions assume child ordering. `Volume.create` may call an outdated handle signature, so ENOSPC coverage is fragile. The tests are high-signal for degraded/faulted transitions, NVMf metadata, reservation setup, and I/O failure handling.
