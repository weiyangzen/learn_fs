# sources/distributed-fs/ceph-client/sound/soc/samsung/i2s.h

## Purpose
Provides Samsung I2S public DAI names and machine-driver clock/divider IDs.

## Important APIs, Types, And Functions
Defines `SAMSUNG_I2S_DAI`, `SAMSUNG_I2S_DAI_SEC`, `SAMSUNG_I2S_DIV_BCLK`, `SAMSUNG_I2S_RCLKSRC_0`, `SAMSUNG_I2S_RCLKSRC_1`, `SAMSUNG_I2S_CDCLK`, `SAMSUNG_I2S_OPCLK`, and OPCLK source constants such as `SAMSUNG_I2S_OPCLK_PCLK`.

## Control Flow
No executable flow. Machine drivers pass these constants to `snd_soc_dai_set_sysclk()` or `snd_soc_dai_set_clkdiv()`.

## State And Persistence
No state.

## Dependencies And Integration Points
Shared by Samsung machine drivers and `i2s.c`. It is the lightweight external contract for configuring Samsung I2S clocks without exposing register internals.

## Risks And Edge Cases
Constants must remain synchronized with `i2s_set_sysclk()` and `i2s_set_clkdiv()` switch cases. Incorrect clock ID use returns `-EINVAL` or can conflict with active DAI state.

## Test Signals
Compile coverage for machine drivers and runtime clock setup calls on Arndale, Midas, Odroid, Snow, SMDK, Aries, and other Samsung boards.
