## sources/cloud-native/buildkit/session/sshforward/sshprovider/raw_provider.go

Purpose: implements the server side of the SSH forwarding gRPC service by mapping SSH IDs to dialers.

Important APIs/types/functions: `dialerFn` dials an agent connection. `socketProvider` holds `map[string]dialerFn`. `CheckAgent` verifies an ID exists and returns an empty response. `ForwardAgent` reads `buildkit.ssh.id` from incoming metadata, dials the selected agent, and bridges it to the gRPC stream with `sshforward.Copy`. `Register` registers the generated SSH server.

Control flow: both RPCs default empty IDs to `sshforward.DefaultID`. `ForwardAgent` validates metadata, fails fast on unknown ID, dials, defers close, then blocks until `Copy` completes.

State and persistence: provider state is the in-memory ID-to-dialer map. It does not mutate during requests.

Dependencies and integration points: registered via session `Attachable`; called by `sshforward.MountSSHSocket` client code. Relies on gRPC metadata for per-stream ID selection.

Risks and test signals: unknown IDs return a plain wrapped error, so callers rely on message text. Raw dialers may expose writable agent capabilities unless `agentprovider.go` wrapped them. `raw_provider_test.go` exercises unknown ID, check success, and bidirectional streaming.
