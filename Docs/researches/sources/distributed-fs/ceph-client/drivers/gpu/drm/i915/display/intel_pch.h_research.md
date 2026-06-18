# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.h

Purpose: defines PCH compatibility categories and helper macros used throughout display code.

Important types/macros: `enum intel_pch` is ordered by south display compatibility and includes real PCHs (`IBX` through `ADP`), `PCH_NOP`, `PCH_NONE`, and fake PCHs for DG1/DG2/MTL/LNL. Macros like `HAS_PCH_LPT()`, `HAS_PCH_SPLIT()`, and `INTEL_PCH_TYPE()` centralize checks.

Control flow/state: no runtime logic beyond macro evaluation against `display->pch_type`. Declares `intel_pch_detect()` and `intel_pch_init_clock_gating()`.

Dependencies/integration: included by PCH display/refclk/backlight/LVDS and platform-specific display code.

Risks/test signals: enum ordering and compatibility comments matter because many checks imply inherited south display behavior. Build and platform boot tests catch misuse.
