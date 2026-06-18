# sources/control-plane/external-snapshotter/cmd/csi-snapshotter/main.go

## Purpose
Main entrypoint for the CSI external-snapshotter sidecar that talks to a CSI driver and reconciles VolumeSnapshotContent operations.

Source size: 376 lines, 14754 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Functions/methods: `main`, `buildConfig`, `supportsControllerCreateSnapshot`, `supportsGroupControllerCreateVolumeGroupSnapshot`.
- Key imports: `context`, `flag`, `fmt`, `net/http`, `os`, `os/signal`, `strings`, `sync`, `time`, `google.golang.org/grpc`, `k8s.io/apimachinery/pkg/apis/meta/v1`, `k8s.io/apimachinery/pkg/labels`, ...

## Control Flow
- Parses feature gates, logging, common CSI sidecar flags, retry, metrics, leader election, and node-deployment options.
- Builds Kubernetes and snapshot clientsets, shared informer factories, optional node-local content filtering, and event schemes.
- Connects to the CSI endpoint, discovers driver name, probes readiness, verifies snapshot capability, optionally checks group snapshot capability, then constructs sidecar controllers.
- Starts metrics/health endpoints, leader election or direct controller loops, informer factories, and worker queues until shutdown.

## State and Persistence
- Maintains process-local clients, gRPC connection, metrics manager, informer caches, workqueues, and controller goroutines.
- Persists desired/observed snapshot state through Kubernetes snapshot CRs and CSI driver calls.
- Node deployment mode filters content by the managed-by label derived from `NODE_NAME`.

## Dependencies and Integration Points
- CSI protobuf/gRPC APIs, csi-lib-utils config/connection/rpc/metrics/leader election, Kubernetes client-go, generated snapshot client/informers, sidecar controller, snapshotter, group snapshotter.

## Risks and Edge Cases
- Requires a reachable CSI endpoint and driver support for create/delete snapshot or exits.
- Leader election conflicts with node-deployment mode by design.
- Feature gate and driver capability mismatches can leave group snapshot functionality disabled or warning-only.

## Test Signals
- Companion `main_test.go` covers capability probing helper behavior with mock CSI responses.
- Integration coverage requires a Kubernetes cluster and CSI driver.
