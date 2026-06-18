# sources/distributed-fs/ceph-client/sound/aoa/core/Makefile

## Purpose

This Makefile builds the AOA core module that contains codec/fabric coordination, ALSA helper functions, and GPIO implementations.

## Important APIs, types, and functions

It adds `snd-aoa.o` under `CONFIG_SND_AOA` and composes it from `core.o`, `alsa.o`, `gpio-pmf.o`, and `gpio-feature.o`.

## Control Flow

Kbuild links the core pieces into one module or built-in object when AOA is enabled.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is controlled by AOA Kconfig and provides exported symbols consumed by codecs and fabrics.

## Risks and Test Signals

Risks include missing GPIO implementation objects or link-order issues. Build tests should enable AOA core with PMF and feature GPIO users.
