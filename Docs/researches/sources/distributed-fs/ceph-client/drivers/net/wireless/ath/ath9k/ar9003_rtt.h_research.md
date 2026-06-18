# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_rtt.h

## Purpose
`ar9003_rtt.h` declares the AR9003 radio retention table interface and provides no-op stubs when PCOEM support is not compiled. It lets calibration and reset code call RTT helpers without scattering preprocessor conditionals across the driver.

## Important APIs, Types, and Functions
When `CONFIG_ATH9K_PCOEM` is enabled, the header declares `ar9003_hw_rtt_enable()`, `ar9003_hw_rtt_disable()`, `ar9003_hw_rtt_set_mask()`, `ar9003_hw_rtt_force_restore()`, `ar9003_hw_rtt_load_hist()`, `ar9003_hw_rtt_fill_hist()`, `ar9003_hw_rtt_clear_hist()`, and `ar9003_hw_rtt_restore()`. When it is disabled, the same names are inline stubs: void functions do nothing and boolean functions return `false`.

## Control Flow
The header has no active control flow beyond compile-time selection. It creates two call patterns: PCOEM builds execute the implementation in `ar9003_rtt.c`, while non-PCOEM builds compile out RTT side effects. Callers can therefore try RTT restore opportunistically and fall back to normal calibration when the returned boolean is false.

## State and Persistence Behavior
No state is stored in the header. The enabled implementation stores retained calibration entries in `ath9k_hw_cal_data`; the disabled stubs leave all calibration state untouched. Because disabled `ar9003_hw_rtt_restore()` returns false, higher layers should not mark RTT restoration successful unless the implementation was present and hardware accepted it.

## Dependencies and Integration Points
The header depends on `struct ath_hw`, `struct ath9k_channel`, and `u32` definitions from the surrounding ath9k include graph. It is included by `ar9003_rtt.c` and calibration code. It also depends indirectly on `ar9003_phy.h` because the implementation uses RTT register macros there, though this header only publishes the function contract.

## Risks
Stubbed-out builds can hide dead code in the enabled implementation unless both configurations are compiled. Because the stub functions silently do nothing, callers must use return values where available and not assume side effects occurred. API changes must keep enabled prototypes and disabled stubs synchronized exactly.

## Test Signals
Build tests should cover both `CONFIG_ATH9K_PCOEM=y` and disabled configurations. Runtime tests in enabled builds should verify RTT restore can avoid unnecessary calibration, while disabled builds should continue through the normal calibration path with no unresolved symbols and no behavioral dependency on RTT state.
