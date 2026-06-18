# sources/distributed-fs/beegfs-go/ctl/internal/util/terminal.go

Purpose: provides terminal refresh and alert helpers for watch-like command output.

Important APIs/types/functions: `TermRefresher`; `StartRefresh`; `FinishRefresh`; `WithTermFooter`; `WithCancelRefresh`; `TerminalAlert`.

Control flow: `StartRefresh` records terminal dimensions, creates a pipe, saves `os.Stdout`, and redirects stdout to the pipe. `FinishRefresh` closes and reads the pipe, restores stdout, optionally clears the terminal, prints buffered output, and draws a colored footer at the bottom. `TerminalAlert` emits a bell.

State and persistence: temporarily mutates global `os.Stdout`; no persistence. The caller must call `FinishRefresh` after successful `StartRefresh`.

Dependencies and integration points: uses `golang.org/x/term` for terminal size and ANSI control sequences for clearing and footer coloring. Intended for commands that repeatedly refresh printed output.

Risks: global stdout redirection is process-wide and not safe with concurrent writers. Errors between `StartRefresh` and `FinishRefresh` can leave stdout redirected if callers do not defer cleanup. Footer width uses `len`, not display width. It requires stdout to be a terminal.

Test signals: no direct tests. Useful tests would require an isolated pseudo-terminal or abstraction for stdout/term size.
