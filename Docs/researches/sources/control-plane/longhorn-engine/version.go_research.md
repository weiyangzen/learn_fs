## sources/control-plane/longhorn-engine/version.go

### Purpose
`version.go` implements the Longhorn engine CLI `version` command.

### Important APIs, Types, And Functions
`VersionCmd` returns a `cli.Command` named `version` with a `--client-only` flag. `VersionOutput` contains `ClientVersion` and optional `ServerVersion` fields. `version` obtains local build metadata from `meta.GetVersion`, optionally connects to the controller using global `url`, `volume-name`, and `engine-instance-name`, fetches server version detail, and prints indented JSON.

### Control Flow
The command action calls `version` and logs fatally on error. When `client-only` is false, it creates a controller client, defers close with logging, calls `VersionDetailGet`, and includes the result. JSON marshal failure is returned.

### State, Persistence, And Dependencies
It reads build metadata and remote controller state but writes only stdout. Dependencies are `urfave/cli`, `encoding/json`, logrus, controller client, and `meta`.

### Integration Points
This CLI command helps users compare client binary version with running engine controller version.

### Risks
Without `--client-only`, the command depends on a reachable controller and correct global flags. Fatal logging exits the process from the action wrapper.

### Test Signals
Tests should cover client-only JSON output, remote server version inclusion with a fake controller client, and error propagation for connection/version failures.
