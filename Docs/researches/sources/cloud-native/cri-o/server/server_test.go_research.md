# sources/cloud-native/cri-o/server/server_test.go

## Purpose
Ginkgo/Gomega tests for high-level `server.New`, exit monitoring, shutdown, and stream server stopping behavior.

## Important APIs, Types, And Functions
Defines the `Server` spec under the shared `t.Describe` wrapper. Exercises `server.New`, `StartExitMonitor`, `Shutdown`, and `StopStreamServer` through mocks from the suite fixture.

## Control Flow
Each test resets the common mock/config fixture. Successful `New` cases cover default config, UID/GID mappings, TLS stream configuration, container restoration from storage metadata, valid stream idle timeout, and disabled hostport mapping. Failure cases pass nil config, invalid directory paths, malformed UID/GID mappings, invalid stream address/port, invalid TLS certificate paths, and invalid idle timeout. Runtime behavior tests start the exit monitor goroutine and signal its close channel, verify shutdown calls storage shutdown and creates the clean shutdown file, and stop the stream server.

## State And Persistence
Creates temp graph roots and test directories through the shared suite, writes the clean shutdown marker during `Shutdown`, and relies on mocked storage metadata for restoration state.

## Dependencies And Integration Points
Uses GoMock expectations for config/storage/CNI, `go.podman.io/storage` containers, CRI-O config, and the server package.

## Risks And Test Signals
Strong signal for constructor error handling and restoration sequencing. It does not validate the internal restored container contents, stream data paths, or seccomp watcher behavior. The duplicated "valid config path" test is equivalent to the default success case.
