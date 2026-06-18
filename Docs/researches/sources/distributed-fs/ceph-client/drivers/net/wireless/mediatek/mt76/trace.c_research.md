# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.c

## Purpose
Instantiates the generic mt76 tracepoints declared in `trace.h` and exports selected tracepoint symbols for use by mt76 modules.

## Important APIs, Types, And Functions
The file defines `CREATE_TRACE_POINTS`, includes `trace.h`, and exports `mac_txdone` and `dev_irq` tracepoint symbols with GPL visibility. It excludes sparse/checker builds through `#ifndef __CHECKER__`.

## Control Flow
No runtime control flow beyond tracepoint registration produced by the trace subsystem at compile/load time.

## State And Persistence
Tracepoint metadata is registered with the kernel tracing subsystem. No mt76 device state is stored here.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure, `trace.h`, module support, and consumers in mt76 code that call `trace_mac_txdone()`, `trace_dev_irq()`, `trace_reg_rr()`, or `trace_reg_wr()`.

## Risks
Only one C file may define `CREATE_TRACE_POINTS` for this trace header. Include path settings in the build must let `trace/define_trace.h` locate `trace.h`.

## Test Signals
Successful module build/load, visible mt76 trace events under ftrace/perf, and no duplicate tracepoint definition link errors.
