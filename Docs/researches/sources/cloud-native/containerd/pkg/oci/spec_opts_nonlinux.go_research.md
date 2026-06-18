# sources/cloud-native/containerd/pkg/oci/spec_opts_nonlinux.go

Purpose: non-Linux stubs for Linux capability propagation options.

Important APIs/types/functions: `WithAllCurrentCapabilities` and `WithAllKnownCapabilities` both delegate to `WithCapabilities(defaultUnixCaps())`.

Control flow: no host capability inspection occurs; the default Unix capability list is applied to the spec.

State/persistence: generated spec only.

Dependencies/integration: selected on non-Linux platforms to preserve `SpecOpts` API compatibility without libcap/Linux syscalls.

Risks: semantics differ from Linux because current process capabilities are not inspected. Callers that expect host cap reflection should account for platform behavior.

Test signals: compile-time coverage and general capability tests on non-Linux should confirm defaults are applied without platform syscalls.
