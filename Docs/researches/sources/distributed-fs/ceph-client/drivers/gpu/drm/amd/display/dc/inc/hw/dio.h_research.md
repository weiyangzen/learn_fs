# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dio.h

## Purpose

`dio.h` defines a small Display I/O abstraction for memory power control. It currently exposes an object and vtable to control I2C light-sleep behavior in DIO memory.

## Important APIs, Types, And Functions

`struct dio_funcs` contains `mem_pwr_ctrl(struct dio *dio, bool enable_i2c_light_sleep)`. `struct dio` stores the vtable and DC context.

## Control Flow

Callers invoke `mem_pwr_ctrl` when display I/O memory power policy changes, typically during init, low-power entry/exit, or link/DDC-related transitions.

## State And Persistence Behavior

`dio` persists in the resource pool. Hardware retains the selected memory power state. The header stores no additional state.

## Dependencies And Integration Points

It includes `dc_types.h` and integrates with `resource_pool`, clock/power management, DDC/I2C/AUX paths, and HWSS or resource init code that controls DIO power.

## Risks And Edge Cases

Enabling I2C light sleep while DDC/AUX-like operations need hardware access could cause communication failures. Unsupported ASICs may have a null or minimal DIO implementation. Power sequencing must coordinate with link hotplug and HPD handling.

## Test Signals

Tests should cover display init, suspend/resume, DDC reads with light sleep enabled/disabled, hotplug, and low-power transitions. EDID read failures and link-detection instability are relevant signals.
