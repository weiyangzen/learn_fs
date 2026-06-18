# sources/distributed-fs/coda/coda-src/vtools/logprogress.in

## Purpose

`logprogress.in` is a Tcl/Tk/Tix meter for fetch progress messages from Venus.

## Important APIs, Types, and Functions

The script creates a label and `tixMeter`. `updatemeter()` reads mariner lines and matches `progress::fetching (<path>) <percent>x`, converting percent to a 0.0-1.0 meter value and updating the label.

## Control Flow

It connects to `localhost venus`, sends `set:fetch`, makes the socket nonblocking, registers a readable callback, and updates the meter when matching fetch progress lines arrive.

## State and Persistence Behavior

It stores only the last meter value in process memory. It does not write files or alter Coda state.

## Dependencies and Integration Points

It requires Tcl/Tk/Tix, the `venus` service, and Venus mariner fetch progress message format.

## Risks and Test Signals

The regex accepts arbitrary percent text and relies on `expr double(...)`. It exits on EOF with no reconnect. Tests should cover valid progress lines, nonmatching lines, percent bounds, unusual paths, and EOF handling.
