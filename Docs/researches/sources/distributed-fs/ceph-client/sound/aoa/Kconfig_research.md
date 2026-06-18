# sources/distributed-fs/ceph-client/sound/aoa/Kconfig

## Purpose

This file declares the Apple Onboard Audio top-level config menu and sources fabric, codec, and soundbus submenus.

## Important APIs, types, and functions

It defines `SND_AOA`, a tristate option depending on `PPC_PMAC` and selecting `SND_PCM`.

## Control Flow

When `SND_AOA` is enabled, Kconfig sources `sound/aoa/fabrics/Kconfig`, `sound/aoa/codecs/Kconfig`, and `sound/aoa/soundbus/Kconfig`.

## State and Persistence

The config selection persists in `.config`. Runtime AOA state is implemented in the subdirectories.

## Dependencies and Integration Points

It integrates AOA with ALSA and PowerMac platform support. It is consumed by `sound/aoa/Makefile`.

## Risks and Test Signals

Risks include exposing AOA on unsupported architectures or missing PCM dependency selection. Build tests should cover PowerMac configs with AOA built-in and modular, plus non-PowerMac configs where it is unavailable.
