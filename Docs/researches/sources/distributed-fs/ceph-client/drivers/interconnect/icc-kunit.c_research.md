# sources/distributed-fs/ceph-client/drivers/interconnect/icc-kunit.c

Purpose: KUnit tests for core interconnect topology, aggregation, bandwidth votes, tags, enable/disable, and bulk helpers.

Important APIs/types/functions: `test_topology[]` models CPU/GPU to BUS to DDR. `struct icc_test_priv` owns provider/device/nodes. Tests cover topology integrity, `icc_set_bw()`, shared-node aggregation, and bulk operations.

Control flow: suite init creates a platform device, registers a synthetic provider, creates nodes and links, and calls `icc_sync_state()`. Helpers manually allocate mock `icc_path` objects and attach requests to node hlist state.

State and persistence: nodes are registered in the real core and removed at suite exit. Mock path requests are explicitly detached before freeing.

Dependencies/integration: KUnit, KUnit platform device helpers, interconnect core internals, `bulk.c` helpers.

Risks and test signals: good coverage for sum/max aggregation, disabled votes, tag propagation, and bulk enable/disable. It bypasses OF lookup, provider user counts, and real path search, so those need separate tests.
