# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/pp_thermal.h

## Purpose

`pp_thermal.h` provides shared thermal policy constants for PowerPlay, especially SMU7-era temperature ranges and critical-temperature-fault offsets. It is a small data header used by thermal controller setup code.

## Important APIs, Types, And Functions

The file includes `power_state.h` and defines two static `struct PP_TemperatureRange` arrays: `SMU7ThermalWithDelayPolicy` and `SMU7ThermalPolicy`. Each contains a low/normal row with minimums around `-273150` and maximums around `99000`, and a high/emergency row around `120000`. It also defines `CTF_OFFSET_EDGE`, `CTF_OFFSET_HOTSPOT`, and `CTF_OFFSET_HBM`, each set to 5.

## Control Flow And Data Flow

There is no executable control flow. Consumers select one of the static policies and copy or reference threshold values when initializing thermal management. CTF offsets are used as adjustment constants when deriving firmware critical temperature thresholds.

## State And Persistence Behavior

The arrays are static read-only data in each translation unit that includes the header. Programmed thermal thresholds persist in SMC firmware or hardware thermal controllers after consumers apply them.

## Dependencies And Integration Points

The header depends on `struct PP_TemperatureRange` from `power_state.h` and `__maybe_unused`. It integrates with SMU7 hwmgr thermal setup, fan policy, software CTF handling, and thermal interrupt or polling paths.

## Risks And Edge Cases

Because arrays are `static const` in a header, each includer gets its own copy. The initializer omits the final `sw_ctf_threshold` field, relying on zero initialization. Temperature units must match `PP_TEMPERATURE_UNITS_PER_CENTIGRADES`. Delayed versus non-delayed behavior is not encoded in these values.

## Test Signals

Validation should include thermal controller init on SMU7 ASICs, fan response around 99 C and 120 C thresholds, software CTF tests, suspend/resume threshold restoration, and build coverage with warnings enabled for struct initializer changes.
