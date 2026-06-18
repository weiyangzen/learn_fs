<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/exec.go -->
# sources/cloud-native/moby/api/types/container/exec.go

## Purpose
ExecCreateResponse is the response for a successful exec-create request.

## Important APIs, Types, And Functions
- Exported types: ExecCreateResponse, ExecInspectResponse, ExecProcessConfig.
- `ExecInspectResponse` fields include ID, Running, ExitCode, ProcessConfig, OpenStdin, OpenStderr, OpenStdout, CanRemove, ContainerID, DetachKeys, Pid.
- `ExecProcessConfig` fields include Tty, Entrypoint, Arguments, Privileged, User.
- Wire JSON fields include CanRemove, ContainerID, DetachKeys, ExitCode, ID, OpenStderr, OpenStdin, OpenStdout, Pid, Running, arguments, entrypoint, privileged, tty, user.
- Source comments highlight: ExecCreateResponse is the response for a successful exec-create request. ExecInspectResponse is the API response for the "GET /exec/{id}/json" endpoint and holds information about and exec. ExecProcessConfig holds information about the exec process running on the host.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `github.com/moby/moby/api/types/common`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/exec.go -->
