# sources/cloud-native/moby/integration/internal/container/container.go

Purpose: shared test helper package for creating, running, attaching to, inspecting, removing, and reading output from containers in integration tests.

Important APIs and types: `TestContainerConfig`, `NewTestConfig`, `Create`, `CreateFromConfig`, `Run`, `RunResult`, `RunAttach`, `demultiplexStreams`, `Remove`, `RemoveAll`, `Inspect`, `ContainerOutput`, and `Output`.

Control flow: `NewTestConfig` builds a busybox default command (`top` on Linux, `sleep 240` on Windows) and applies functional options. `Create` and `Run` wrap `ContainerCreate`/`ContainerStart` with assertions. `RunAttach` enables stdout/stderr attach, starts the container, demultiplexes streams until EOF or context cancellation, then inspects with a fresh background context for exit code. `demultiplexStreams` copies Docker multiplexed output in a goroutine, closes the hijacked response on completion/cancel, and waits for the copy goroutine. Removal/list/inspect/output helpers wrap common API calls.

State and persistence: creates real containers and reads logs/inspect state. The helper itself stores only transient buffers and config structs.

Dependencies and integration: depends on Moby client API, container/network types, OCI platform, `stdcopy`, test assertions, runtime GOOS, and functional options from `ops.go`.

Risks: `RunAttach` uses context cancellation to stop stream reads but always inspects with `context.Background`, so hung daemon inspect could still block. Helpers assert fatally, making them convenient but unsuitable for tests that need error inspection.

Test signals: helper code; its reliability affects many integration tests by standardizing container setup, cleanup, and output capture.
