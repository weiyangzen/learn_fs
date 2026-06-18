# sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config.go

## Purpose
This file maintains peer cluster and RBD pool ID mappings used by ceph-csi for RBD mirroring disaster recovery. It writes mappings to `rook-ceph-csi-mapping-config`.

## Important APIs, Types, and Functions
`PeerIDMapping` stores one peer-to-local cluster ID map and a list of peer-to-local RBD pool ID maps. `PeerIDMappings` has methods for adding cluster maps, adding pool maps, updating pool maps, JSON serialization, and lookup. `ReconcilePoolIDMap` skips pools without peer secrets, gets mappings, and calls `CreateOrUpdateConfig`. `getClusterPoolIDMap` reads local pool details, peer bootstrap secrets, decodes tokens, queries peer pool details through `ceph`, and builds mappings. `CreateOrUpdateConfig`, `UpdateExistingData`, `createConfig`, `decodePeerToken`, `getPeerPoolDetails`, and `getMapKV` support persistence and CLI interaction.

## Control Flow, State, and Persistence
State is persisted in a ConfigMap key `csi-mapping-config-json` in the operator namespace. New mappings are merged with existing config data unless it is exactly `[]`. Peer pool queries use temporary keyring, config, and output files and execute `ceph osd pool get ... --format json`.

## Dependencies and Integration Points
Dependencies include CephBlockPool mirroring peer secrets, Kubernetes Secrets/ConfigMaps, Rook Ceph client pool-detail parsing, operator deployment owner references, and the configured executor.

## Risks
Single-entry maps are assumed by `getMapKV`; empty maps silently produce empty keys. Config merging never removes stale peer/pool mappings. Peer secret token content and temp-file cleanup are critical. The command argument layout is tested indirectly and can be brittle.

## Test Signals
Tests cover cluster and pool map insertion/update, single and multi-peer mapping generation, token decoding, and create/update ConfigMap behavior with fake command output.
