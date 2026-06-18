# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.h

## Purpose
This header defines the SAMA5D2 CLASSD amplifier register map and bit fields used by `atmel-classd.c`.

## Important APIs, Types, And Functions
It exports offsets for `CLASSD_CR`, `CLASSD_MR`, `CLASSD_INTPMR`, `CLASSD_THR`, interrupt registers, and write-protect register. It also defines masks/shifts/values for left/right enable and mute, PWM type, non-overlap timing, attenuation, DSP clock family, deemphasis, swap, frame/sample-rate selection, EQ configuration, mono mode, and reset.

## Control Flow
None.

## State And Persistence
The definitions address volatile MMIO state. `CLASSD_INTPMR` has a default in the driver's regmap cache, so its fields persist across suspend through regcache.

## Dependencies And Integration Points
The header is tightly coupled to `atmel-classd.c` and the hardware manual. It uses plain macros rather than `GENMASK`, so callers must combine masks and shifts carefully.

## Risks And Test Signals
Wrong masks or shifts can invert channels, leave outputs muted, or select bad clock/sample-rate/EQ values. Test signals are register dumps matching expected mode fields after probe and `hw_params`, audible playback, and ALSA controls mapping to documented dB/EQ behavior.
