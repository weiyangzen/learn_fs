# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.c

## Purpose
`trace.c` instantiates wil6210 tracepoints declared in `trace.h`. It is the single translation unit that defines `CREATE_TRACE_POINTS` for this driver.

## Important APIs, Types, And Functions
The file includes `<linux/module.h>`, defines `CREATE_TRACE_POINTS`, and includes `trace.h`. It does not define functions directly; the tracepoint machinery expands declarations from the header.

## Control Flow
There is no driver runtime control flow in this file. Build-time macro expansion creates the tracepoint definitions when tracing is enabled.

## State And Persistence
Tracepoint registration state is managed by the Linux tracing subsystem. No wil6210 runtime state is stored here.

## Dependencies And Integration Points
It depends on `trace.h` and kernel tracepoint infrastructure. Other driver files call `trace_wil6210_*()` helpers generated or stubbed by `trace.h`.

## Risks
There must be exactly one `CREATE_TRACE_POINTS` instantiation for the header. Moving this include pattern or including `trace.h` with the macro elsewhere can cause duplicate definitions.

## Test Signals
Build with `CONFIG_WIL6210_TRACING=y` and disabled. At runtime, verify wil6210 events appear in ftrace/perf only when tracing support is enabled.
