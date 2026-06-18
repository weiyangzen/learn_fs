# sources/distributed-fs/ceph-client/sound/aoa/codecs/toonie.c

## Purpose

This file implements the simple Toonie codec driver used on Mac Mini hardware. Toonie is treated as an analog-output-only DAC with no I2C register programming.

## Important APIs, types, and functions

State is a single global `struct toonie *toonie` containing an `aoa_codec`. Important functions are `toonie_init_codec`, `toonie_exit_codec`, `toonie_usable`, optional PM no-op callbacks, module `toonie_init`, and `toonie_exit`. `toonie_transfers` advertises big-endian 16/24-bit output rates from 32 kHz through 96 kHz.

## Control Flow

Module init allocates the codec, fills name/owner/init/exit, and registers with AOA. Fabric init requires `connected == 1`, creates an ALSA codec device, and attaches to the soundbus. Exit detaches the soundbus codec; module exit unregisters and frees the singleton.

## State and Persistence

The singleton codec persists for the module lifetime. There is no hardware register cache or mutable control state.

## Dependencies and Integration Points

It depends on AOA core, ALSA device helpers, and soundbus attach/detach. The layout fabric sets `connected` and soundbus fields for supported Mac Mini layouts.

## Risks and Test Signals

Risks include singleton assumptions, no controls for mute/power, and strict connected-bit matching. Tests should cover registration before/after fabric, attach/detach, unsupported connection masks, and PCM capability exposure.
