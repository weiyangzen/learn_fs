# sources/distributed-fs/ceph-client/sound/aoa/soundbus/i2sbus/control.c

## Purpose

This file implements low-level control helpers for Apple I2S soundbus devices. It discovers platform functions for enabling the bus, cell, and clocks, and falls back to KeyLargo FCR register bits for bus 0 and 1 when platform functions are absent.

## Important APIs, types, and functions

Public functions are `i2sbus_control_init`, `i2sbus_control_destroy`, `i2sbus_control_add_dev`, `i2sbus_control_remove_dev`, `i2sbus_control_enable`, `i2sbus_control_cell`, and `i2sbus_control_clock`. State is carried in `struct i2sbus_control` and `struct i2sbus_dev` fields declared in `i2sbus.h`.

## Control Flow

Initialization allocates a control object, initializes its list, and records the macio chip. Adding a device discovers PMF functions named `enable`, `cell-enable`, `clock-enable`, `cell-disable`, and `clock-disable`; nonzero/nonone bus numbers require all PMF functions because FCR fallback is only known for buses 0 and 1. Enable/cell/clock operations prefer PMF calls, otherwise check macio base and set or clear the matching KeyLargo FCR bit. Device removal deletes the device list item and destroys the control object when the list becomes empty.

## State and Persistence

The control object persists while at least one I2S device is on its list. Each I2S device stores PMF function handles discovered at add time. Hardware enable state is in PMF-managed firmware or KeyLargo FCR registers.

## Dependencies and Integration Points

It depends on macio, PowerMac feature and platform-function APIs, KeyLargo register macros, I/O access macros, and I2S bus structures. Higher-level I2S core/PCM code calls these helpers around bus and clock operations.

## Risks and Test Signals

Risks include unbalanced PMF function references on normal remove, fallback register writes lacking locking as noted by comments, destroying shared control while callers still hold pointers, unsupported bus numbers without full PMF data, and invalid enable values. Tests should cover PMF-present and FCR-fallback paths, buses 0/1 and unsupported buses, enable/disable sequencing, list lifetime, and error returns for missing macio base.
