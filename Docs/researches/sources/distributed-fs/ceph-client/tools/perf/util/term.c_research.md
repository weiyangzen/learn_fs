# sources/distributed-fs/ceph-client/tools/perf/util/term.c

## Purpose

`term.c` provides small terminal helpers for interactive perf UIs. It discovers terminal dimensions and switches stdin into quiet noncanonical mode for key polling.

## Important APIs, Types, and Functions

`get_term_dimensions(struct winsize *ws)` prefers `LINES` and `COLUMNS`, falls back to `ioctl(1, TIOCGWINSZ)`, then defaults to 25x80. `set_term_quiet_input(struct termios *old)` saves current stdin settings, clears `ICANON` and `ECHO`, sets `VMIN`/`VTIME` to zero, and applies the modified settings.

## Control Flow and State

The only persistent effect is terminal state changed by `tcsetattr`; callers must restore the saved `old` termios. The dimension helper mutates only the passed `winsize`.

## Dependencies and Integration Points

It depends on libc termios, environment variables, and optional `TIOCGWINSZ`. It is used by terminal and TUI-oriented commands such as `perf top`.

## Risks and Test Signals

Risks include leaving stdin noncanonical if callers fail to restore settings, environment variables with invalid zero values, and non-tty stdout. Tests can set `LINES`/`COLUMNS`, run under a pseudo-terminal, and verify fallback dimensions.
