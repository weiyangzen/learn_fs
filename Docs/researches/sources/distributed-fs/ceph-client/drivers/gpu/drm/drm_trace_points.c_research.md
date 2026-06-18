# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_trace_points.c

Purpose: instantiates the DRM tracepoints declared in `drm_trace.h`.

Important APIs/types/functions: includes `drm/drm_file.h`, defines `CREATE_TRACE_POINTS`, then includes local `drm_trace.h`.

Control flow: compile-time tracepoint instantiation only; the tracepoint macros emit the storage and registration code for events declared in the header.

State and persistence behavior: tracepoint registration/static key state is owned by kernel tracing infrastructure; this file holds no custom state.

Dependencies and integration points: must be built exactly once into DRM core so other files can include `drm_trace.h` without duplicate definitions.

Risks: duplicate `CREATE_TRACE_POINTS` elsewhere causes linker conflicts; omitting this object removes tracepoint definitions. Include order must provide complete types needed by trace macros.

Test signals: DRM core link succeeds, trace events appear once, enabling/disabling vblank tracepoints works, and no duplicate symbol errors under modular and built-in builds.
