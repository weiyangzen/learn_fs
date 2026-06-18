<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h

## Purpose
This header defines the STA32x/STA326 register addresses, bit fields, coefficient indices, and count constants used by `sta32x.c`.

## Important APIs, Types, And Definitions
It defines `STA32X_REGISTER_COUNT`, `STA32X_COEF_COUNT`, core control registers from `CONFA` through `FDRC2`, coefficient access registers (`CFADDR2`, coefficient byte windows, `CFUD`), mute/volume/config registers, and field masks/shifts for clock selection, serial format, thermal/fault behavior, automodes, output mapping, limiter fields, and coefficient update commands. Coefficient offsets enumerate biquad bases, crossover bases, pre/postscales, thermal postscale, and mixer coefficients.

## Control Flow
No executable flow is defined. The C file uses these constants for regmap ranges, mixer controls, coefficient indirect addressing, DAI format/rate setup, platform-data programming, and power bits.

## State And Persistence
No storage is defined. `STA32X_COEF_COUNT` sizes the C driver's coefficient shadow array and must remain aligned with coefficient offset definitions.

## Dependencies And Integration Points
The header is private to the STA32x codec implementation and is included by `sta32x.c`. Public board policy comes from `<sound/sta32x.h>`, not this file.

## Risks And Edge Cases
Coefficient offsets and register bit masks must match the hardware data sheet because the driver writes indirect coefficient windows using these indices. Bad masks can break thermal/fault policy, output mapping, or mute behavior without compile-time symptoms.

## Test Signals
Compile coverage, coefficient control read/write tests, DAI hw_params register programming, platform property programming, and watchdog cache restore paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/sta32x.h -->
