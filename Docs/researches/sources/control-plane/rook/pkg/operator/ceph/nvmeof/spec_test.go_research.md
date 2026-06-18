# sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec_test.go

## Purpose
`spec_test.go` is the deployment and service specification regression suite for the Ceph NVMe-oF gateway controller. It validates the Kubernetes objects produced by `ReconcileCephNVMeOFGateway.makeDeployment()` and `generateCephNVMeOFService()` without needing a live cluster or Ceph daemon. The tests protect the operator contract for pod labels, resources, service account, liveness probes, placement, host networking, ConfigMap references, init container setup, daemon container setup, image fallback, hostnames, and gateway ports.

## Important APIs, Types, and Functions
`newDeploymentSpecTest()` builds a fake controller-runtime client seeded with a `CephNVMeOFGateway`, a fake Kubernetes clientset, a mock executor, `ClusterInfo`, and a minimal `ClusterSpec`. `TestDeploymentSpec()` contains subtests for each supported deployment variant. Local helpers `assertEnvVar`, `assertEnvVarPresent`, `assertServicePort`, and `assertContainerPort` make targeted assertions against Kubernetes `EnvVar`, `ServicePort`, and `ContainerPort` slices. The test code exercises constants and functions defined in the production package, including `AppName`, `serviceAccountName`, `connectionConfigScript`, `instanceName`, `nvmeofIOPort`, `nvmeofGatewayPort`, `nvmeofMonitorPort`, and `nvmeofDiscoveryPort`.

## Control Flow, State, and Persistence
The suite constructs CR instances, invokes spec-generation functions, and inspects returned Kubernetes API objects in memory. There is no persistent cluster state, but the test verifies fields that become persisted cluster state when the controller applies them: Deployment annotations include the config hash, pod templates carry resource requests/limits and placement constraints, volumes reference the selected ConfigMap, services expose gateway ports, and host-network deployments use `DNSClusterFirstWithHostNet`. The image fallback test injects a mock executor result so `makeDeployment()` can discover an image from Ceph config when the CR omits one.

## Dependencies and Integration Points
The file depends on Rook's Ceph API types, fake Rook/client-go clients, controller-runtime fake clients, operator test helpers, mock exec, Ceph version metadata, and Kubernetes core API types. It integrates with the NVMe-oF reconciler's deployment/service builders and with shared Ceph label validation through `cephTest.AssertLabelsContainCephRequirements()`. `optest.NewPodTemplateSpecTester()` validates common pod-template conventions shared across Rook daemons.

## Risks
The tests are strong for object shape but do not validate Kubernetes admission behavior or runtime gateway readiness. Assertions depend on exact container names, port names, and generated labels, so intentional production renames need coordinated test updates. The image fallback mock only returns a happy-path string or empty value; it does not cover command errors or malformed image data. The invalid-hostname case only checks an underscore-based name and may not cover all Kubernetes hostname edge cases.

## Test Signals
Positive signals include coverage for default and custom liveness probes, default topology spread constraints, user placement override, host network behavior, custom ConfigMap refs, init container env/volume wiring, privileged daemon container setup, image fallback and failure, valid/invalid hostnames, service labels, and custom ports. Useful follow-up signals would include tests for executor error propagation in image discovery and any future TLS or multi-instance service behavior.
