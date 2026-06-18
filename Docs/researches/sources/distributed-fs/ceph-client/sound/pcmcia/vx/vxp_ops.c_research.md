# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_ops.c

## Purpose

This file adapts the shared Digigram VX core to the VXPocket PCMCIA register map. It supplies low-level register access, Xilinx/DSP firmware loading, interrupt acknowledgement, pseudo-DMA transfer, codec programming, input source switching, clock source switching, and mic hardware programming.

## Important APIs, types, and functions

`snd_vxpocket_ops` is the exported callback table consumed by `snd_vx_create()`. Important callbacks include `vxp_inb()`, `vxp_outb()`, `vxp_test_and_ack()`, `vxp_validate_irq()`, `vxp_write_codec_reg()`, `vxp_load_dsp()`, `vxp_dma_write()`, `vxp_dma_read()`, `vxp_change_audio_source()`, `vxp_set_clock_source()`, `vxp_reset_dsp()`, `vxp_reset_codec()`, and `vxp_reset_board()`. Public helpers `vx_set_mic_boost()` and `vx_set_mic_level()` are used by the mixer.

## Control flow

Firmware load is staged: boot image, Xilinx bitstream, DSP boot, then DSP image. The Xilinx path enters reprogramming mode, saves CSUER/RUER, handshakes through ISR/RX/TX registers, validates the magic byte, restores registers, resets codec and DSP, and returns errors on handshake failure. Runtime DMA enables pseudo-DMA mode in DIALOG/ICR, transfers 16-bit words with wraparound through the PCM buffer, then disables the mode. Interrupt acknowledgement checks MEMIRQ, pulses ACK, and the shared VX threaded IRQ performs higher-level work.

## State and persistence behavior

`struct snd_vxpocket` caches `regCDSP`, `regDIALOG`, `port`, and `mic_level`. The code mutates cached CDSP/DIALOG bits and writes them to hardware, because several register bits are write-only control state. PCM pipe positions are persisted in shared `struct vx_pipe::hw_ptr`.

## Dependencies and integration points

It depends on `sound/vx_core.h` helpers such as `vx_wait_isr_bit()`, `vx_wait_for_rx_full()`, `snd_vx_load_boot_image()`, and shared PCM/control orchestration. PCMCIA resource setup in `vxpocket.c` supplies the I/O base and IRQ. `vxp_mixer.c` consumes mic helpers; VX core consumes the ops table.

## Risks and test signals

Risks include firmware handshake timeouts, corrupted cached write-only bits, pseudo-DMA alignment mistakes, off-by-one ring wrap during DMA read/write, interrupt ACK races, and model-specific mic bit handling. Test firmware loading through all four indexes, playback/capture wraparound, IRQ validation, digital/line/mic source switching, clock switching, and both VXPocket and VXPocket440 mic paths.
