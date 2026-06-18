# sources/distributed-fs/ceph-client/sound/aoa/fabrics/Makefile

## Purpose

This Makefile builds the AOA layout fabric module.

## Important APIs, types, and functions

It maps `snd-aoa-fabric-layout-y += layout.o` and adds `snd-aoa-fabric-layout.o` under `CONFIG_SND_AOA_FABRIC_LAYOUT`.

## Control Flow

Kbuild conditionally compiles `layout.c` into the fabric object.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It consumes the layout fabric Kconfig symbol and produces a module that registers a soundbus driver.

## Risks and Test Signals

Risks are limited to build wiring and module naming used by users/configs. Build tests should cover built-in and modular layout fabric.
