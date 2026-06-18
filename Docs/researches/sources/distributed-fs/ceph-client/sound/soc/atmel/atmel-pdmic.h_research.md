# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.h

## Purpose
This header defines PDMIC register offsets and bit fields used by the Atmel PDM microphone controller driver.

## Important APIs, Types, And Functions
It defines `PDMIC_CR`, `PDMIC_MR`, `PDMIC_CDR`, interrupt registers, `PDMIC_DSPR0`, `PDMIC_DSPR1`, write-protect registers, and masks/shifts for software reset, PDM enable, clock source, prescaler, overrun interrupt, high-pass and SINCC filter bypass, sample size, oversampling ratio, gain scale, shift, digital gain, and offset.

## Control Flow
None.

## State And Persistence
The macros describe volatile PDMIC MMIO state. Gain/offset/filter fields are user-visible through ALSA controls and component probe initialization.

## Dependencies And Integration Points
It depends on Linux bit helpers and is included by `atmel-pdmic.c`. Correct mask definitions are required for clock, DMA, gain, and interrupt handling.

## Risks And Test Signals
Wrong fields could disable capture, select incorrect sample width, or corrupt gain/offset. Test signals are register dumps after probe and `hw_params`, ALSA control round trips for gain/filter switches, and capture data with expected word size and level.
