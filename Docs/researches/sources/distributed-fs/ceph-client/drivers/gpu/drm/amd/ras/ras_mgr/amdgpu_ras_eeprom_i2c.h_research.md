# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_eeprom_i2c.h

## Purpose

`amdgpu_ras_eeprom_i2c.h` exposes the AMDGPU I2C EEPROM system-function table to the RAS manager.

## Important APIs, Types, And Functions

The only public symbol is `extern const struct ras_eeprom_sys_func amdgpu_ras_eeprom_i2c_sys_func;`, which provides EEPROM transfer and configuration callbacks.

## Control Flow, State, And Persistence

The header has no runtime control flow or storage. Persistence is supplied by the implementation through the physical EEPROM table.

## Dependencies And Integration Points

It includes `ras.h` for `struct ras_eeprom_sys_func` and is consumed by `amdgpu_ras_mgr.c` when populating `ras_core_config.eeprom_cfg`.

## Risks And Test Signals

Risks are declaration/definition drift and missing object selection in `ras_mgr/Makefile`. Test signals are build/link coverage and successful EEPROM callback installation during RAS manager creation.
