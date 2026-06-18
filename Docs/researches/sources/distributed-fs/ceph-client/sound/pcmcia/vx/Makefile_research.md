# sources/distributed-fs/ceph-client/sound/pcmcia/vx/Makefile

## Purpose

This Makefile builds the ALSA PCMCIA Digigram VXPocket module.

## Important APIs, types, and functions

It declares `snd-vxpocket-y := vxpocket.o vxp_ops.o vxp_mixer.o` and wires `obj-$(CONFIG_SND_VXPOCKET) += snd-vxpocket.o`.

## Control flow

Kbuild links the PCMCIA probe/lifecycle code, low-level VX hardware operations, and mixer controls into one module when `CONFIG_SND_VXPOCKET` is enabled.

## State and persistence behavior

There is no runtime state. Build state is controlled entirely by Kconfig and Kbuild object selection.

## Dependencies and integration points

The module depends on the shared VX core APIs used by `vxp_ops.c` and `vxpocket.c`, plus PCMCIA and ALSA core configuration selected elsewhere.

## Risks and test signals

Risks are missing object membership or config drift. Build `CONFIG_SND_VXPOCKET=m/y` and confirm `snd-vxpocket.ko` contains all three objects and resolves `snd_vxpocket_ops` and `vxp_add_mic_controls`.
