# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/trace.h

## Purpose
Declares generic mt76 tracepoints for register reads/writes, IRQ status, and TX completion identifiers. These are low-overhead instrumentation hooks used across mt76 bus and chip code.

## Important APIs, Types, And Functions
Defines event classes `dev_reg_evt` and `dev_txid_evt`, concrete events `reg_rr`, `reg_wr`, `dev_irq`, and `mac_txdone`, and shared formatting macros for wiphy name, register/value pairs, and WCID/packet id pairs.

## Control Flow
No driver control flow. The trace macros generate tracepoint call sites and record assignments when a tracepoint is enabled. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct `define_trace.h` to this header.

## State And Persistence
Trace records persist only in the kernel tracing buffers. Each record carries the wiphy name plus event-specific register, value, mask, WCID, or packet id fields.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure and `mt76.h` for `struct mt76_dev`. It is used by generic mt76 code and bus/datapath code to diagnose register access, interrupts, and TX status.

## Risks
Trace event field layout is user-visible to tracing tools. Renaming events or changing field meanings can break diagnostics. The fixed 32-byte wiphy name buffer truncates longer names by design.

## Test Signals
Events appear under `/sys/kernel/tracing/events/mt76`, can be enabled individually, and show correct wiphy/register/IRQ/TX id data during traffic and interrupt handling.
