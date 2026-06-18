# sources/distributed-fs/ceph-client/sound/aoa/soundbus/Kconfig

## Purpose

This file declares the generic Apple Soundbus option and the I2S soundbus implementation option.

## Important APIs, types, and functions

It defines `SND_AOA_SOUNDBUS`, selecting `SND_PCM`, and `SND_AOA_SOUNDBUS_I2S`, depending on `SND_AOA_SOUNDBUS && PCI`.

## Control Flow

Kconfig selections control generic soundbus support and I2S bus implementation availability.

## State and Persistence

Configuration persists in `.config`. Runtime bus state is in `soundbus/core.c` and `i2sbus` files.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the soundbus Makefile. The layout fabric selects both symbols.

## Risks and Test Signals

Risks include missing PCI dependency for I2S or missing PCM selection for soundbus. Build tests should cover generic soundbus only and full I2S support.
