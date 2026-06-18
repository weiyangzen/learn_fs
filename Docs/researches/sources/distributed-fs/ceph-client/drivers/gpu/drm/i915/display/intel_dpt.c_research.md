<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c

## Purpose
This file manages display page table configuration for framebuffers scanned out through GGTT-to-DPT mappings. It toggles the platform DPT enable/disable hardware knobs and preserves DPT-backed framebuffer mappings across system suspend and resume.

## Important APIs, Types, and Functions
The exported functions are `intel_dpt_configure()`, `intel_dpt_suspend()`, and `intel_dpt_resume()`. `intel_dpt_configure()` writes `PLANE_CHICKEN_DISABLE_DPT` per non-cursor plane on display version 14 and `CHICKEN_MISC_DISABLE_DPT` on display version 13, based on `display->params.enable_dpt`. Suspend/resume functions walk all registered DRM framebuffers under `mode_config.fb_lock` and call parent DPT callbacks for framebuffers with `fb->dpt`.

## Control Flow
Configuration is called per CRTC and branches by display generation. On version 14 it iterates planes on the CRTC and skips the cursor; on version 13 it uses a global display chicken register. Suspend first returns on no-display platforms, then locks framebuffer enumeration and suspends each DPT. Resume mirrors that flow and restores DPT PTEs after GGTT mappings have been restored.

## State and Persistence Behavior
The file does not allocate DPTs. It operates on persistent `struct intel_framebuffer` DPT pointers created by the framebuffer layer. During S4 and some S3RST-to-S4 flows, DPT page table contents are not stored in the hibernation image, so `intel_dpt_resume()` is responsible for reprogramming mappings rather than assuming the table memory remained valid.

## Dependencies and Integration Points
It depends on display MMIO helpers, `intel_display_types`, `intel_parent_dpt_suspend()`, `intel_parent_dpt_resume()`, and plane register definitions. It is coupled with `intel_fb.c` and `intel_fb_pin.c`, which decide when a framebuffer uses DPT, create DPT objects, and pin DPT VMAs for scanout.

## Risks
Calling suspend/resume in the wrong order relative to GGTT suspend/resume can leave hardware page tables pointing at stale or missing mappings. A mismatch between `enable_dpt` and the chicken-register setting changes how non-linear framebuffers are addressed. Framebuffer enumeration must stay under `fb_lock` because DPT-backed framebuffers can be added or destroyed by userspace.

## Test Signals
Signals include suspend/resume with tiled or compressed framebuffers, no blank scanout after hibernation/resume, correct behavior with `enable_dpt` toggled, no cursor-plane DPT side effects on display version 14, and framebuffer lifetime tests that create/destroy DPT-backed framebuffers around suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c -->
