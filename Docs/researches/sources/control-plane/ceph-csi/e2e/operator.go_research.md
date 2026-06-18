# sources/control-plane/ceph-csi/e2e/operator.go

## Purpose
`operator.go` implements the e2e deployment-method adapter for Ceph-CSI when it is managed by the Ceph-CSI operator. It maps common RBD and CephFS deployment operations onto operator-created deployment and daemonset names and patches the operator config CR for cluster-name and topology-domain settings.

## Important APIs, Types, And Functions
`OperatorConfigName` is the fixed CR name `ceph-csi-operator-config`. `OperatorDeployment` embeds `DriverInfo`, so it satisfies the existing deployment method interfaces through shared methods plus operator-specific methods.

`NewRBDOperatorDeployment(c)` returns an `RBDDeploymentMethod` configured with operator RBD deployment/daemonset names and RBD container names. `NewCephFSOperatorDeployment(c)` returns a `CephFSDeploymentMethod` configured with operator CephFS names and the CephFS container.

`getPodSelector()` returns a selector matching Helm labels and operator deployment/daemonset names. `setClusterName(value)` patches `spec.driverSpecDefaults.clusterName` with a merge patch. `setDomainLabels(labels)` builds a JSON Patch adding `nodePlugin`, `topology`, and `domainLabels` under `spec.driverSpecDefaults`.

## Control Flow
Constructors populate `DriverInfo` with the clientset, expected controller deployment, nodeplugin daemonset, and driver container names. Runtime selection and readiness checks inherited from `DriverInfo` use `getPodSelector` to find Ceph-CSI pods across Helm-like labels and operator names. Configuration methods build kubectl patch argument lists and call `retryKubectlArgs` in the Ceph-CSI namespace with `deployTimeout`; errors are wrapped with operation-specific context.

## State, Persistence, And Dependencies
The Go object holds only client and naming metadata. Persistent state is modified in the Kubernetes API by patching the `operatorconfigs.csi.ceph.io` resource named by `OperatorConfigName`. Dependencies include local constants for operator and Helm names, deployment interfaces (`RBDDeploymentMethod`, `CephFSDeploymentMethod`), `DriverInfo`, `retryKubectlArgs`, `kubectlPatch`, `cephCSINamespace`, and standard JSON marshaling for JSON Patch serialization.

## Integration Points
This adapter lets existing deployment-agnostic e2e tests run against operator-managed Ceph-CSI. Topology and cluster-name tests can call the same interface methods regardless of whether the suite deployed via Helm/manifests or the operator, while this file translates those calls into operator config patches.

## Risks
`setDomainLabels` uses JSON Patch `add` operations for intermediate paths. If `nodePlugin` or `topology` already exists, Kubernetes JSON Patch may reject duplicate additions or replace behavior may not match test intent; a merge patch could be safer if repeated calls are expected. `getPodSelector` mixes Helm labels with operator names, so a broad selector could match stale pods during transitions. These helpers patch config but do not themselves wait for operator reconciliation; callers must restart or wait for affected CSI pods where needed.

## Test Signals
Tests should verify constructor interface compatibility, generated selectors for RBD and CephFS, successful merge patch JSON for cluster names, correct JSON Patch payload for domain labels, retry behavior on transient kubectl errors, and idempotency or expected failure behavior when `setDomainLabels` is called more than once against an existing config.
