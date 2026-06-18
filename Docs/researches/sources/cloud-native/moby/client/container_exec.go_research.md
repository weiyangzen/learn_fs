<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec.go -->
# sources/cloud-native/moby/client/container_exec.go

Purpose: implements Docker exec lifecycle client methods: create, start, attach, resize validation support, and inspect.

Important APIs/types/functions: `ExecCreateOptions/Result`, `ConsoleSize`, `ExecStartOptions/Result`, `ExecAttachOptions/Result`, `getConsoleSize`, `ExecInspectOptions`, `ExecInspectResult`, `Client.ExecCreate`, `Client.ExecStart`, `Client.ExecAttach`, and `Client.ExecInspect`.

Control flow: `ExecCreate` validates container id, validates console size only when TTY is true, maps options into `container.ExecCreateRequest`, posts to `/containers/{id}/exec`, and decodes the exec ID. `ExecStart` posts `container.ExecStartRequest` to `/exec/{id}/start` and closes the response. `ExecAttach` uses the same start endpoint through `postHijacked` and returns a hijacked connection. `ExecInspect` GETs `/exec/{id}/json`, decodes `container.ExecInspectResponse`, and flattens a nil `ExitCode` pointer to zero.

State and integration behavior: no local persistence; daemon creates and controls exec process state. Hijacked attach transfers connection ownership to the caller.

Dependencies: container API types, containerd errdefs, shared request/hijack helpers, and HTTP headers.

Risks and test signals: risks include allowing console size without TTY, losing nil exit-code semantics, leaked hijack connections, and route confusion between start and attach. `container_exec_test.go` covers errors, connection failures, create/start/attach/inspect routes and console-size validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec.go -->
