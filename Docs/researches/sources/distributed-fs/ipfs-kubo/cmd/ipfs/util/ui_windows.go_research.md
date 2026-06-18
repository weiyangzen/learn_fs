# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/ui_windows.go

Purpose: Windows-specific heuristic for determining whether the process was launched without an interactive terminal.

Important APIs/types/functions: `InsideGUI()` calls `windows.GetConsoleScreenBufferInfo(windows.Stdout, ...)` and returns true when the console cursor position is still `(0,0)`.

Control flow, state, and persistence: The function allocates a `ConsoleScreenBufferInfo`, queries stdout, returns false on API error, and otherwise treats an untouched cursor as a high-probability GUI launch. It has no persistent state.

Dependencies and integration points: Uses `golang.org/x/sys/windows`; pairs with `ui.go` for non-Windows builds. Callers can suppress terminal-oriented prompts or output behavior when it returns true.

Risks and test signals: The cursor-position heuristic can produce false positives if a terminal has not moved the cursor before Kubo starts, and false negatives if GUI launchers attach a console. No direct tests in this subset; behavior depends on Windows console API semantics.
