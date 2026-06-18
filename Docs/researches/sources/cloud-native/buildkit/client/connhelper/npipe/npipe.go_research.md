# sources/cloud-native/buildkit/client/connhelper/npipe/npipe.go

Purpose: registration shim for named-pipe connection support under `npipe://` URLs.

Important APIs/types/functions: package `init` registers scheme `npipe` with the platform-specific `Helper` function defined in build-tagged files.

Control flow: import side effect installs the helper during package initialization.

State and persistence: only shared registry mutation in `connhelper`.

Dependencies/integration points: shared `connhelper` registry and platform-specific implementations in `npipe_windows.go` or `npipe_other.go`.

Risks/test signals: behavior depends entirely on build tags. There are no direct tests in this subset; platform files define success/error behavior.
