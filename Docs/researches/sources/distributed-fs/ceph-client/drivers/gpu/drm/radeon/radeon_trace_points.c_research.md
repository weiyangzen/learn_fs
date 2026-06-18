<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c

## Purpose
`radeon_trace_points.c` is the single compilation unit that instantiates the Radeon tracepoints declared in `radeon_trace.h`.

## Important APIs, types, and functions
The file includes DRM Radeon UAPI and `radeon.h`, defines `CREATE_TRACE_POINTS`, and includes `radeon_trace.h`. It contains no functions of its own; the generated tracepoint definitions are produced by the Linux trace infrastructure.

## Control flow
Build-time control flow is the important behavior: ordinary source files include `radeon_trace.h` for declarations, while this file includes it with `CREATE_TRACE_POINTS` so storage and registration code are emitted exactly once. This avoids multiple-definition errors while still allowing every driver file to use `trace_radeon_*` calls.

## State, dependencies, and integration points
The generated tracepoint state is registered with the kernel tracing subsystem. This translation unit depends on all types referenced by tracepoint prototypes being visible through `radeon.h` and included DRM headers. It integrates with every file that calls Radeon tracepoints, especially VM, command submission, fences, semaphores, and BO allocation paths.

## Risks and test signals
The main risk is omitting this file from the build or defining `CREATE_TRACE_POINTS` elsewhere, causing missing trace symbols or duplicate definitions. Test signals are successful module/kernel link, visible Radeon trace events in tracing interfaces, and no unresolved `trace_radeon_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_trace_points.c -->
