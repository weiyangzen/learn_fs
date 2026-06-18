## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_slpc.h

Purpose: declares SLPC feature predicates and public lifecycle, frequency, policy, PM interrupt, waitboost, and diagnostic APIs.

Important APIs, types, and functions:
- `SLPC_MAX_FREQ_MHZ` defines the special/upper frequency constant used by SLPC code.
- Inline predicates `intel_guc_slpc_is_supported()`, `intel_guc_slpc_is_wanted()`, and `intel_guc_slpc_is_used()` combine `guc->slpc` support/selection with GuC submission use.
- Public APIs include early/full init, enable, fini, max/min/boost set/get, info print, media ratio mode, PM interrupt mask enable, boost/decrement waiters, efficient-frequency ignore, strategy, and power profile setters.

Control flow:
- Higher-level UC and GT PM code use predicates to decide whether to allocate, enable, expose sysfs/debugfs controls, and route waitboost/policy requests through SLPC.

State and persistence:
- No header-owned state; it exposes operations on `struct intel_guc_slpc` defined in `intel_guc_slpc_types.h`.

Dependencies and integration points:
- Includes GuC submission predicates and SLPC type definition. Used by GuC debugfs, PM/sysfs, request wait paths, and UC init.

Risks:
- `intel_guc_slpc_is_used()` must only be true when GuC submission is actually active; exposing controls too early can lead to `-ENODEV`.
- API users must understand which setters are cached/persistent across reset and which are immediate firmware commands.

Test signals:
- Compile and policy matrix tests for support/wanted/used.
- Runtime tests for each public setter/getter through sysfs/debugfs and reset/re-enable.
