# sources/control-plane/rook/pkg/daemon/ceph/client/radosnamespace.go

This file manages RBD/RADOS namespaces within a pool. It exposes create, delete, list, and internal statistics checks used by pool deletion safety and namespace reconciliation.

`CreateRadosNamespace()` runs `rbd namespace create --pool --namespace`, treating `EEXIST` as success. `getRadosNamespaceStatistics()` runs `rbd pool stats --pool --namespace` with JSON output and treats `ENOENT` as an empty `PoolStatistics`. `checkForImagesInRadosNamespace()` reports whether images or snapshots exist. `DeleteRadosNamespace()` refuses deletion when the stats check reports images, then runs `rbd namespace remove`, treating `ENOENT` as successful absence. `ListRadosNamespacesInPool()` parses `rbd namespace list` JSON objects into a string slice.

State is persisted in Ceph's RBD namespace metadata and queried via RBD CLI. Dependencies include `PoolStatistics` from `pool.go`, syscall exit-code interpretation through `exec.ExitStatus`, and shared command wrappers. Integration points include `IsPoolEmpty()` in `pool.go`, which calls the image check for each namespace before deleting a pool.

Risks include interpreting exit codes consistently across RBD versions, returning `containsImages` with wrapped errors during delete preflight, and not checking trash counts in emptiness logic. There is no dedicated test file in this work item for namespace creation/deletion/listing, so coverage is indirect through pool emptiness logic and command-wrapper conventions.
