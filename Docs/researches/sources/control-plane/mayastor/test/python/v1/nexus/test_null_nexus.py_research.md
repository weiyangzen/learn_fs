# sources/control-plane/mayastor/test/python/v1/nexus/test_null_nexus.py

Purpose: v1 nexus test that creates many nexuses backed by shared null bdevs and runs fio against all published devices.

Important APIs and control flow: `check_nexus_state` asserts every nexus and child is online. Fixtures define three device nodes and one nexus node, create 15 null bdevs per device node, share every bdev, create 15 nexuses on `ms3` from zipped child share URIs, publish all nexuses, connect all devices via NVMe, and clean up bdevs/nexuses/shares. `test_null_nexus` checks state and runs fio randwrite across connected devices.

State, dependencies, and integration: state includes null bdevs, NVMf share URIs, published nexuses, NVMe host connections, and fio activity. It depends on `NEXUS_DONT_READ_LABELS=true` in compose, `common.nvme`, `common.fio`, and v1 handle wrappers.

Risks and test signals: enum use comes from legacy `mayastor_pb2` while handles use v1 nexus methods, so compatibility matters. Null devices cannot be read, limiting verification to write behavior. Signals are online state for every child and successful fio completion.
