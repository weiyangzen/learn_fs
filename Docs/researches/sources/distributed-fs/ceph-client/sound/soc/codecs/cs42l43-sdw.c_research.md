# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-sdw.c

## Purpose

`cs42l43-sdw.c` is the small SoundWire stream helper module for the CS42L43 codec component. Unlike CS42L42, CS42L43 appears as an MFD child codec whose parent can be a SoundWire device; this file only connects ASoC DAI stream operations to SoundWire stream add/remove and stream-pointer storage.

## Important APIs, Types, and Functions

- `cs42l43_sdw_add_peripheral()` obtains the `sdw_stream_runtime` from DAI DMA data, converts ALSA params to SoundWire stream and port configs, chooses the SoundWire data port from `dai->id`, and calls `sdw_stream_add_slave()`.
- `cs42l43_sdw_remove_peripheral()` gets the same stream and parent SoundWire slave, then calls `sdw_stream_remove_slave()`.
- `cs42l43_sdw_set_stream()` stores the stream pointer in DAI DMA data for the selected direction.

## Control Flow

The main codec driver wires these helpers into SoundWire DAI ops. A machine driver calls `.set_stream`, `hw_params` calls `cs42l43_sdw_add_peripheral()` and then sample-rate programming in `cs42l43.c`, and `hw_free` calls `cs42l43_sdw_remove_peripheral()`. The parent SoundWire slave is recovered with `dev_to_sdw_dev(priv->dev->parent)`.

## State and Persistence Behavior

This file persists no independent state. It reads `struct cs42l43_codec` from component drvdata and relies on DAI DMA data to hold the `sdw_stream_runtime`. The active stream association is owned by ASoC/SoundWire core state.

## Dependencies and Integration Points

It depends on `CONFIG_SND_SOC_CS42L43_SDW`, the SoundWire core, `sound/sdw.h`, ASoC DAI/component APIs, and `cs42l43.h`. The functions are exported in namespace `SND_SOC_CS42L43` and are compiled as `snd-soc-cs42l43-sdw.o`.

## Risks

The helper assumes the codec device parent is a SoundWire slave. Calling it for a non-SoundWire parent would miscast device state. The data port number is exactly `dai->id`, so DAI table changes in `cs42l43.c` must remain aligned with SoundWire DP numbering. Missing `.set_stream` causes `-EINVAL` at `hw_params`/`hw_free`.

## Test Signals

Exercise each CS42L43 SoundWire DAI DP1 through DP7, verify capture/playback port numbering, confirm no stream leaks after `hw_free`, test missing stream pointer failures, and compile both reachable and non-reachable `CONFIG_SND_SOC_CS42L43_SDW` paths because `cs42l43.h` supplies stubs when this module is absent.
