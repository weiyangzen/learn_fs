# sources/cloud-native/containerd/cmd/ctr/commands/commands_windows.go

Purpose: adds Windows-specific container resource/device flags and stubs runtime options.

Important APIs/functions: `init()` appends CPU count/shares/max and Windows device flags; `RuntimeOptions()` returns nil.

Control flow: Windows builds mutate shared `ContainerFlags` during init. Runtime option construction is currently delegated elsewhere or unsupported.

State and persistence: no persistence.

Dependencies/integration: selected on Windows; uses urfave/cli.

Risks: runtime-specific Windows options are not produced by `RuntimeOptions()`, so consumers expecting options must handle nil.

Test signals: no local tests.
