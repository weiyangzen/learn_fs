# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui.go

Purpose: Non-Windows GUI detection stub for CLI UI behavior.

Important APIs/types/functions: `InsideGUI() bool` always returns false on `!windows` builds.

Control flow, state, and persistence: No state and no side effects. The function is a platform split that lets shared code ask whether it likely runs from a GUI launcher.

Dependencies and integration points: No imports. The build tag excludes Windows so `ui_windows.go` supplies the Windows implementation.

Risks and test signals: Non-Windows platforms always report terminal-like behavior even when invoked from a graphical launcher. This is intentional but conservative. No direct tests are present; build-tag compilation is the relevant check.
