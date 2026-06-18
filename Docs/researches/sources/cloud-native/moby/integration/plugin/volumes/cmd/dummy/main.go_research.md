# sources/cloud-native/moby/integration/plugin/volumes/cmd/dummy/main.go

## Purpose
No-op volume plugin binary fixture. It provides a Docker plugin Unix socket process for tests that need to enable a volume-driver plugin with specific mount configuration.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock`, creates an empty HTTP mux, sets `ReadHeaderTimeout`, and serves indefinitely.

## Control Flow
The program panics on listen failure; otherwise it blocks in `server.Serve`.

## State And Persistence Behavior
No internal or persistent state.

## Dependencies And Integration Points
Built by volume helper `ensurePlugin` and wrapped by fixture metadata that declares volume-driver capability.

## Risks
Because it implements no volume-driver endpoints, it is only suitable for tests that validate plugin enable/configuration rather than volume operations.

## Test Signals
Indirectly verified by `TestPluginWithDevMounts`, which expects the daemon to enable the plugin successfully.
