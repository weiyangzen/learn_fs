# sources/distributed-fs/ceph-client/sound/aoa/Makefile

## Purpose

This Makefile recurses into Apple Onboard Audio core, soundbus, fabrics, and codec subdirectories according to config selections.

## Important APIs, types, and functions

It adds `core/`, `soundbus/`, `fabrics/`, and `codecs/` through `obj-$(CONFIG_SND_AOA)` and `obj-$(CONFIG_SND_AOA_SOUNDBUS)`.

## Control Flow

Kbuild includes the core, fabric, and codec pieces when AOA is enabled, and includes the soundbus layer when its config is enabled.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is driven by the AOA Kconfig symbols and feeds Kbuild recursion for all AOA files researched here.

## Risks and Test Signals

Risks include missing soundbus recursion for fabric dependencies and incorrect built-in/module ordering. Build tests should cover AOA with and without soundbus and each codec/fabric as modules.
