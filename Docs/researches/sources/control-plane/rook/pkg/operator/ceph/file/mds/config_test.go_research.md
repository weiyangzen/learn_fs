# sources/control-plane/rook/pkg/operator/ceph/file/mds/config_test.go

## Purpose
This test suite validates `setDefaultFlagsMonConfigStore`, especially how it derives `mds_cache_memory_limit` from MDS resource limits or requests and how custom factor fields override defaults.

## Important APIs, Types, and Functions
`TestSetDefaultFlagsMonConfigStore` builds `Cluster` instances with different `CephFilesystem.Spec.MetadataServer.Resources` and optional `CacheMemoryLimitFactor` or `CacheMemoryRequestFactor`. Each subtest installs a mock executor that inspects `ceph config set` calls for `mds_cache_memory_limit` and `mds_join_fs`.

## Control Flow, State, and Persistence
Subtests cover default limit factor for `1Gi`, custom limit factor `0.25`, default request factor for `512Mi`, custom request factor `0.6`, and no memory specified. The mock executor asserts the target daemon name `mds.myfs-a` and expected byte values, then `setDefaultFlagsMonConfigStore("myfs-a")` is called.

## Dependencies and Integration Points
The tests depend on Kubernetes resource quantity parsing, Rook Ceph config store command construction, mock executor utilities, and the `Cluster` struct. They validate command intent but do not talk to a real monitor config DB.

## Risks
Because config options are stored in a map, command order is nondeterministic; the mocks are permissive enough to tolerate this. The tests do not assert absence of `mds_cache_memory_limit` in the no-memory case except by only handling `mds_join_fs`, so an unexpected cache command could be missed if the mock returns success. They also do not cover executor errors.

## Test Signals
Signals are exact byte values `536870912`, `268435456`, `429496729`, and `322122547`, correct daemon identity, correct filesystem join target, and no error returned in all configured scenarios.
