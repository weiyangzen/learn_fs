<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go

## Purpose
`deploy.go` embeds base Kubernetes manifests and exposes typed accessors so Go code, especially the operator, can instantiate the same objects used by Kustomize deployments.

## Important APIs, Types, and Functions
`//go:embed` captures controller, CSIDriver, node, and RBAC YAML. Constants define expected container names, resource names, and keys: `beegfs`, `node-driver-registrar`, `csi-provisioner`, `csi-resizer`, `liveness-probe`, `csi-beegfs-config`, `csi-beegfs-connauth`, `csi-beegfs-tlscerts`, and their file keys. Accessors are `GetRBAC()`, `GetControllerServiceStatefulSet()`, `GetCSIDriver()`, and `GetNodeServiceDaemonSet()`.

## Control Flow
`GetRBAC()` splits the multi-document RBAC manifest on `---`, detects object kind by byte containment, strictly unmarshals each document into the corresponding Kubernetes API type, and returns a slice of interfaces. Other accessors strictly unmarshal single YAML documents into typed objects.

## State and Persistence
Embedded YAML bytes are compile-time state in the binary. The functions allocate typed Kubernetes objects but do not persist them; callers decide whether to create/update objects in a cluster.

## Dependencies and Integration Points
The package depends on Go embed, Kubernetes API packages, `sigs.k8s.io/yaml`, and `github.com/pkg/errors`. Operator logic relies on the exported constants and accessors to avoid separately maintaining deployment manifests.

## Risks
Kind detection by substring is simple and can be confused if comments or unexpected documents include matching text. Splitting on raw `---` assumes no document content uses that sequence. Strict unmarshal is good for drift detection but can break builds when Kubernetes API versions change fields. Constant names are intentionally coupled to operator logic.

## Test Signals
`deploy_test.go` verifies RBAC object typing, manifest unmarshalling, expected containers, expected key args, and expected volume resource names. Additional signals include operator reconciliation tests and CI generated-manifest diff checks.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy.go -->
