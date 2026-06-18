# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_ads.h

### Purpose
`intel_guc_ads.h` declares the GuC ADS lifecycle, policy-printing, reset, and engine-usage mapping APIs.

### Important APIs, Types, And Functions
It declares create/destroy/late-init/reset helpers, `intel_guc_ads_print_policy_info()`, `intel_guc_engine_usage_record_map()`, and `intel_guc_engine_usage_offset()` for `struct intel_guc`, `struct intel_engine_cs`, and `struct drm_printer`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on iosys-map and forward declarations. It integrates GuC core, debug/status code, and engine usage accounting with ADS implementation. Risks are declaration drift or callers using engine usage maps before ADS creation. Compile coverage and GuC ADS create/reset tests are signals.
