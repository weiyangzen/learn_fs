# sources/control-plane/rook/cmd/rook/ceph/mgr.go

## Purpose

Defines the Ceph manager sidecar command that watches the active mgr daemon and updates Kubernetes labels accordingly.

## Important APIs, Types, and Functions

Commands are `mgrCmd` and `mgrSidecarCmd` (`watch-active`). Flags include dashboard and monitoring enablement, update interval, cluster ID/name, daemon name, raw Ceph version, and shared Ceph flags. `runMgrSidecar()` initializes cluster info and loops forever. `reconcileMgr()` compares current active mgr to the previous active mgr and calls `mgr.SetMgrRoleLabel`.

## Control Flow

On startup, the sidecar reads the mounted Ceph secret, parses monitor endpoints, logs flags, builds owner info, writes Ceph config, parses the update interval and Ceph version, then repeatedly reconciles labels and sleeps. Reconciliation fetches active mgr from Ceph, skips label updates when unchanged, refreshes the current CephCluster spec from Kubernetes, constructs a mgr controller helper, and updates the local daemon's `mgr_role` label based on active status.

## State and Persistence Behavior

The command writes Ceph config locally and persistently mutates Kubernetes pod/service labels through the mgr controller. It tracks only `activeMgr` in process memory between loops.

## Dependencies and Integration Points

It integrates with Ceph monitor secrets, Rook clientsets, Ceph mgr client APIs, Kubernetes owner references, Ceph version parsing, operator mgr controller logic, and monitoring/dashboard label preservation.

## Risks and Edge Cases

Invalid intervals or Ceph version strings terminate startup. The infinite loop only logs reconcile errors and continues. Label correctness depends on active mgr names matching daemon names and on being able to refresh the CephCluster spec each time active mgr changes.

## Test Signals

Unit tests can target `reconcileMgr` with fake mgr/client behavior; integration tests validate active mgr label updates and service routing during mgr failover.
