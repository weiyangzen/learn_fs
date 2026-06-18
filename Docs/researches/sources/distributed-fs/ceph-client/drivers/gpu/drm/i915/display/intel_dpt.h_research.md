<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h

## Purpose
This small header declares the display page table helper API used by the i915 display suspend/resume and CRTC configuration paths.

## Important APIs, Types, and Functions
The header forward declares `struct intel_crtc` and `struct intel_display`, then exposes `intel_dpt_configure()`, `intel_dpt_suspend()`, and `intel_dpt_resume()`. It intentionally does not expose the DPT object internals; those live behind the parent interface and framebuffer structures.

## Control Flow
There is no executable control flow. Callers use this header to invoke DPT configuration during display setup and to bracket system suspend/resume around GGTT state save and restore.

## State and Persistence Behavior
No state is stored here. The API implies that DPT mappings are persistent framebuffer state, but the helper functions must rebuild volatile hardware/PTE programming after low-power transitions.

## Dependencies and Integration Points
The header is included by display power-management and plane/CRTC paths needing DPT configuration. It bridges framebuffer DPT ownership in `intel_fb.c` with system suspend/resume sequencing in the display driver.

## Risks
Because only opaque forward declarations are exposed, callers cannot validate DPT state directly. Misordering these calls relative to GGTT suspend/resume is the primary integration risk.

## Test Signals
Compile coverage of display suspend/resume paths, DPT-enabled framebuffer scanout before and after resume, and no unresolved symbols when DPT support is built with the display driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h -->
