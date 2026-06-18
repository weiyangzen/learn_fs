# sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.h

## Purpose
Defines Samsung PCM machine-driver constants for source clock selection and SCLK-per-frame divider selection.

## Important APIs, Types, And Functions
Defines `S3C_PCM_CLKSRC_PCLK`, `S3C_PCM_CLKSRC_MUX`, and `S3C_PCM_SCLK_PER_FS`.

## Control Flow
No executable flow. Machine drivers pass these constants to `snd_soc_dai_set_sysclk()` and `snd_soc_dai_set_clkdiv()`.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by `pcm.c` and SMDK PCM machine driver. It is the public configuration contract for the Samsung PCM DAI.

## Risks And Edge Cases
Constants must remain aligned with `s3c_pcm_set_sysclk()` and `s3c_pcm_set_clkdiv()`.

## Test Signals
Compile coverage and SMDK PCM `hw_params` successfully configuring `S3C_PCM_CLKSRC_MUX` and `S3C_PCM_SCLK_PER_FS`.
