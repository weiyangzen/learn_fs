# sources/distributed-fs/ceph-client/drivers/video/backlight/aat2870_bl.c

## Purpose
This platform driver controls the AnalogicTech AAT2870 backlight block through callbacks exposed by the AAT2870 MFD core.

## Important APIs, types, and functions
`struct aat2870_bl_driver_data` stores the platform device, backlight device, channel mask, max current, and cached brightness. Key functions are `aat2870_brightness`, `aat2870_bl_enable`, `aat2870_bl_disable`, `aat2870_bl_update_status`, `aat2870_bl_probe`, and `aat2870_bl_remove`.

## Control flow
Probe requires platform data and the expected platform ID, registers a raw backlight, applies channel/current/max-brightness defaults, initializes brightness to max, and calls update. Updates validate brightness, scale the requested backlight brightness into the chip current register, write `AAT2870_BLM`, disable all channels at zero, and enable configured channels on transition from off to nonzero. Remove forces power off and brightness zero.

## State and persistence
Runtime state is device-managed, with a cached brightness used for transition decisions. Hardware register state persists until changed by the MFD or reset.

## Dependencies and integration points
It depends on `MFD_AAT2870_CORE`, platform data, parent device driver data, and the backlight core. The MFD provides the actual `write` operation.

## Risks and test signals
Risks include no platform data, invalid platform ID, scaling divide assumptions, parent driver-data mismatch, and inconsistent hardware state after failed writes. Test signals include default and explicit platform data, all-channel and subset-channel masks, brightness 0/max/intermediate transitions, remove path power-off, and MFD write failure injection.
