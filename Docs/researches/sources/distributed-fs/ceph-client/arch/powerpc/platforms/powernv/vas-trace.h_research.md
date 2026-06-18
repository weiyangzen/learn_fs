## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/vas-trace.h

### Purpose
`vas-trace.h` defines tracepoints for VAS receive-window open, send-window open, and CRB paste operations.

### Important APIs, Types, And Functions
Trace events are `vas_rx_win_open`, `vas_tx_win_open`, and `vas_paste_crb`. They record current task pid, VAS id, coprocessor type, lpid/pid/tid attributes, window id, and paste kernel address depending on the event.

### Control Flow
`vas-window.c` defines `CREATE_TRACE_POINTS` before including this header, causing tracepoint definitions to be emitted. Window open and paste paths call the trace hooks before validation or hardware paste.

### State, Persistence, And Dependencies
There is no retained state beyond ftrace/perf trace buffers. Dependencies include tracepoint infrastructure, `struct vas_rx_win_attr`, `struct vas_tx_win_attr`, and `struct pnv_vas_window`.

### Integration Points
The header sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so generated trace code can locate it from the PowerNV source directory.

### Risks
Trace fields must stay in sync with public VAS attribute structures. The paste event assumes a `pnv_vas_window` pointer with valid `vinst` and `paste_kaddr`.

### Test Signals
Kernel trace builds, enabling each tracepoint, and VAS open/paste workloads showing expected fields validate it.
