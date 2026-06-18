# sources/distributed-fs/ceph-client/sound/aoa/fabrics/Kconfig

## Purpose

This file declares the AOA layout-id fabric option, which binds codecs to soundbus devices based on PowerMac device-tree layout or device IDs.

## Important APIs, types, and functions

It defines `SND_AOA_FABRIC_LAYOUT`, a tristate option selecting `SND_AOA_SOUNDBUS` and `SND_AOA_SOUNDBUS_I2S`.

## Control Flow

Selecting this option builds the layout fabric and its required soundbus/I2S support.

## State and Persistence

Configuration persists in `.config`. Runtime state is implemented in `layout.c`.

## Dependencies and Integration Points

It is sourced by AOA Kconfig and consumed by the fabrics Makefile.

## Risks and Test Signals

Risks include missing soundbus dependencies and unavailable fabric for supported machines. Build tests should compile this fabric with AOA and I2S bus enabled.
