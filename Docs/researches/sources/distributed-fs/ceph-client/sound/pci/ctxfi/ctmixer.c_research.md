# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.c

## Purpose

This file builds the ctxfi internal mixer topology and exports ALSA mixer controls for volumes, capture/playback switches, IEC958 status, analog route, and model-specific output/mic controls.

## Important APIs, types, and functions

Public entry points are `ct_mixer_create()`, `ct_mixer_destroy()`, and `ct_alsa_mix_create()`. Internal enums map ALSA controls to AMIXER and SUM resources. `ct_mixer_kcontrols_create()` registers controls. `ct_mixer_topology_build()` wires AMIXER and SUM resources. `mixer_get_output_ports()`, `mixer_set_input_left()`, and `mixer_set_input_right()` are installed in `struct ct_mixer`. Volume handlers scale ALSA values by `VOL_SCALE`; switch handlers call `do_switch()`.

## Control flow

Creation allocates arrays, allocates SUM and AMIXER resources from ATC resource managers, builds a fixed stereo topology, and exposes operations. ALSA control creation loops over enabled volume and switch descriptors, adds IEC958 controls, and conditionally adds output, mic-source, and RCA route controls from hardware capabilities. Runtime switch changes update `mixer->switch_state`, rewire capture AMIXERs for selected sources, and call ATC mute/source functions.

## State and persistence behavior

The mixer persists `switch_state`, AMIXER scale/input/sum configuration, SUM resources, and ALSA kcontrols. PM resume recommits every AMIXER and reapplies each switch state. Two static `kctls` pointers cache line-in and mic switch controls for notifications, which is explicitly noted as problematic for multiple cards.

## Dependencies and integration points

It depends on `ctatc`, `ctresource`, `ctamixer`, ALSA control/TLV/PCM APIs, and hardware capability callbacks. PCM routing uses `ct_mixer` operations to connect PCM/SRC resources to mixer ports. IEC958 controls call ATC SPDIF get/set helpers.

## Risks and test signals

Risks include the global `kctls[2]` multi-card bug, mutable static control templates during registration, incomplete rollback on `snd_ctl_add()` errors, route/switch mismatches for dedicated RCA cards, and capture source conflicts. Test signals include `amixer` enumeration, volume persistence across suspend/resume, line/mic mutual exclusion notifications, SPDIF status round trips, RCA/front routing on CTOK0010, and resource leak checks after failed creation.
