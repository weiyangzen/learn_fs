<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h

### Purpose
`trace.h` declares Linux tracepoints for Intel GVT internals. The events cover shadow page table lifecycle, guest-to-host address translation, out-of-sync page handling, command scanning, interrupt propagation, MSI injection, and render MMIO switching.

### Important APIs, Types, And Functions
It defines `TRACE_SYSTEM gvt` and trace events `spt_alloc`, `spt_free`, `gma_index`, `gma_translate`, `spt_refcount`, `spt_change`, `spt_guest_change`, `oos_change`, `oos_sync`, `gvt_command`, `write_ir`, `propagate_event`, `inject_msi`, and `render_mmio`. It also sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for `trace/define_trace.h`.

### Control Flow
The header is included by GVT code to emit trace events and by `trace_points.c` with `CREATE_TRACE_POINTS` to instantiate them. Each event describes arguments, copies fields into a trace entry, and formats a compact print string for ftrace/perf consumers.

### State, Persistence, And Dependencies
The file holds no runtime state. Trace state is owned by the kernel tracing subsystem. Dynamic arrays are used for raw command dwords in `gvt_command`; fixed-size local buffers are used for formatted event text. Dependencies include tracepoint macros, Linux types, stringify helpers, and architecture TSC inclusion.

### Integration Points
GVT MM, command parser, interrupt, and scheduler code can call generated `trace_*` helpers. Users observe these through ftrace, tracefs, perf, or kernel tracing infrastructure when GVT tracepoints are enabled.

### Risks
Trace formatting must not read beyond command length or overflow fixed buffers; the code uses `snprintf()` and dynamic arrays for those cases. Event ABI names and field layouts are consumed by tracing tools, so renaming or changing field meaning can break diagnostics. Tracing command contents may expose guest workload details to privileged tracing users.

### Test Signals
Build tests must verify tracepoint generation with and without multiple includes. Runtime signals include enabling each GVT trace event under tracefs while creating, running, resetting, and destroying vGPUs, and checking that command events print the expected raw dword arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/trace.h -->
