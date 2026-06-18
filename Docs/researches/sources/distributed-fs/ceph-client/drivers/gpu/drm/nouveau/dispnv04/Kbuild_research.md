# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/Kbuild

## Purpose
This Kbuild fragment adds legacy NV04-era Nouveau display implementation objects to the main `nouveau-y` object list.

## Important APIs, Types, And Data
It includes objects for arbitration, CRTC, cursor, DAC, DFP, display setup, low-level hardware helpers, I2C encoders, overlay, TV modes, and NV04/NV17 TV output handling. It also includes the `dispnv04/i2c/Kbuild` subfragment.

## Control Flow, State, And Integration
The fragment is included by the top-level Nouveau Kbuild during module assembly. The files in this work item (`arb.o`, `crtc.o`, `cursor.o`, `dac.o`, `dfp.o`) become part of the legacy display path used by pre-NV50 hardware.

## Risks And Test Signals
Removing or misordering objects can break legacy modesetting symbols. The fragment assumes the top-level include paths have already been set. Test signals are Nouveau builds on configs covering legacy display code, no unresolved `nv04_*`/`nouveau_calc_arb` symbols, and runtime display init on NV04-NV4x GPUs.
