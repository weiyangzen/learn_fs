# sources/distributed-fs/coda/coda-src/vcodacon/monitor.cc

## Purpose
Implements the `vcodacon` monitor that connects to Coda mariner/codacon output and updates FLTK widgets for connection, activity, cache walks, fetch progress, stores, reintegration, attribute fetches, and conflicts.

## Important APIs, Types, And Functions
Static FLTK callbacks are `GetNextLine`, `ConnExcept`, `TryAgain`, `AgeColor`, `ClearVattr`, and `ClearXfer`. `monitor` methods are `Start`, `NextLine`, `ForceClose`, and `AgeActColor`. Global generated widgets from `vcodacon.h` are updated directly.

## Control Flow
`Start()` initializes the singleton monitor pointer, reads `marinersocket` from `venus.conf`, tries a Unix socket then localhost `CODACONPORT`, registers fd read/exception callbacks, sets connection/activity colors, switches line mode to Unix, and sends `set:fetch`. `NextLine()` reads one line, appends most lines to the browser with bounded history, ages activity color, parses known substrings, and updates progress bars and status widgets. Connection loss or exception closes the fd, marks red, and schedules reconnect. Timeouts clear transient colors/progress bars.

## State And Persistence
State is GUI/runtime only: `TheMon`, `Vattrnum`, progress labels, monitor counters, current activity color, browser size, and socket connection state. No persistent data is written.

## Dependencies And Integration Points
Depends on `Inet`, `codaconf`, FLTK event loop/widgets, generated `vcodacon.h`, and `util.h` for `XferLabel`. It integrates the Coda client mariner event stream with a visual status dashboard.

## Risks
Parsing is substring-based and mutates input strings after locating parentheses/percent signs without validating all pointers, so malformed progress lines can crash. `ForceClose()` calls `Start()` immediately after close, while other paths schedule delayed reconnects. Static singleton design prevents multiple independent monitors. Progress label memory is managed manually.

## Test Signals
Feed representative mariner lines for fetch progress, cache begin/end, shutdown, store/reintegration begin/end, attr fetches, conflicts, malformed progress lines, connection close, and repeated reconnects. Verify FLTK fd/timeout registration, browser trimming, progress-bar reuse, and color aging.
