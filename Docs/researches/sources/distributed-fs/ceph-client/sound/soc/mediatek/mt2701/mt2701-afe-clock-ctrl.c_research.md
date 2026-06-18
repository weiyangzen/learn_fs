# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-clock-ctrl.c

## Purpose

This file implements MT2701/MT7622 AFE clock acquisition and sequencing. It obtains the base audio gates, per-I2S source/divider/MCLK/hopping/ASRC clocks, optional Bluetooth merge-interface clock, and exposes helpers used by the PCM driver's runtime PM and DAI callbacks.

## Important APIs, Types, and Functions

- `mt2701_init_clock()` gets named clocks from DT and fills `mt2701_afe_private`.
- `mt2701_afe_enable_clock()` and `mt2701_afe_disable_clock()` control global audsys gates and AFE/ASYS register enables.
- `mt2701_afe_enable_i2s()` / `mt2701_afe_disable_i2s()` enable ASRC output and per-direction I2S hopping clocks.
- `mt2701_afe_enable_mclk()` / `mt2701_afe_disable_mclk()` wrap per-I2S MCLK gates.
- `mt2701_enable_btmrg_clk()` / `mt2701_disable_btmrg_clk()` control the optional BT merge gate.
- `mt2701_mclk_configuration()` chooses an MCLK parent from the 98.304 MHz or 90.3168 MHz PLL domains and programs the divider.

## Control Flow

Probe calls `mt2701_init_clock()`. Runtime resume calls `mt2701_afe_enable_clock()`, which enables base gates in dependency order, sets `ASYS_TOP_CON_ASYS_TIMING_ON`, enables `AFE_DAC_CON0_AFE_ON`, and writes ASRC initialization values. Runtime suspend clears those register bits and disables gates in reverse-ish order. I2S startup enables MCLK, prepare configures parent/divider, and path enable activates ASRC/hopping clocks. Shutdown disables path clocks and MCLK.

## State and Persistence Behavior

Clock handles and per-I2S MCLK rates live in `mt2701_afe_private` and `mt2701_i2s_path`. Hardware state is register-backed and is reset/reprogrammed across runtime PM. The PCM driver's backup list preserves selected AFE registers around suspend.

## Dependencies and Integration Points

The file depends on Common Clock Framework, regmap, MT2701 register macros, and `struct mt2701_afe_private`. It is linked into the platform object and called by `mt2701-afe-pcm.c`.

## Risks and Edge Cases

Clock-name mismatches in DT cause probe failure, except `audio_mrgif_pd` is optional unless probe defers. `mt2701_mclk_configuration()` requires `mclk_rate` to divide one supported PLL domain; a zero or unsupported rate fails. BT merge helpers assume `mrgif_ck` is valid before use. Correct unwind order matters because partial clock enable failures otherwise leave gates active.

## Test Signals

Probe logs for all required clock names, runtime PM suspend/resume loops, I2S playback/capture at 44.1/48 kHz families, high-rate MCLK requests, and BT SCO startup/shutdown are the main signals.
