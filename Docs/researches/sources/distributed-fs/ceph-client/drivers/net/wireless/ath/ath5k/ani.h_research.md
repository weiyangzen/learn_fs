# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.h

## Purpose

`ani.h` declares the ath5k Adaptive Noise Immunity interface and state. It defines thresholds, max levels, operating modes, the persistent `struct ath5k_ani_state`, and function prototypes used by calibration, interrupt, RX error, sysfs, and debug code.

## Important APIs, Types, And Constants

- Thresholds: `ATH5K_ANI_LISTEN_PERIOD`, `ATH5K_ANI_OFDM_TRIG_HIGH`, `ATH5K_ANI_OFDM_TRIG_LOW`, `ATH5K_ANI_CCK_TRIG_HIGH`, and `ATH5K_ANI_CCK_TRIG_LOW`.
- RSSI thresholds: `ATH5K_ANI_RSSI_THR_HIGH` and `ATH5K_ANI_RSSI_THR_LOW`.
- Level caps: `ATH5K_ANI_MAX_FIRSTEP_LVL` and `ATH5K_ANI_MAX_NOISE_IMM_LVL`.
- `enum ath5k_ani_mode`: off, manual low, manual high, and auto.
- `struct ath5k_ani_state`: mode, current immunity/weak-signal state, max spur level, active counters, and debug/stat snapshots.
- Lifecycle paths: `ath5k_ani_init()`, `ath5k_ani_mib_intr()`, `ath5k_ani_calibration()`, and `ath5k_ani_phy_error_report()`.
- Manual controls: setters for noise immunity, spur immunity, firstep, OFDM weak signal, and CCK weak signal.
- Debug: `ath5k_ani_print_counters()`.

## Control Flow

Attach/base code initializes or restores ANI mode; MIB interrupt handling calls `ath5k_ani_mib_intr()`; RX descriptor processing calls `ath5k_ani_phy_error_report()` on older hardware; calibration calls `ath5k_ani_calibration()`; sysfs/debug paths call manual setters and read `ani_state`.

## State And Persistence Behavior

`struct ath5k_ani_state` is embedded in `struct ath5k_hw` and persists for the device lifetime. It tracks current hardware-programmed levels and algorithm counters. Debug fields are reset by `ath5k_ani_init()`, so accumulated stats do not survive mode reinitialization.

## Dependencies And Integration Points

The header includes `../ath.h` for shared ath definitions and forward-declares `enum ath5k_phy_error_code`. It is consumed by `ani.c`, `ath5k.h`, `base.c`, `desc.c`, `sysfs.c`, and `debug.c`.

## Risks

Changing thresholds or max levels changes RF behavior. `max_spur_level` is chip-specific and must not be treated as a fixed macro. Manual setters can be called while auto mode is active, but calibration may later overwrite the settings. Debug/stat consumers must account for resets on `ath5k_ani_init()`.

## Test Signals

Compile all declared functions with ath5k. Verify mode transitions reset state and apply expected defaults. Confirm sysfs/debug controls enforce limits and reflect `ani_state`. Ensure MIB and RX PHY error paths compile and drive calibration/tasklet behavior across debug and non-debug builds.
