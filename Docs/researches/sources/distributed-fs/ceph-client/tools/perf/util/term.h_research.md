# sources/distributed-fs/ceph-client/tools/perf/util/term.h

## Purpose

`term.h` declares the terminal helper API used by perf interactive display code.

## Important APIs, Types, and Functions

It forward-declares `struct termios` and `struct winsize`, then exports `get_term_dimensions()` and `set_term_quiet_input()`.

## Control Flow and State

There is no local state. The declarations expose functions that mutate caller-owned terminal structures and process terminal mode.

## Dependencies and Integration Points

The header intentionally avoids including termios headers, keeping include cost low for users in UI code.

## Risks and Test Signals

The API relies on callers passing valid storage and restoring terminal state after quiet mode. Build tests should ensure users include the platform headers that define the concrete structs where needed.
