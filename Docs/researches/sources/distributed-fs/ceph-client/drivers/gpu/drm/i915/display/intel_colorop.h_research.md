# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.h

## Purpose
Declares i915 colorop wrapper helpers for the DRM plane color pipeline implementation.

## APIs and integration
The header forward-declares `enum intel_color_block`, `struct drm_colorop`, and `struct intel_colorop`, then exposes conversion, allocation, creation, and destruction helpers. `intel_color_pipeline.c` uses these declarations to create typed i915 colorop objects and register the destroy callback with DRM.

## State, dependencies, risks, and tests
It owns no state. Its declarations are a narrow boundary between generic DRM colorop code and i915 display types. Risks are signature drift with DRM helper callbacks or missing declarations when new color block types are introduced. Build coverage and plane pipeline property teardown tests are sufficient signals.
