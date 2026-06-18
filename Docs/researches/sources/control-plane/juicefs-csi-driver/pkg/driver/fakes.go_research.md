# sources/control-plane/juicefs-csi-driver/pkg/driver/fakes.go

Purpose: builds an in-memory fake `Driver` for tests that need controller and node services without real Kubernetes, real mounts, or real JuiceFS.

Important APIs and functions: `NewFakeDriver(endpoint, fakeProvider)` constructs a `Driver` with a fake endpoint, fake controller service, and fake node service. The fake controller uses the supplied `juicefs.Interface`, an empty `vols` map, and a quota dispatch pool. The fake node service uses a fake Kubernetes clientset, fake mount table containing `/tmp/csi-mount/target`, a fake exec runner, metrics, unmounted-path tracking, and test-local volume locks.

Control flow: the helper creates Prometheus metrics, builds a `mount.SafeFormatAndMount` with `mount.NewFakeMounter`, and returns a partially populated driver. It does not construct a provisioner service or gRPC server.

State and persistence behavior: all state is process-local and test-scoped: fake mount entries, maps, sync maps, metrics, and locks. No filesystem or Kubernetes API writes occur.

Dependencies and integration points: integrates test code with `juicefs.Interface`, fake client-go, Kubernetes mount fake utilities, `testingexec.FakeExec`, `util.NewPrometheus`, `dispatch.Pool`, and `resource.VolumeLocks`.

Risks and test signals: useful for isolating CSI method tests, but it does not mirror all production fields, especially provisioner service and shared volume locks. Metrics registration can conflict if reused with duplicate metric names under the same registerer.
