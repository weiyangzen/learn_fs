# sources/control-plane/rook/pkg/operator/ceph/csi/predicate.go

## Purpose
This file defines controller-runtime predicates controlling when the CSI controller reconciles for operator ConfigMap and CephCluster events.

## Important APIs, Types, and Functions
`cmPredicate` returns typed predicates for `ConfigMap` events. It accepts creates/deletes for the operator settings ConfigMap and updates when `.Data` changes according to `cmp.Diff`. `cephClusterPredicate` accepts CephCluster creates only when not a duplicate and either the operator config map is absent or the cluster generation is `1`; it ignores updates and accepts deletes.

## Control Flow, State, and Persistence
Predicates are pure event filters except `cephClusterPredicate`, which reads the operator config map and checks duplicate clusters through the controller-runtime client. They do not persist state.

## Dependencies and Integration Points
They integrate with `controller.OperatorSettingConfigMapName`, `opcontroller.DuplicateCephClusters`, Kubernetes API errors, go-cmp, and controller-runtime typed event/predicate APIs.

## Risks
The ConfigMap update comparison uses only `.Data`, so metadata or owner changes do not trigger reconciliation. CephCluster updates never trigger CSI reconcile, so CSI settings changed in cluster spec rely on other controllers/flows. The create predicate has nuanced behavior when the operator ConfigMap is absent to support env-var-only deployments.

## Test Signals
Tests cover create/delete/update behavior for operator ConfigMaps and CephCluster create filtering by generation, config-map presence, and duplicate cluster detection.
