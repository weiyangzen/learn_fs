# sources/control-plane/mayastor/test/python/tests/ana_client/test_ana_client.py

## Purpose
Tests Linux ANA/multipath client behavior against multiple published Mayastor nexuses.

## Important APIs, Types, And Functions
Fixtures `create_replicas` and `create_nexuses` build pools/replicas and publish nexuses on `ms2`/`ms3`. Helpers connect multiple paths. Tests `test_io_policy` and `test_namespace_guid` inspect NVMe subsystem paths, sysfs virtual controller links, IO policy files, nexus info keys, and namespace identifiers.

## Control Flow
The suite disconnects all NVMe controllers, creates replicas on `ms0`/`ms1`, publishes two nexuses with the same GUID, connects both paths, asserts one multipath namespace, verifies path ANA state and sysfs policy, then checks namespace NGUID/EUI64 values.

## State And Persistence
State includes pools, replicas, nexuses, kernel NVMe connections, and sysfs multipath entries. Teardown disconnects NVMe and destroys nexuses/pools.

## Dependencies And Integration Points
Depends on `common.nvme`, `mayastor_pb2`, Docker fixtures, `/sys/class/nvme-subsystem`, `/sys/block/<dev>/queue/iopolicy`, and Linux NVMe multipath.

## Risks
Sysfs layout and path state names are kernel-version dependent. The tests use `glob` and fixed expectations for virtual controller counts.

## Test Signals
Passing tests indicate Mayastor ANA exports form a single multipath namespace with optimized live paths and correct namespace identity.
