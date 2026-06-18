# sources/cloud-native/containerd/pkg/oci/spec_opts_windows_test.go

Purpose: Windows-specific tests for resources, networking flags, command-line generation, image config args, and default PATH.

Important APIs/types/functions: tests cover `WithWindowsCPUCount`, `WithWindowsIgnoreFlushesDuringBoot`, `WithWindowNetworksAllowUnqualifiedDNSQuery`, combinations of process args and image config entrypoint/cmd with Docker `ArgsEscaped`, `WithImageConfigArgsWindows`, `WithImageConfigArgsEscapedWindows`, and `WithDefaultPathEnv`.

Control flow: fake image configs are applied to Windows specs with or without user args, then assertions check whether `Process.Args` or `Process.CommandLine` is populated and escaped correctly.

State/persistence: in-memory fake image content only.

Dependencies/integration: Windows runtime-spec fields and shared fake image helpers.

Risks: escaping expectations are subtle and tightly coupled to Docker image config semantics. Tests are platform/build-tag specific.

Test signals: strong regression coverage for Windows command activation rules, especially interaction between image `Entrypoint`, `Cmd`, user args, and deprecated `ArgsEscaped`.
