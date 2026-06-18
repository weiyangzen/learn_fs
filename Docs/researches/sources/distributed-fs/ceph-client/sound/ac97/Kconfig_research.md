# sources/distributed-fs/ceph-client/sound/ac97/Kconfig

## Purpose

This file declares the newer AC97 bus Kconfig symbols used by drivers that want automatic AC97 codec probing and optional compatibility with older `struct snd_ac97` users.

## Important APIs, types, and functions

It defines `AC97_BUS_NEW` as a tristate bus type and `AC97_BUS_COMPAT` as a bool depending on `AC97_BUS_NEW` and `!AC97_BUS`.

## Control Flow

Drivers select `AC97_BUS_NEW` when they need the new AC97 controller/codec bus. `AC97_BUS_COMPAT` enables the compatibility object only when the legacy AC97 bus is not separately selected.

## State and Persistence

Configuration choices persist in `.config`; runtime bus state is implemented by `bus.c`.

## Dependencies and Integration Points

It is sourced from the top-level sound Kconfig and consumed by `sound/ac97/Makefile`.

## Risks and Test Signals

Risks include selecting both legacy and compat paths at once, or missing compat support for old SoC codecs. Build tests should exercise `AC97_BUS_NEW` with and without `AC97_BUS_COMPAT`, and combinations with legacy `AC97_BUS`.
