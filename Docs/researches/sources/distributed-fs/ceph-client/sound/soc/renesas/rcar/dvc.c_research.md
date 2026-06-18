# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dvc.c

## Purpose

`dvc.c` implements the Digital Volume Control block. It creates playback/capture volume, mute, and volume-ramp ALSA controls, programs DVC registers during stream init and control updates, and attaches the matching CMD block for SCU routing.

## Important APIs, types, and functions

`struct rsnd_dvc` stores the embedded module and control configs for per-channel volume, per-channel mute, ramp enable, ramp-up rate, and ramp-down rate. `rsnd_dvc_probe()` allocates DT-described DVC modules and initializes their clocks. `rsnd_dvc_probe_()` attaches CMD by module ID. `rsnd_dvc_pcm_new()` registers controls named differently for playback (`DVC Out ...`) and capture (`DVC In ...`). `rsnd_dvc_volume_init()` programs initial ADINR, control, ramp, and volume registers. `rsnd_dvc_volume_update()` safely updates mute, ramp, and digital-volume registers by disabling/enabling DVC register access around the update.

## Control Flow

At module init, DVC powers on, resets, initializes volume/ramp state, applies current controls, and enables register access. ALSA control writes update software values through `core.c` kcontrol callbacks, then invoke `rsnd_dvc_volume_update()` immediately. Quit halts DVC and powers off. DMA request support returns the DVC `tx` channel for paths where DVC is DMA-adjacent.

## State and Persistence Behavior

Volume, mute, and ramp settings persist in module-owned `rsnd_kctrl_cfg_*` structures. Hardware state is rebuilt each stream start and can be updated while controls are accepted. Ramp mode temporarily writes maximum volume values to volume registers and uses derived ramp parameters for hardware ramping.

## Dependencies and Integration Points

DVC uses common control registration, common ADINR/channel helpers, CMD attachment, DMA channel request helpers, and pseudo-register access. It can be used after SRC/CTU/MIX and before memory or SSI depending on stream direction.

## Risks and Test Signals

Risks include incorrect channel count for controls, ramp scaling noted by the FIXME, stale control state after rebinding, and capture/playback alignment differences. Test signals include amixer volume/mute/ramp changes before and during playback/capture, DVC with and without SRC conversion, DMA channel availability, debugfs DVC register dumps, and no duplicate controls after card rebind.
