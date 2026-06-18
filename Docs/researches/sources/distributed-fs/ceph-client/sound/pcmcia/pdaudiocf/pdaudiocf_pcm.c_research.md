# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_pcm.c

## Purpose

This file exposes PDAudioCF as an ALSA capture-only PCM device. It defines hardware capabilities, prepares the FPGA and AK4117 for the selected sample format, starts/stops capture, and reports the current hardware pointer.

## Important APIs, types, and functions

`snd_pdacf_pcm_new()` creates the PCM named `PDAudioCF`, installs capture ops, uses vmalloc managed buffers, and builds AK4117 controls for the capture substream. `pdacf_pcm_capture_open()` advertises rates from 32 kHz through 192 kHz, mono/stereo, and 16/24/32-bit formats. `pdacf_pcm_prepare()` clears SRAM, computes byte-order/sample-format state, programs FPGA data format and AK4117 digital-interface width, enables FIFO-level IRQs, and records buffer/period pointers. `pdacf_pcm_trigger()` validates digital lock/rate and toggles the RECORD bit.

## Control flow

Open stores the active substream. Prepare rejects stale hardware, derives `pcm_little`, `pcm_swab`, `pcm_xor`, `pcm_sample`, and `pcm_frame`, drains existing SRAM data, and synchronizes the FPGA data format with AK4117 `REG_IO`. Start zeroes software counters, verifies AK4117 is locked and the external rate equals `runtime->rate`, increments `pcm_running`, and sets `PDAUDIOCF_RECORD`; stop clears the bit and decrements the run count. Close reinitializes the device and clears the substream pointer.

## State and persistence behavior

Per-stream state is held in `struct snd_pdacf`: runtime format metadata, capture buffer location, buffer and period sizes, `pcm_hwptr`, `pcm_tdone`, and `pcm_running`. Register updates go through the cached helper under `reg_lock`; PCM buffers are vmalloc-backed, not bus-master DMA-backed.

## Dependencies and integration points

It depends on `pdaudiocf_core.c` for AK4117 setup/reinit and on `pdaudiocf_irq.c` for actual data movement and period accounting. ALSA PCM core calls the ops; AK4117 provides external rate/lock validation and user-visible S/PDIF status controls.

## Risks and test signals

Risks include starting capture on a changed external S/PDIF clock, stale `pcm_xor` for signed formats if not reset between prepares, SRAM clear timeout, and mismatches between advertised formats and transfer helper packing. Test open/close/reprepare cycles, all supported formats, start rejection on unlocked or wrong-rate input, pause/resume triggers, and pointer monotonicity across buffer wrap.
