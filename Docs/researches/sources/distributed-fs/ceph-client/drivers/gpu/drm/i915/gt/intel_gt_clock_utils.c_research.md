# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_clock_utils.c

### Purpose
`intel_gt_clock_utils.c` determines the GT timestamp clock frequency for each generation and converts between GT clock/PM intervals and nanoseconds.

### Important APIs, Types, And Functions
Public functions are `intel_gt_init_clock_frequency()`, debug-only `intel_gt_check_clock_frequency()`, `intel_gt_clock_interval_to_ns()`, `intel_gt_pm_interval_to_ns()`, `intel_gt_ns_to_clock_interval()`, and `intel_gt_ns_to_pm_interval()`. Internal readers cover Gen11+, Gen9, Gen6, Gen5, G4x, and Gen4.

### Control Flow
Initialization reads platform registers such as `CTC_MODE`, `TIMESTAMP_OVERRIDE`, and `RPM_CONFIG0` or uses documented fixed frequencies. It stores `gt->clock_frequency` and `gt->clock_period_ns`, with a special Icelake CTX timestamp period. Conversion helpers use integer multiply/divide and Gen6 PM interval conversion rounds to a multiple of 25 to avoid known RPS issues.

### State, Persistence, And Dependencies
State is persisted in `gt->clock_frequency` and `gt->clock_period_ns`. Dependencies include uncore MMIO reads, platform version checks, `i915_freq` helpers, GT register definitions, and integer math helpers.

### Integration Points
GT MMIO init calls this before subsystems that need timestamp scaling. RPS/PM code, debugfs, request timing, and GuC busyness paths use the conversion helpers.

### Risks
Clock registers are assumed stable after initialization. Wrong source selection or crystal-clock decoding skews timeouts, PM thresholds, busyness accounting, and debug output. Zero frequency on unsupported generations must not be used by conversion callers.

### Test Signals
Test frequency decoding on Gen4 through Gen12+, timestamp override paths, debug check warnings when firmware changes clocking, conversion round-trip behavior, and Gen6 PM rounding.
