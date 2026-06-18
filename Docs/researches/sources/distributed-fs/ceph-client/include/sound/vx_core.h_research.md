<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/vx_core.h -->
# sources/distributed-fs/ceph-client/include/sound/vx_core.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/vx_core.h` is Shared ALSA core contract for
Digigram VX cards, covering DSP command/status buffers, pipe bookkeeping, low-level board
operations, firmware loading, IRQ handling, pseudo-DMA, mixer, IEC958, clocking, and PM helpers. The
source was read as a complete 535-line header for this report.

## Important APIs, Types, and Functions

types: `firmware`, `device`, `vx_rmh`, `vx_ibl_info`, `vx_pipe`, `vx_core`, `snd_vx_ops`,
`snd_vx_hardware`; enums: `anonymous enum`; typedefs: `pcx_time_t`; functions/prototypes: `char`,
`int`, `snd_vx_setup_firmware`, `snd_vx_load_boot_image`, `snd_vx_dsp_boot`, `snd_vx_dsp_load`,
`snd_vx_free_firmware`, `snd_vx_irq_handler`, `snd_vx_threaded_irq_handler`, `vx_send_msg`,
`vx_send_msg_nolock`, `vx_send_rih`, `vx_send_rih_nolock`, `vx_reset_codec`, and 13 more; inline
helpers: `vx_test_and_ack`, `vx_validate_irq`, `snd_vx_inb`, `snd_vx_inl`, `snd_vx_outb`,
`snd_vx_outl`, `vx_reset_dsp`, `vx_pseudo_dma_write`, `vx_pseudo_dma_read`; macros/constants:
`__SOUND_VX_COMMON_H`, `VX_DRIVER_VERSION`, `SIZE_MAX_CMD`, `SIZE_MAX_STATUS`, `VX_MAX_PIPES`,
`VX_MAX_PERIODS`, `VX_MAX_CODECS`, `SND_VX_HWDEP_ID`, `VX_ANALOG_OUT_LEVEL_MAX`, `vx_inb`,
`vx_outb`, `vx_inl`, `vx_outl`, `vx_check_isr`, and 87 more

## Control Flow

Card-specific PCI/PCMCIA code creates `vx_core` with a `snd_vx_ops` vtable, loads boot/DSP firmware,
registers PCM/mixer/hwdep devices, then runtime paths send RMH commands, perform pseudo-DMA
transfers through callbacks, process IRQ events, and update clock/audio-source state.

## State and Persistence Behavior

Runtime state is substantial: `vx_core` stores ALSA card/PCM/hwdep handles, IRQ, locks, firmware
pointers, DSP status, pipe arrays, mixer levels, monitor levels, clock source/mode/frequency, IEC958
bits, IBL info, and per-pipe buffer positions.

## Dependencies and Integration Points

Direct includes: `sound/pcm.h`, `sound/hwdep.h`, `linux/interrupt.h`. Integrates with ALSA core,
ASoC codec/card drivers, rawmidi/seq, firmware loading, or legacy card drivers depending on the
matching subsystem.

## Risks and Edge Cases

Risks include vtable callbacks missing for a board type, command/status length overruns, lock misuse
between IRQ and normal RMH sends, stale firmware pointers across suspend, pseudo-DMA position drift,
and hardware-type alias registers being used with the wrong card family.

## Test Signals

Test VX222 and VXpocket variants, firmware load stages, IRQ acknowledge/threaded handling,
playback/capture period accounting, mixer mute/monitor changes, external clock detection, IEC958
status, suspend/resume, and error-code masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/vx_core.h -->
