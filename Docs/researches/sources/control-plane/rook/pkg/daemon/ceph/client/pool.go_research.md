# sources/control-plane/rook/pkg/daemon/ceph/client/pool.go

This file implements Ceph pool lifecycle helpers for the Rook Ceph client package. Its public API covers listing pool summaries, reading pool details and stats, creating replicated or erasure-coded pools, deleting pools, setting pool properties/quotas/replica size, and cleaning unused CRUSH rules.

Important types are `CephStoragePoolSummary`, `CephStoragePoolDetails`, `CephStoragePoolStats`, and `PoolStatistics`, all JSON-bound to Ceph CLI or RBD CLI output. Creation flows route through `CreatePoolWithPGs()`: validate name, override applications for built-in pools, dispatch replicated versus erasure-coded, create EC profiles when needed, then set common properties. Replicated pools coordinate CRUSH rule creation/update under `crushRuleMutex` so `CleanupUnusedCrushRules()` cannot delete a rule between creation and pool attachment.

State is persisted in Ceph itself through `ceph osd pool`, `ceph osd crush`, `rbd pool stats`, pool quotas, pool app tags, mirroring settings, and temporary CRUSH map files. Integration points include Ceph command wrappers, erasure-code profile helpers, CRUSH map helpers, mirroring/snapshot scheduling helpers, Kubernetes resource quantity parsing, and cluster stretch/hybrid storage specs.

Risks center on CLI output shape, malformed multi-object JSON from `osd pool get all`, CRUSH cleanup races, partial failures in property application where some errors are logged but reconciliation continues, and destructive pool deletion. Tests in `pool_test.go` exercise EC/replicated creation, application tags, CRUSH update/cleanup behavior, statistics parsing, replica size confirmation flags, stretch/two-step/hybrid CRUSH rules, and optional `crushtool` paths.
