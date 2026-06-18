# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_windows.go

Purpose: implements Windows kernel/version information retrieval.

Important APIs, types, and functions: Windows-specific `VersionInfo`, `String`, and `GetKernelVersion`.

Control flow: opens the Windows registry key for current version, reads `BuildLabEx` into `kvi`, then calls `windows.GetVersion` to populate major, minor, and build fields.

State and persistence: reads registry and OS version state; no mutation.

Dependencies and integration points: depends on `fmt`, `unsafe`, and `golang.org/x/sys/windows`. This file replaces the Unix `VersionInfo` shape under Windows.

Risks and edge cases: comments note executable manifest requirements for accurate `GetVersion` output. Registry access can fail and returns a partially populated `"Unknown"` value with error.

Test signals: no Windows tests in the requested set; behavior depends on platform registry/API integration.
