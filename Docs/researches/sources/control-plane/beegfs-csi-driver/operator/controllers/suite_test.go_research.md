<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go -->
# sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go

## Purpose
Bootstraps the envtest suite for controller integration tests.

## Important APIs, Types, And Functions
`TestAPIs` runs the Ginkgo suite. `BeforeSuite` starts envtest with CRDs from `../config/crd/bases`, registers the BeegfsDriver scheme, creates a controller-runtime manager, registers the reconciler, and starts the manager in a goroutine. `AfterSuite` cancels and stops envtest.

## Control Flow
The test process starts an API server/etcd, initializes client/manager, runs specs, then tears down after all tests.

## State And Persistence
All state is ephemeral envtest state. No real cluster resources persist.

## Dependencies And Integration Points
Uses controller-runtime envtest, client-go scheme, Ginkgo/Gomega, zap logging, and operator API registration.

## Risks And Edge Cases
Only CRD bases are loaded, so kustomize patches such as singleton name are absent. Manager startup is asynchronous and depends on shared global context.

## Test Signals
Provides the foundation for all controller integration tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/controllers/suite_test.go -->
