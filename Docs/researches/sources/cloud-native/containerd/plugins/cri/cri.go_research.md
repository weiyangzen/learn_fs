<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri.go -->
# sources/cloud-native/containerd/plugins/cri/cri.go

## Purpose
Registers and initializes the top-level Kubernetes CRI gRPC plugin by wiring runtime/image services, sandbox controllers, NRI, streaming config, warnings, and containerd in-memory services.

## Important APIs, Types, And Functions
init registration, initCRIService, imageService and initializer interfaces, criGRPCServer, criGRPCServerWithTCP, getNRIAPI, getSandboxControllers, and configMigration.

## Control Flow
Init loads runtime and image CRI service dependencies, propagates runtime-specific snapshotters to image service, validates config and emits warnings, creates an in-memory containerd client, collects sandbox controllers, builds server.CRIServiceOptions, starts the CRI service readiness goroutine, and returns a gRPC registrar with optional TCP registration.

## State And Persistence
Long-running CRI service state is owned by server.NewCRIService and its Run loop. Config migration mutates pluginConfigs maps during daemon startup.

## Dependencies And Integration Points
Depends on containerd client, plugin registry, internal CRI config/server/images/instrument packages, sandbox/NRI plugins, warning service, grpc, Kubernetes CRI API, and platform defaults.

## Risks And Edge Cases
Startup is dependency-heavy; missing runtime/image services or bad config abort plugin init. NRI type mismatch disables NRI. DisableTCPService changes returned interface capabilities. Migration preserves only selected streaming/TCP fields from old grpc.cri config.

## Test Signals
cri_test.go covers configMigration field retention/removal. Broader CRI behavior is tested in internal CRI packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri.go -->
