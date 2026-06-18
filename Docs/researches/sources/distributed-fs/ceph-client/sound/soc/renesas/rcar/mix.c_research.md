# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/mix.c

## Purpose

`mix.c` implements the R-Car MIX block, which combines up to four CTU/SRC inputs into one stream with per-input volume and optional volume ramping. It registers ALSA controls for the relevant MIX input lane and shared ramp controls.

## Important APIs, types, and functions

`struct rsnd_mix` stores the module plus control configs for volume lanes A-D, ramp enable, ramp-up rate, ramp-down rate, and flags recording which lanes exist. `rsnd_mix_probe()` allocates DT-described MIX modules and initializes clocks. `rsnd_mix_probe_()` attaches the matching CMD module. `rsnd_mix_pcm_new()` maps SRC IDs to MIX volume lanes, creates a `MIX Playback Volume` control for that lane, initializes the software value to max, and installs shared ramp controls once. `rsnd_mix_volume_init()` and `rsnd_mix_volume_update()` program MIX channel count, ramp, lane volumes, and update enable state.

## Control Flow

On stream init, MIX powers on, resets/activates, writes general info and ramp settings, writes volume registers, then enables dB setting. ALSA control writes update software values and call `rsnd_mix_volume_update()` to disable dB setting, rewrite lane volumes, and re-enable it. Volume lane selection is based on the connected SRC ID: SRC3/6 to A, SRC4/9 to B, SRC0/1 to C, and SRC2/5 to D.

## State and Persistence Behavior

Per-lane and ramp control values persist in `struct rsnd_mix`. `ONCE_KCTRL_INITIALIZED` prevents duplicate shared ramp controls while allowing multiple lane controls for streams sharing one MIX. Hardware state is rebuilt on init and can be updated by control writes.

## Dependencies and Integration Points

MIX depends on SRC identity, CTU/CMD routing, common control helpers, `volume_ramp_rate[]` from `core.c`, and SCU pseudo-register access. It is primarily a playback-side multi-source integration point.

## Risks and Test Signals

Risks include unsupported SRC-to-lane mappings, duplicated or missing controls for shared MIX paths, ramp control scope across multiple inputs, and route assumptions delegated to the integrator. Tests should run two or more DAIs feeding one MIX, verify independent lane volumes, exercise ramp changes during playback, inspect `CMD_ROUTE_SLCT`, and validate error handling for unsupported SRC IDs.
