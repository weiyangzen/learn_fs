<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_attach.go -->
# sources/cloud-native/moby/client/container_attach.go

Purpose: implements attaching to a container’s stdio/log stream through an HTTP connection upgrade.

Important APIs/types/functions: `ContainerAttachOptions`, `ContainerAttachResult{HijackedResponse}`, and `Client.ContainerAttach`.

Control flow: validates container id, maps booleans and detach keys to query parameters (`stream`, `stdin`, `stdout`, `stderr`, `detachKeys`, `logs`), then calls `postHijacked` on `/containers/{id}/attach` with `Content-Type: text/plain`. It returns a `HijackedResponse`; the caller owns closing the connection.

State and integration behavior: no local persistence; it creates a long-lived network connection. Integrates with `hijack.go`, raw dialer selection in `client.go`, and Docker stream multiplexing conventions described in comments.

Risks and test signals: risks include leaked hijacked connections, incorrect query flags, and TTY vs multiplexed stream handling by callers. Dedicated attach tests are not in this subset, so coverage is indirect through hijack and exec attach tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_attach.go -->
