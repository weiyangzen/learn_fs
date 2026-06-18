# sources/distributed-fs/ceph-client/sound/aoa/codecs/onyx.c

## Purpose

This file implements the Apple Onboard Audio Onyx/PCM3052 codec driver. It registers as an I2C driver, exposes an `aoa_codec`, initializes the codec registers, creates ALSA mixer and IEC958 controls based on connected endpoints, and attaches PCM capabilities to an AOA soundbus device.

## Important APIs, types, and functions

The core state is `struct onyx`, containing a write-only register cache, I2C client, AOA codec, initialization and lock flags, open count, optional codec info copy, and mutex. Important functions include `onyx_read_register`, `onyx_write_register`, mixer callbacks for volume/input gain/capture/mute/single-bit/SPDIF controls, `onyx_set_spdif_pcm_rate`, `onyx_register_init`, `onyx_usable`, `onyx_prepare`, `onyx_open`, `onyx_close`, `onyx_switch_clock`, PM suspend/resume callbacks, `onyx_init_codec`, `onyx_exit_codec`, `onyx_i2c_probe`, and `onyx_i2c_remove`.

## Control Flow

I2C probe allocates state, reads the control register to verify hardware, fills codec callbacks, and registers with AOA core. Fabric attachment calls `onyx_init_codec()`, which resets hardware through GPIO, initializes cached registers, creates an ALSA codec device, tailors transfer capabilities for connected inputs/outputs, attaches to soundbus, and adds ALSA controls. Runtime ALSA callbacks lock the mutex, read from cache or hardware, validate ranges, and write I2C registers. PCM prepare locks or disables S/PDIF or analog paths depending on format/rate; close unlocks when the last stream closes.

## State and Persistence

Write-only registers 65-80 are cached in `onyx->cache`. ALSA controls persist on the single AOA card. `spdif_locked`, `analog_locked`, and `open_count` persist across stream lifetime. PM resume restores registers from cache after GPIO reset. The codec node reference is held from probe to remove.

## Dependencies and Integration Points

It depends on I2C SMBus, OF nodes, ALSA controls, IEC958 constants, AOA core helpers, soundbus attach/detach, and fabric-provided GPIO. The layout fabric assigns `connected`, GPIO, and soundbus fields before init.

## Risks and Test Signals

Risks include cache desynchronization for write-only registers, I2C errors ignored by some setters, ALSA controls created without full rollback on partial failure, single-card assumptions, lock flags leaving controls busy, and rate-dependent S/PDIF disable behavior. Tests should cover probe/remove, register init, all mixer controls, S/PDIF status/rate controls, connected-bit permutations, PM suspend/resume, PCM open/prepare/close, and error unwinds.
