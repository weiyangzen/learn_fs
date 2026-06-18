# sources/distributed-fs/coda/coda-src/vtools/logcmls.in

## Purpose

`logcmls.in` is a Tcl/Tk/Tix strip-chart monitor for reintegration queue size. It visualizes active and inactive CML entries reported by Venus.

## Important APIs, Types, and Functions

It stores two 200-sample logs and draws stacked vertical bars on a canvas. `strip_draw()` rescales to the current maximum combined count. `updatestats()` handles nonblocking socket reads. `checkline()` parses `reintegrate::<volume>, <active>/<total>` and updates active, inactive, title, and label text.

## Control Flow

The script initializes the chart, connects to `localhost venus`, sends `set:fetch`, registers a readable callback, and repeatedly redraws.

## State and Persistence Behavior

State is in process-local Tcl variables only. It does not persist data or change Coda state.

## Dependencies and Integration Points

It depends on Tix, the `venus` socket service, and Venus mariner reintegration messages.

## Risks and Test Signals

Malformed numeric fields can break `expr`. The dynamic scale can make historical values visually jump. Disconnect exits instead of reconnecting. Tests should feed representative reintegration lines, zero totals, one-change labels, malformed lines, and EOF behavior.
