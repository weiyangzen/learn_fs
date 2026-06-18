# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/mgr_test.go

## Purpose

This file is the main unit test suite for Rook's Ceph manager cluster controller. It exercises manager startup, deployment/service reconciliation, active/standby role labeling, module configuration, Prometheus module behavior, monitoring labels, daemon ID generation, and manager cephx key rotation status.

## Important APIs and Test Flow

`createNewCluster()` builds a fake `mgr.Cluster` with a mock Ceph executor, fake Kubernetes clientsets, a controller-runtime fake client containing a `CephCluster`, and a temporary config directory. The executor returns canned responses for `mgr stat`, `auth get-or-create-key`, `auth rotate`, and `versions`, while `waitForDeploymentToStart` is stubbed so tests focus on object reconciliation.

`TestStartMgr` calls `Start()` through several spec variants and validates expected deployments and services. `validateStart()` checks deployment annotations, labels, priority class, sidecar presence when `Mgr.Count > 1`, and absence of extra manager deployments. `validateServices()` verifies the metrics service and conditional dashboard service, including custom dashboard port handling.

`TestActiveMgrLabels` creates fake manager pods and verifies `SetMgrRoleLabel()` toggles `mgr_role` between `active` and `standby`. `TestUpdateServiceSelectors` verifies legacy selectors lose `ceph_daemon_id` and gain active-manager selection. `TestConfigureModules` covers generic mgr module enable/disable. `TestCluster_configurePrometheusModule` covers metrics-disabled behavior, metrics port changes, scrape interval comparison, and the disable-enable sequence needed for config changes. `TestMgrKeyRotation` validates key-generation status updates when the CephCluster daemon key-rotation policy advances.

## State, Dependencies, and Integration

The tests model state across Kubernetes Deployments, Services, Pods, fake `CephCluster.Status.Cephx.Mgr`, and command-output counters. They depend on Rook's fake operator clients, the Prometheus Operator API type for `ServiceMonitor`, Kubernetes policy/app/core APIs, and Ceph client command wrappers.

## Risks and Test Signals

The strongest signals are around upgrade-sensitive selectors and key generation. Risks include global test hooks (`updateDeploymentAndWait`, `waitForDeploymentToStart`) leaking if not reset, map-order-insensitive endpoint/service assertions, and mocked Ceph commands that may not catch argument changes outside the tested branches.
