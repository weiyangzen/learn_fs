# sources/cloud-native/containerd/cmd/containerd/command/service_unsupported.go

Purpose: provides non-Windows stubs for Windows service integration hooks.

Important APIs/functions: `serviceFlags()`, `applyPlatformFlags()`, `registerUnregisterService()`, and `launchService()` are no-ops on `!windows`.

Control flow: daemon startup can call service hooks unconditionally; on non-Windows no flags are added and no early stop or service launch occurs.

State and persistence: none.

Dependencies/integration: selected by `!windows`; references server type and cli package for signature compatibility.

Risks: none beyond platform-specific feature absence.

Test signals: no local tests; stub behavior is trivial.
