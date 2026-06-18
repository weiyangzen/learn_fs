<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go -->
## sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go

### Purpose
`sanity_test.go` runs the Kubernetes CSI sanity test suite against a fake JuiceFS CSI driver served on a Unix socket.

### Important APIs, Types, And Functions
Constants define mount path, staging path, socket path, and CSI endpoint. `TestSanity` runs the Ginkgo suite. `BeforeSuite` creates `driver.NewFakeDriver(endpoint, newFakeJfsProvider())` and starts it. `AfterSuite` stops the driver and removes the socket. The `Describe` block builds `sanity.NewTestConfig` and calls `sanity.GinkgoTest`.

### Control Flow
Before the suite, the fake driver starts asynchronously and is expected not to error. The csi-test sanity suite connects to `unix:///tmp/csi.sock` and executes standard CSI conformance scenarios. After the suite, the driver stops and the socket file is removed.

### State, Persistence, And Dependencies
State includes a local Unix socket under `/tmp/csi.sock` and any temporary mount/stage directories used by the driver/sanity tests. Dependencies include Ginkgo, Gomega, `kubernetes-csi/csi-test`, and the fake provider.

### Integration Points
This is a standardized CSI API compatibility gate for the JuiceFS driver. It exercises driver methods through gRPC rather than direct package calls.

### Risks
The driver starts in a goroutine without explicit readiness wait beyond sanity connection behavior. Fixed `/tmp` paths can collide with concurrent runs. Fake provider behavior limits coverage of real mount/backend failures.

### Test Signals
Passing csi-test sanity cases signals basic CSI RPC contract compliance for identity, controller, and node paths supported by the fake driver. Failures indicate API-level regressions independent of real storage.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go -->
