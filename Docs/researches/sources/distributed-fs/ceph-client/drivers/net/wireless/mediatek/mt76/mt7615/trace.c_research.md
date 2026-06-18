# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/trace.c

Purpose: Instantiates mt7615 tracepoints declared in `mt7615_trace.h`.

Important APIs and functions: Defines `CREATE_TRACE_POINTS` before including `mt7615_trace.h`, guarded by `#ifndef __CHECKER__` for sparse compatibility.

Control flow and integration: Compiled once into the driver so the tracepoint declarations become definitions. Other files can include the trace header without defining storage.

State and persistence: No runtime state beyond kernel tracepoint registration.

Dependencies: Linux module infrastructure and tracepoint generation macros.

Risks: If this file is omitted from the build, tracepoint users link-fail. If `CREATE_TRACE_POINTS` is duplicated elsewhere, duplicate definitions occur.

Test signals: Successful module link and visibility of mt7615 tracepoints in kernel tracing.
