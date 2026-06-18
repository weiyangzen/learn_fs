# sources/cloud-native/buildkit/client/connhelper/npipe/npipe_other.go

Purpose: non-Windows implementation of the `npipe` helper that reports unsupported platform usage.

Important APIs/types/functions: build tag `!windows`; `Helper` returns nil helper and error `npipe connections are only supported on windows`.

Control flow: any non-Windows attempt to construct an npipe helper fails immediately.

State and persistence: none.

Dependencies/integration points: standard errors, URL type, and shared `ConnectionHelper`.

Risks/test signals: clear fail-fast behavior avoids silent unsupported connections. No direct tests in this subset.
