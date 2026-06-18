# sources/distributed-fs/ceph-client/sound/aoa/codecs/Kconfig

## Purpose

This file declares Apple Onboard Audio codec driver options for Onyx, TAS, and Toonie chips.

## Important APIs, types, and functions

It defines `SND_AOA_ONYX`, `SND_AOA_TAS`, and `SND_AOA_TOONIE`. Onyx and TAS select `I2C` and `I2C_POWERMAC`; Toonie has no I2C dependency because it is a simple DAC codec wrapper.

## Control Flow

Kconfig selections control whether the matching codec modules are built and can be auto-requested by layout fabric.

## State and Persistence

Selected symbols persist in `.config`. Runtime codec state is in the `.c` files.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the codecs Makefile. The layout fabric requests modules named `snd-aoa-codec-*`.

## Risks and Test Signals

Risks include missing I2C dependencies and fabric requesting unavailable codec modules. Build tests should compile each codec alone and in combination with the layout fabric.
