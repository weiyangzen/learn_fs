# sources/distributed-fs/ceph-client/sound/ppc/pmac.h

## Purpose

This header defines the shared private interface for the `snd-powermac` module: DBDMA command storage, stream state, hardware model/capability state, callback hooks, Keywest I2C context, and exported functions used by codec, beep, and platform files.

## Important APIs, types, and functions

`struct pmac_dbdma` describes coherent DBDMA command storage. `struct pmac_stream` stores PCM stream state, DBDMA registers, command ring, substream, and current rate/format masks. `enum snd_pmac_model` identifies AWACS, Screamer, Burgundy, DACA, Tumbler, and Snapper. `struct snd_pmac` is the central device object. Function declarations cover low-level creation, PCM creation, beep attachment/control, PM, codec initialization, Keywest I2C, and automute.

## Control flow

No code executes here, but callback fields in `struct snd_pmac` define runtime flow: codec files install `set_format`, `update_automute`, `detect_headphone`, `suspend`, and `resume`; `pmac.c` calls them from PCM/control/PM paths.

## State and persistence behavior

The header defines all persistent PowerMac driver state: resources, MMIO mappings, AWACS register cache, stream rings, IRQs, mixer pointers, controls, feature flags, and codec hooks. It also fixes the maximum DBDMA fragment count at `PMAC_MAX_FRAGS`.

## Dependencies and integration points

It includes ALSA control/PCM, AWACS definitions, ADB/PMU/CUDA/NVRAM, TTY/VT, DBDMA, Open Firmware, machine, and PowerMac feature headers. All PowerMac sound implementation files depend on this contract.

## Risks and test signals

Risks include central-struct ABI drift inside the module, callback misuse, and compile breakage from platform header changes. Test by building every PowerMac codec combination and checking runtime callback installation for each detected model.
