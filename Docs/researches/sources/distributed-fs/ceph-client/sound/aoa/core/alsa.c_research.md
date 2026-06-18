# sources/distributed-fs/ceph-client/sound/aoa/core/alsa.c

## Purpose

This file manages the single ALSA card used by Apple Onboard Audio and provides helper wrappers for codec/fabric code to create ALSA devices and controls.

## Important APIs, types, and functions

Public APIs are `aoa_alsa_init`, `aoa_get_card`, `aoa_alsa_cleanup`, `aoa_snd_device_new`, and `aoa_snd_ctl_add`. Module parameter `index` controls ALSA card index. Static `aoa_card` stores the active card wrapper.

## Control Flow

`aoa_alsa_init()` rejects a second card, allocates an ALSA card with private `aoa_card`, fills names, registers the card, and unwinds on failure. Device creation gets the current card, calls `snd_device_new`, immediately registers the device, and frees it if registration fails. Control addition forwards to `snd_ctl_add`.

## State and Persistence

`aoa_card` is a singleton global. The ALSA card persists until `aoa_alsa_cleanup()` frees it and clears the pointer.

## Dependencies and Integration Points

It depends on ALSA core device/control APIs and is called from AOA fabric registration and codec init paths through `aoa.h`.

## Risks and Test Signals

Risks include the single-card assumption, immediate device registration ordering, NULL card failures reported as `-ENOMEM`, and controls not being freed on later codec errors. Tests should cover init/cleanup, duplicate init, device/control failure unwinds, and codec registration before card creation.
