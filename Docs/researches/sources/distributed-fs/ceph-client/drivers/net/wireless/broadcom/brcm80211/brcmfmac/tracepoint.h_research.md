# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/tracepoint.h

## Purpose
`tracepoint.h` defines the `brcmfmac` trace events used for errors, debug messages, hexdumps, BCDC headers, and SDPCM headers. It also supplies no-op inline stubs when tracing is disabled so callers can use trace functions unconditionally.

## Important APIs, types, and functions
- Fallback macro overrides for `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` create inline no-op `trace_*` functions when `CONFIG_BRCM_TRACING` is not enabled.
- `TRACE_SYSTEM brcmfmac` names the trace subsystem.
- `TRACE_EVENT(brcmf_err)` records function name and formatted error message from `struct va_format`.
- `TRACE_EVENT(brcmf_dbg)` records debug level, function name, and formatted message.
- `TRACE_EVENT(brcmf_hexdump)` records a data address, length, and dynamic byte array.
- `TRACE_EVENT(brcmf_bcdchdr)` extracts BCDC flags, priority, flags2, signal length, and dynamic signal bytes.
- `TRACE_EVENT(brcmf_sdpcm_hdr)` records SDPCM direction, length, sequence number, and a 12- or 20-byte header snapshot.
- When tracing is enabled, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` integrate with the kernel trace generation system.

## Control flow
At compile time, tracing-enabled builds generate tracepoint code from these macros, with `tracepoint.c` acting as the definition site. Tracing-disabled builds replace trace calls with inline no-ops. Runtime trace calls copy relevant fields or dynamic arrays into trace buffers and format compact `TP_printk()` summaries for consumers.

## State and persistence behavior
The header defines static trace metadata and per-event trace records. It does not own driver runtime state. Event payloads copy data from caller-provided pointers at trace time.

## Dependencies and integration points
The file depends on Linux tracepoint infrastructure and `struct va_format`. It is used by debug/error helpers, BCDC protocol code, and SDIO SDPCM framing code. The SDPCM direction fallback macros keep this header independent enough to compile even if direction constants are not already defined.

## Risks and edge cases
- Trace events that copy dynamic data trust caller-provided lengths and pointer validity at trace-call time.
- `brcmf_bcdchdr` derives dynamic array length from byte 3 of the header; malformed or too-short input would be a caller bug.
- `brcmf_sdpcm_hdr` copies 20 bytes for glom headers and 12 bytes otherwise; callers must provide at least that much header data.
- Disabled-tracing macro overrides must stay compatible with call signatures, or no-op builds will break.

## Test signals
Build with tracing disabled to validate no-op stubs, build with `CONFIG_BRCM_TRACING` to validate trace generation, and exercise error/debug/hexdump/BCDC/SDPCM call sites while inspecting trace buffers for expected fields and lengths.
