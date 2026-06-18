# Research: sources/cloud-native/moby/daemon/libnetwork/error.go

Purpose: defines libnetwork-specific error types with marker methods used by containerd/libnetwork error classification. Important types are `ErrNoSuchNetwork`, `NetworkNameError`, `ActiveEndpointsError`, `ActiveContainerError`, and `ManagerRedirectError`.

Control flow: each type formats a user-facing error string and exposes marker methods such as `NotFound`, `Conflict`, `Forbidden`, or `Maskable`. These marker methods let shared error helpers classify errors without wrapping every return site in a common struct. `ActiveEndpointsError` joins active endpoint names in its message; `ActiveContainerError` reports endpoint name and ID; `ManagerRedirectError` tells callers to redirect manager-only requests.

State/dependencies: there is no persistent state. Dependencies are standard formatting and string joining. Integration points include endpoint/network delete paths and swarm manager redirection. Risks are mostly API compatibility: marker method changes would alter HTTP/API error classification. Tests verify selected marker interfaces using containerd errdefs and libnetwork `types.MaskableError`.
