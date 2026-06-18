# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3_reg.h

## Purpose

This header documents and defines the PS3 audio hardware register offsets, field masks, field values, FIFO destination addresses, DMA kick events/statuses, and source/destination encoding used by `snd_ps3.c`.

## Important APIs, types, and functions

It defines interrupt/config registers, `PS3_AUDIO_DMAC_REGBASE()`, `PS3_AUDIO_KICK/SOURCE/DEST/DMASIZE()`, audio mute/buffer pointer/interrupt registers, 3-wire serial control registers, S/PDIF control/status/user-bit registers, and field macros such as `PS3_AUDIO_AX_IE_ASOBEIE()`, `PS3_AUDIO_AO_3WMCTRL_ASOEN()`, `PS3_AUDIO_KICK_EVENT_AUDIO_DMA()`, `PS3_AUDIO_KICK_STATUS_MASK`, and `PS3_AUDIO_AO_3W_LDATA/RDATA()`.

## Control flow

No code executes here. `snd_ps3.c` uses the macros to poll DMA status, clear interrupts, program chained DMA events, reset serial buffers, enable 3-wire output, choose LSB data placement, and target audio FIFO left/right data ports.

## State and persistence behavior

The header describes MMIO state and documented field behavior, including write-one-to-clear status bits, sticky CLEAR behavior, buffer reset semantics, and DMA status progression. Software state is held in `snd_ps3_card_info`.

## Dependencies and integration points

It is consumed by the PS3 sound driver and must match the PS3 audio hardware specification and LV1/PS3AV setup expectations. The DMA sizing macro in `snd_ps3.h` depends on `PS3_AUDIO_DMASIZE_BLOCKS_MASK`.

## Risks and test signals

Risks include incorrect bit positions, stale comments versus hardware behavior, writes to reserved fields, and event-chain mistakes that can starve the FIFO or create interrupt storms. Test with register traces during playback start/stop, underflow recovery, rate/width changes, and DMA channel status polling.
