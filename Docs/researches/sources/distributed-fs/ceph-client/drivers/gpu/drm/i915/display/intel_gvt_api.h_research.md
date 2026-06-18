# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.h

Purpose: declares the GVT-facing i915 display offset and pipe-validity API.

Important APIs/types/functions: declares functions for pipe, transcoder, cursor, display MMIO base offsets, and pipe validity. Forward-declares `enum pipe`, `enum transcoder`, and `struct intel_display`.

Control flow: no executable code; consumers call into `intel_gvt_api.c`.

State and persistence: no state in the header. Returned values reflect display runtime info and MMIO layout.

Dependencies and integration: includes Linux types and is intended for GVT namespace consumers.

Risks: callers must treat this as a query interface only and not assume every enum value is valid on every platform.

Test signals: compile GVT consumers and verify all declared symbols resolve from the `I915_GVT` namespace.
