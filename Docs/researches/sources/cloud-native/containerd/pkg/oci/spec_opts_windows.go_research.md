# sources/cloud-native/containerd/pkg/oci/spec_opts_windows.go

Purpose: Windows-specific spec option helpers and stubs for Linux-only device behavior.

Important APIs/types/functions: `escapeAndCombineArgs` uses `windows.EscapeArg` for command-line construction. `WithProcessCommandLine` sets `s.Process.CommandLine` and clears args. `WithHostDevices` is a no-op, `DeviceFromPath` returns not implemented, and `WithDevices` is a no-op. `WithDefaultPathEnv` sets Windows PATH to `c:\Windows\System32;c:\Windows`.

Control flow: Windows command-line option initializes process state before mutation. Default PATH delegates to shared env merge logic. Linux device APIs remain callable but intentionally do nothing or return not implemented.

State/persistence: generated spec only.

Dependencies/integration: selected on Windows; uses `github.com/Microsoft/go-winio/pkg/guid` for not-implemented error construction and `golang.org/x/sys/windows` escaping.

Risks: Windows command-line escaping must match HCS/runtime expectations. No-op host devices can hide caller assumptions from cross-platform code.

Test signals: `spec_opts_windows_test.go` exercises command-line/image arg escaping and Windows resource/default PATH options.
