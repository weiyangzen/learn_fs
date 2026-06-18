<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go

## Purpose
This file tests the NVMe-oF gateway controller's high-level reconcile behavior, CephX key rotation status, and generated gateway configuration.

## Important APIs and control flow
`TestCephNVMeOFGatewayController` builds fake clients, mock executors, and version stubs to exercise no-cluster/not-ready requeues, invalid specs, one gateway, repeated reconcile, three gateways, scale-down to two and one, and two independent gateway CRs. `TestNVMeOFKeyRotation` verifies initial CephX status, retention on subsequent reconcile, brownfield unknown status behavior, key-generation-driven status changes, and no unnecessary repeat rotation. `TestNVMeOFConfigGeneration` validates default INI values and user overrides/new sections. `TestNVMeOFConfigMapGeneration` verifies ConfigMap name, namespace, config key, placeholder pod IP, group, port override, and pool fields.

## State and persistence
Tests use fake Kubernetes clientsets for Services/Deployments/ConfigMaps and fake controller clients for CR/status state. Ceph status, config image lookup, and NVMe gateway commands are mocked.

## Dependencies and integration points
The tests depend on Rook fake clientsets, controller-runtime fake clients, fake event recorders, Ceph version stubs, INI parsing, and mock executors. They validate integration among controller reconciliation, spec generation, config generation, and status reporting.

## Risks and test signals
The tests do not execute the embedded shell script or validate actual Ceph-side NVMe gateway registration. They are strong signals for resource naming, scaling, spec validation, generated INI content, and CephX status transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/controller_test.go -->
