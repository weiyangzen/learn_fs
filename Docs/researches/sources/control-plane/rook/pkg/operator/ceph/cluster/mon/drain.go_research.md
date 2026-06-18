# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain.go

## Purpose

This file reconciles the monitor PodDisruptionBudget used to keep voluntary node drains from breaking Ceph monitor quorum. It adjusts `maxUnavailable` based on desired mon count and current quorum health.

## Important APIs and Control Flow

`reconcileMonPDB()` exits early when `ManagePodBudgets` is disabled or `spec.Mon.Count <= 2`. For larger mon sets, it queries `cephclient.GetMonQuorumStatus()`, computes how many mons are down as `len(mon map) - len(quorum)`, and subtracts that from the allowed unavailable count. The result is clamped at zero, which blocks additional drains while monitors are already down. If the existing PDB already has the same `maxUnavailable`, reconciliation returns without updating.

`createOrUpdateMonPDB(maxUnavailable)` uses controller-runtime `CreateOrUpdate` to maintain `rook-ceph-mon-pdb` in the cluster namespace. The selector targets pods labeled `app=rook-ceph-mon`, and `MaxUnavailable` is an integer value. `getExistingMaxUnavailable()` reads the current PDB, returning `-1` for not found. `getMaxUnavailableMonPodCount()` returns `2` for five or more mons and `1` otherwise.

## State, Persistence, and Dependencies

The persistent object is a Kubernetes `policy/v1.PodDisruptionBudget`. Runtime state comes from Ceph quorum status. The code depends on controller-runtime client APIs, Ceph quorum command helpers, Rook logging, and Kubernetes label conventions.

## Risks and Test Signals

The safety-critical risk is allowing too many monitor pods to be drained during partial quorum loss. Conservative clamping to zero mitigates that. Another risk is stale PDB values if the Ceph quorum query fails; in that case reconciliation fails instead of guessing. `drain_test.go` covers disabled management, low mon counts, 3/5 mon quorum states, down-mon clamping, idempotent second reconciliation, and the max-unavailable threshold helper.
