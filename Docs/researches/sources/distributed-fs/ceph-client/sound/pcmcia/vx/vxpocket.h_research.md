# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.h

## Purpose

This header defines the VXPocket private device structure, shared declarations, and PCMCIA hardware bit masks used by `vxpocket.c`, `vxp_ops.c`, and `vxp_mixer.c`.

## Important APIs, types, and functions

`struct snd_vxpocket` embeds `struct vx_core`, stores I/O port, mic level, cached CDSP/DIALOG register values, ALSA card index, and `struct pcmcia_device *`. `to_vxpocket()` converts from `vx_core` to the containing type. The header declares `snd_vxpocket_ops`, `vx_set_mic_boost()`, `vx_set_mic_level()`, and `vxp_add_mic_controls()`.

## Control flow

There is no executable control flow. The macros define how control flow in `vxp_ops.c` manipulates CDSP reset/source/clock/IRQ/mic bits and DIALOG Xilinx/DMA/ACK bits.

## State and persistence behavior

The important persisted state is cached write-only register content in `regCDSP` and `regDIALOG`. Bit masks in this header define which portions of that cache select DSP reset, codec reset, input source, mic mode, IRQ validation, Xilinx reprogramming, pseudo-DMA, and MEMIRQ acknowledgement.

## Dependencies and integration points

It depends on `sound/vx_core.h` and PCMCIA headers. All VXPocket implementation files include it, and the shared VX core indirectly depends on the ops and container layout declared here.

## Risks and test signals

Risks are incorrect bit definitions for VXPocket variants, stale cached register semantics, and container layout assumptions. Build coverage plus hardware tests for reset, IRQ, source selection, and pseudo-DMA mode are the primary signals.
