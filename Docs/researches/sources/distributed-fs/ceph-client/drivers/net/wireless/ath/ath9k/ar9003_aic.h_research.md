# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.h

## Purpose
`ar9003_aic.h` declares constants, state types, packed SRAM helper structures, and public function prototypes for AR9003 Adaptive Interference Cancellation. It is the local contract between the AIC implementation, MCI Bluetooth coexistence code, and hardware attach paths.

## Important APIs, Types, And Constants
- Include guard: `AR9003_AIC_H`.
- Table/limit constants:
  - `ATH_AIC_MAX_COM_ATT_DB_TABLE` = 6.
  - `ATH_AIC_MAX_AIC_LIN_TABLE` = 69.
  - Rotation attenuation min/max constants cover 0 through 37 dB.
- SRAM/register constants:
  - `ATH_AIC_SRAM_AUTO_INCREMENT` = `0x80000000`.
  - `ATH_AIC_SRAM_GAIN_TABLE_OFFSET` = `0x280`.
  - `ATH_AIC_SRAM_CAL_OFFSET` = `0x140`.
  - `ATH_AIC_SRAM_OFFSET` = `0x00`.
  - `ATH_AIC_BT_JUPITER_CTRL` = `0x66820`.
  - `ATH_AIC_BT_AIC_ENABLE` = `0x02`.
- `enum aic_cal_state` defines the lifecycle states `IDLE`, `STARTED`, `DONE`, and `ERROR`.
- `struct ath_aic_sram_info` models decoded SRAM fields: valid bit, VGA signs, direct/quadrature rotation attenuation, and common attenuation index.
- `struct ath_aic_out_info` holds signed linear direct/quadrature gain values used during interpolation.
- Public functions:
  - `ar9003_aic_calibration()`
  - `ar9003_aic_start_normal()`
  - `ar9003_aic_cal_reset()`
  - `ar9003_aic_calibration_single()`

## Control Flow
This header does not implement control flow, but its declarations define the legal transitions used by `ar9003_aic.c`:
- `AIC_CAL_STATE_IDLE` starts calibration.
- `AIC_CAL_STATE_STARTED` continues calibration.
- `AIC_CAL_STATE_DONE` allows `ar9003_aic_start_normal()` to load normal AIC operation.
- `AIC_CAL_STATE_ERROR` reports unusable calibration state until reset.

## State And Persistence Behavior
The header's structures are temporary decoded forms, not persistent storage. Persistent runtime AIC state is held in `struct ath9k_hw_aic` in `btcoex.h`, while these definitions describe the interpretation of SRAM words and function return values. The constants define hardware offsets and bit values that remain fixed at compile time.

## Dependencies And Integration Points
- Requires `struct ath_hw`, `u8`, `u32`, `int16_t`, and `bool` to be visible from including ath9k/kernel headers.
- Used by `ar9003_aic.c` for implementation and by `ar9003_mci.c` for command handling around calibration/start/reset/single-shot calibration.
- Related state storage lives in `btcoex.h`, which contains `aic_enabled`, `aic_cal_state`, `aic_caled_chan`, `aic_sram`, and `aic_cal_start_time`.
- Hardware field names are in `reg_aic.h`; this header carries only local limits and a few raw offsets.

## Risks
- Constants must match the hardware SRAM layout. A wrong offset or table size causes incorrect SRAM streaming and can corrupt unrelated AIC memory.
- `struct ath_aic_sram_info` uses bitfields only as a decoded software container; it is not safe as a direct packed hardware overlay.
- Return type `u8` for state functions assumes enum values stay small and compatible with MCI message expectations.
- Raw register constants duplicate knowledge that would be safer as named register definitions.

## Test Signals
- Compile tests catch declaration drift between this header and `ar9003_aic.c`.
- Static checks should confirm constants stay consistent with `ATH_AIC_MAX_BT_CHANNEL` and `reg_aic.h` SRAM fields.
- Runtime tests should assert state-return values match `enum aic_cal_state` and that callers handle `ERROR` distinctly from in-progress states.
