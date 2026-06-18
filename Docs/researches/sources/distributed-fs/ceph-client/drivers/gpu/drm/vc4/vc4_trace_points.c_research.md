# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_trace_points.c

Purpose: Instantiates the tracepoints declared in `vc4_trace.h` for the VC4 driver.

Important APIs/types/functions: Defines `CREATE_TRACE_POINTS` before including `vc4_trace.h`, guarded by `#ifndef __CHECKER__` to avoid sparse/static-analysis issues. Includes `vc4_drv.h` for driver context expected by trace declarations.

Control flow: No runtime control flow. Compilation of this translation unit emits the tracepoint storage/definitions.

State and persistence: Creates static tracepoint metadata and call sites at build/load time. No mutable driver state.

Dependencies and integration points: Must be compiled exactly once with `CREATE_TRACE_POINTS`; other files include `vc4_trace.h` without defining it. Integrated with Linux trace infrastructure.

Risks: Removing or duplicating this file can cause missing or duplicate tracepoint definitions. The `__CHECKER__` guard avoids sparse incompatibility, so changes should preserve that behavior.

Test signals: Kernel build/link should have no duplicate trace symbols. Runtime tracefs should list the `vc4` events declared in the header when tracing support is enabled.
