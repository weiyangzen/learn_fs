# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_step.c

Purpose: Converts PCI revision IDs or GMD IP step fields into normalized Intel graphics/media stepping values stored in runtime info.

Important APIs/functions: `intel_step_init()` selects a platform-specific revision table or GMD-based conversion, then writes `RUNTIME_INFO(i915)->step`. `intel_step_name()` returns printable step names. `gmd_to_intel_step()` maps GMD step numbers onto the `STEP_A0`-based enum and clamps future values to `STEP_FUTURE`.

Control flow: If `HAS_GMD_ID(i915)` is true, graphics and media IP step fields are converted directly. Otherwise `intel_step_init()` selects one of many static `intel_step_info` tables for SKL/KBL/BXT/GLK/ICL/JSL/EHL/TGL/RKL/DG1/ADL/RPL/DG2 variants. Unknown gaps warn, then use the next non-empty table entry if possible; out-of-range values become future graphics stepping.

State/persistence: No persistent allocations. The only state mutation is `RUNTIME_INFO(i915)->step`. Static tables encode platform knowledge and preserve unusual non-monotonic revision-to-step mappings.

Dependencies/integration: Depends on platform detection macros, PCI revision via `INTEL_REVID()`, `drm_warn/drm_dbg`, and `drm/intel/step.h` enum values. Other i915 workarounds and feature gates use normalized stepping.

Risks: Missing or stale table entries can select incorrect workarounds. Gap fallback may be wrong for non-monotonic stepping tables, but avoids defaulting to zero. `gmd_to_intel_step()` assumes four numeric steps per letter as documented in the header.

Test signals: Boot logs show warnings for unknown revisions and debug messages for fallback/future steppings. Coverage is mostly platform bring-up and workaround selection behavior rather than standalone unit tests.
