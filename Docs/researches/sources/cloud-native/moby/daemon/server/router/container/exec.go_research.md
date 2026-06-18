# sources/cloud-native/moby/daemon/server/router/container/exec.go

## Purpose
`exec.go` exposes HTTP endpoints for inspecting exec instances, creating an exec command in a container, starting it with optional stream hijacking, and resizing its TTY.

## Important APIs, Types, And Functions
Handlers are `getExecByID`, `postContainerExecCreate`, `postContainerExecStart`, and `postContainerExecResize`. `execCommandError` marks an empty command as invalid. Streaming uses `httputils.HijackConnection`, `stdcopymux.NewStdWriter`, and `stdcopy` stream IDs.

## Control Flow
Create parses JSON into `container.ExecCreateRequest`, rejects empty `Cmd`, strips `ConsoleSize` before API 1.42, and calls `ContainerExecCreate`. Start validates the exec ID with `ExecExists`, strips unsupported or non-TTY console sizing, hijacks the connection unless detached, writes an HTTP upgrade or raw stream response prelude, multiplexes stdout/stderr when no TTY is used, and calls `ContainerExecStart` with a background context. Resize parses `h` and `w` query values and delegates to `ContainerExecResize`.

## State And Persistence
Exec instances are registered and run by the backend/container state machinery. The router only wires streams and request options; it does not persist exec state.

## Dependencies And Integration Points
This file integrates container HTTP routes with backend exec lifecycle methods, API-version logic, hijacked HTTP connections, raw and multiplexed stream media types, and daemon logging.

## Risks
Hijack handling is sensitive: headers are manually written after hijack, errors after stream start are written to stdout, and `context.Background()` intentionally decouples exec execution from the HTTP request. Media type selection changed in API 1.42 and must stay compatible.

## Test Signals
Coverage is mostly integration-level through Docker exec API tests, including detached mode, TTY/non-TTY streaming, resize validation, and old API console-size behavior.
