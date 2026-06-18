# sources/distributed-fs/ceph-client/net/switchdev/Kconfig

## Purpose
This Kconfig entry exposes `NET_SWITCHDEV`, the core switchdev support option. It enables generic glue between networking core objects and hardware or hardware-like switch offload drivers.

## Important APIs, Types, And Functions
The file declares one boolean symbol, `NET_SWITCHDEV`, named "Switch (and switch-ish) device support". It depends on `INET`.

## Control Flow
At configuration time, enabling the symbol allows the build system to include the switchdev core. No runtime control flow exists in this file.

## State And Persistence
The selected value is persisted in the kernel `.config`. It controls whether switchdev code is compiled into the kernel image because the corresponding Makefile uses `obj-y`.

## Dependencies And Integration Points
The dependency on `INET` reflects integration with the core network stack. Drivers that offload bridge, VLAN, FDB, MDB, or L3 behavior rely on this symbol being available.

## Risks And Test Signals
The main risk is configuration coverage: drivers expecting switchdev helpers need `NET_SWITCHDEV=y`. Test signals are Kconfig dependency resolution, successful builds with representative switchdev drivers, and absence of unresolved switchdev symbols.
