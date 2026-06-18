# sources/control-plane/rook/pkg/operator/ceph/file/mds/test/0FS-2MDS.json

## Purpose
This fixture is a `ceph fs dump --format json` sample with no filesystems but two standby MDS daemons. It supports liveness probe tests proving that a daemon in the global standby list is considered healthy even before it joins a filesystem map.

## Important APIs, Types, and Functions
The JSON exposes top-level `epoch`, `default_fscid`, feature compatibility fields, `standbys`, and empty `filesystems`. The relevant standby names are `myfs-a-a` and `myfs-a-b`, both with `state: up:standby` and `join_fscid: -1`.

## Control Flow, State, and Persistence
The fixture is static test data embedded by `livenessprobe_test.go`. The probe's `jq` expression reads `.standbys | map(.name)` and should return true for `myfs-a-a` or `myfs-a-b` even though `.filesystems` is empty.

## Dependencies and Integration Points
It integrates with the rendered bash liveness probe and the Go test harness via `//go:embed`. It represents a Ceph state during early MDS startup or before filesystem association.

## Risks
The fixture validates standby presence but cannot prove filesystem correctness because no filesystem exists. If Ceph changes `fs dump` standby schema, the probe and fixture may diverge. Similar daemon names make it useful for name matching but also easy to misuse in unrelated tests.

## Test Signals
The expected signal is probe success for standby daemon IDs present in the top-level standby list, despite zero filesystems.
