## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_print.h

Purpose: provides GuC-prefixed logging and warning macros layered on GT print helpers.

Important APIs, types, and functions:
- `guc_printk()` maps a GuC pointer to GT print functions with `"GUC: "` prefix.
- Convenience macros include `guc_err`, `guc_warn`, `guc_notice`, `guc_info`, `guc_dbg`, rate-limited variants, and `guc_probe_error`.
- Warning helpers include `guc_WARN`, `guc_WARN_ONCE`, `guc_WARN_ON`, and `guc_WARN_ON_ONCE`.

Control flow:
- No runtime logic beyond macro expansion. Callers use these macros for consistent GuC diagnostics.

State and persistence:
- No state. Messages flow through GT/i915 logging infrastructure.

Dependencies and integration points:
- Includes `gt/intel_gt.h` and `gt/intel_gt_print.h`, and requires `guc_to_gt()` to be valid for the provided GuC pointer.

Risks:
- Macros evaluate the GuC expression in logging context; callers should avoid side-effect expressions.
- Wrong GuC pointer leads to wrong GT association or crash in diagnostics.

Test signals:
- Compile coverage and log output inspection in GuC init/error paths.
