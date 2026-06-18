# sources/control-plane/rook/pkg/util/exec/exec_pod.go

## Purpose
`exec_pod.go` executes commands in Kubernetes containers through the pod exec API and can copy local files into containers.

## Important APIs, Types, and Functions
`ExecOptions` describes command, namespace, pod, container, stdin, capture flags, and whitespace preservation. `RemotePodCommandExecutor` holds a Kubernetes clientset and REST config. `ExecWithOptions()` builds a pod exec request and streams via SPDY. `ExecCommandInContainerWithFullOutput()` finds the first pod with `app=<label>` and executes a command. `ExecCommandInContainerWithFullOutputWithTimeout()` prefixes commands with `timeout <seconds>`. `CopyLocalFileToContainer()` streams a local file to `cat - > dstPath` in the container.

## Control Flow, State, and Persistence
Exec streams are remote Kubernetes API calls. File copy reads a local file and writes remote container filesystem state. Output is trimmed unless `PreserveWhitespace` is true.

## Dependencies and Integration Points
It depends on client-go REST, pod exec parameter encoding, `remotecommand.NewSPDYExecutor`, Kubernetes pod listing, and shell availability in target containers. It supports Ceph commands from pods when the operator lacks direct network access.

## Risks
`CopyLocalFileToContainer()` interpolates `dstPath` into a shell command, so callers must not pass untrusted paths. The first matching pod is always chosen. Timeout behavior depends on the container having a `timeout` binary. SPDY exec requires RBAC and API server support.

## Test Signals
No direct mapped tests cover this file. Integration tests should cover no matching pod, stdout/stderr capture, whitespace preservation, timeout prefixing, RBAC failures, and file copy error reporting.
