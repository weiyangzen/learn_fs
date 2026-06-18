# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-mediatek-trace.h

## Purpose
Declares MediaTek UFS tracepoints for event reporting and clock scaling decisions.

## Important APIs and tracepoints
`TRACE_SYSTEM` is `ufs_mtk`. `TRACE_EVENT(ufs_mtk_event)` records an event type and data value. `TRACE_EVENT(ufs_mtk_clk_scale)` records the clock name, scale direction, and resulting clock rate. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this host-driver path.

## Control flow and state
There is no persistent state. When `ufs-mediatek.c` defines `CREATE_TRACE_POINTS`, these declarations generate tracepoint definitions. Runtime callers emit events through `trace_ufs_mtk_event()` and `trace_ufs_mtk_clk_scale()`.

## Dependencies and integration points
Depends on the Linux tracepoint framework. Integrated with MediaTek event notification and clock scaling code for observability without always printing logs.

## Risks and test signals
Risks are trace include path breakage when files move, format-string mismatch, and unhelpful event IDs unless correlated with UFSHCD event enums. Test signals are successful tracepoint generation, visibility under tracefs/perf, and emitted records during UIC errors and devfreq clock scaling.
