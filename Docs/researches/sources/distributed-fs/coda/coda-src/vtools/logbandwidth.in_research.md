# sources/distributed-fs/coda/coda-src/vtools/logbandwidth.in

## Purpose

`logbandwidth.in` is a Tcl/Tk/Tix strip-chart monitor for Venus connection bandwidth messages.

## Important APIs, Types, and Functions

It maintains three rolling 200-sample lists, a canvas, and label state. `strip_draw()` logs current values, draws logarithmic vertical bars for three bandwidth measures, labels modem/ISDN/Wavelan/Ethernet/Fast Ethernet scale lines, and reschedules itself. `updatestats()` reads mariner socket lines. `checkline()` matches `connection::bandwidth` messages for an optional peer filter and updates graph values plus bit-per-second label.

## Control Flow

The script creates UI elements, connects to `localhost venus`, sends `set:fetch`, configures nonblocking reads with `fileevent`, and starts periodic drawing every 100 ms.

## State and Persistence Behavior

All state is in Tcl globals. No files are written. It consumes live Venus mariner messages and renders transient UI history.

## Dependencies and Integration Points

It requires `+TIXWISH+`, Tcl/Tk/Tix, a resolvable `venus` service, and mariner `set:fetch` bandwidth events.

## Risks and Test Signals

The graph uses `log10()` and clamps values below 100, hiding low-rate detail. Socket disconnect exits immediately. Parsing is based on positional `lindex` fields. Tests can feed mock lines into `checkline`, verify clamping and label math, and simulate EOF handling.
