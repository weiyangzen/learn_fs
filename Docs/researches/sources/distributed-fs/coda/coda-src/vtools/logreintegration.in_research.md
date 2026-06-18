# sources/distributed-fs/coda/coda-src/vtools/logreintegration.in

## Purpose

`logreintegration.in` is a Tcl/Tk/Tix progress meter for reintegration fragment upload progress.

## Important APIs, Types, and Functions

It creates a label and `tixMeter`. `updatemeter()` reads Venus mariner lines, matches `store::SendReintFragment ...(<offset>/<size>)`, maps offset to a fraction, treats `-1` as zero, and sets full completion when `store::CloseReintHandle` appears.

## Control Flow

The script connects to `localhost venus`, sends `set:fetch`, registers a nonblocking readable callback, and updates the meter on reintegration store messages.

## State and Persistence Behavior

Only current meter value is in memory. It has no durable persistence and does not mutate Coda state.

## Dependencies and Integration Points

It depends on Tcl/Tk/Tix, the `venus` service, and specific Venus mariner store/reintegration message strings.

## Risks and Test Signals

Division by zero is possible if message size is zero. The parser is tightly coupled to message text and exits on disconnect. Tests should cover normal fragments, offset `-1`, close handle completion, zero/malformed sizes, and nonmatching lines.
