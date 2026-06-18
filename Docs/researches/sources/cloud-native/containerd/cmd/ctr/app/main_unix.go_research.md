# sources/cloud-native/containerd/cmd/ctr/app/main_unix.go

Purpose: adds the `shim` command to `ctr` on non-Windows builds.

Important APIs/functions: `init()` appends `shim.Command` to `extraCmds`.

Control flow: package init runs before `app.New()`, so the shim command appears after the common command list.

State and persistence: mutates package-level `extraCmds`.

Dependencies/integration: selected by `!windows`; integrates `cmd/ctr/commands/shim`.

Risks: order depends on init-time append. Windows builds intentionally omit this command.

Test signals: no local tests.
