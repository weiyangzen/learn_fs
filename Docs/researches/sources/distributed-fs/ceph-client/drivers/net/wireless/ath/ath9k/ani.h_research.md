# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.h

## Purpose

This header declares ath9k Adaptive Noise Immunity constants, state structures, statistics structures, command bits, and public hardware ANI functions. It is the shared contract between ANI implementation and the rest of the ath9k hardware layer.

## Important APIs and types

- Threshold macros such as `ATH9K_ANI_OFDM_TRIG_HIGH`, `ATH9K_ANI_CCK_TRIG_LOW`, and old/below-INI variants define error-rate decision points in errors per second.
- Default setting macros define initial spur immunity, FIR first step, RSSI thresholds, ANI period, poll interval, and legal register-control ranges.
- `enum ath9k_ani_cmd` defines control bits passed to `ath9k_hw_ani_control()`: OFDM weak signal detection, firstep level, spur immunity level, MRC CCK, and all.
- `struct ath9k_mib_stats` stores accumulated ACK/RTS/FCS/beacon counters.
- `struct ath9k_ani_default` stores INI register defaults used by hardware-specific ANI controls.
- `struct ar5416AniState` holds current ANI levels, flags, listen time, PHY error counts, and INI defaults.
- `struct ar5416Stats` holds ANI transition counters, error counters, average beacon RSSI, and MIB stats.
- Public functions are `ath9k_enable_mib_counters()`, `ath9k_hw_disable_mib_counters()`, and `ath9k_hw_ani_init()`.

## Control flow and integration

`ani.c` consumes these definitions to initialize defaults, compare PHY error rates, and apply hardware controls. Other hardware code embeds `struct ar5416AniState` and `struct ar5416Stats` inside `struct ath_hw`, uses `ah_mibStats` as shorthand, and calls the public functions during reset, start/stop, and monitoring.

## State and persistence behavior

The header defines in-memory state only. ANI state persists only for the lifetime of `struct ath_hw`, allowing per-channel/historical immunity decisions while the device is active. Counter and level fields are reset or reinitialized by ANI reset/init paths.

## Dependencies and risks

This header assumes `struct ath_hw` and related register-control functions are visible to includers through ath9k hardware headers. Risk lies in threshold constants and structure layout coupling with `ani.c`; changing defaults can affect RF behavior on all supported chips. Range macros must stay aligned with hardware register fields.

## Test signals

Compile coverage should include all hardware families that include ANI. Runtime signals include expected ANI stats, MIB counter behavior, periodic monitor calls at `ATH9K_ANI_POLLINTERVAL`, and stable throughput/receive sensitivity when default thresholds are used.
