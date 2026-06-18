# sources/distributed-fs/coda/coda-src/vcodacon/monitor.h

## Purpose
This header declares the `monitor` class used by the FLTK-based `vcodacon` visual console to watch the Coda console/mariner stream on the codacon port. It is a small UI-facing connection wrapper around an `Inet` endpoint with counters and display sizing state.

## Important APIs, Types, and Functions
`CODACONPORT` is fixed at `2430` and `LINESIZE` at `1024`. `monitor::Start()` establishes or starts monitoring the stream, `NextLine()` advances the display by one line, `ForceClose()` closes the active connection, and `AgeActColor()` decays activity highlighting. `SetBrowserSize(int)` only accepts sizes above ten. The global `NextLine(void)` exposes line advancement outside the class.

## Control Flow
The constructor initializes activity color, browser size, and counters for stores, reintegrations, and disconnected filesystem events. Runtime behavior is implemented elsewhere: callers create a monitor, start it, and drive line consumption through `NextLine`.

## State and Persistence Behavior
All state is transient UI state. The class keeps an `Inet conn`, active color, browser row count, and three event counters. It does not persist anything or mutate Coda state.

## Dependencies and Integration Points
It depends on `config.h` and `Inet.h` and integrates with the vcodacon GUI and the codacon network stream.

## Risks and Test Signals
Risks are connection lifecycle mismatches, stale UI counters, and hidden assumptions around the hard-coded port and line size. Test signals are successful connect/close cycles, line rendering under long messages, and activity color aging after store/reintegration/disconnected events.
