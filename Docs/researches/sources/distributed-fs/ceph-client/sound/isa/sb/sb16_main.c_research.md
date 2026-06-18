# sources/distributed-fs/ceph-client/sound/isa/sb/sb16_main.c

## Purpose
This file implements the SB16 DSP PCM engine, interrupt handler, DMA allocation control, and non-PnP DSP mixer-register configuration. It is the shared low-level PCM implementation used by SB16-class cards and some clones.

## Important APIs, Types, and Functions
The exported APIs are `snd_sb16dsp_pcm()`, `snd_sb16dsp_get_pcm_ops()`, `snd_sb16dsp_configure()`, and `snd_sb16dsp_interrupt()`. ALSA PCM operations are `snd_sb16_playback_open/close/prepare/trigger/pointer` and capture equivalents. `snd_sb16_setup_rate()` programs shared sample-rate registers. Optional CSP glue functions add compressed formats and start/stop CSP processing. The control `snd_sb16_dma_control` exposes "16-bit DMA Allocation" with Auto, Playback, and Capture choices.

## Control Flow
Opening playback or capture takes `open_lock`, rejects duplicate stream direction, chooses 16-bit DMA if available and not reserved for the opposite direction, otherwise falls back to 8-bit DMA, and sets runtime format/rate/buffer constraints. If no 16-bit channel exists, DSP v4 can still accept 16-bit samples through 8-bit DMA, so the mode combines 8-bit DMA ownership with 16-bit sample format. CSP hooks may add compressed formats for manually loaded or autoloadable codecs.

Prepare calls optional CSP prepare, computes signed/unsigned and mono/stereo format bytes, programs the shared input and output sample rate if not rate-locked, programs ISA DMA with autoinit, writes the DSP auto-init command and period count, and leaves DMA disabled until trigger. Trigger start/resume locks the rate for the active direction and enables the chosen DSP DMA engine; stop/suspend disables it, handles the AWE32 DSP4.13 quirk by re-enabling the other direction if still active, and clears the rate lock bit.

The interrupt handler reads SB16 IRQ status from mixer register `SB_DSP4_IRQSTATUS`, dispatches MPU input to the MPU callback, services 8-bit and 16-bit IRQs separately, calls `snd_pcm_period_elapsed()` for active substreams matching the width, updates CSP QSound during playback, disables unexpected DMA interrupts, and acknowledges the appropriate interrupt type.

## State and Persistence
State lives in `struct snd_sb`: `mode`, `force_mode16`, `locked_rate`, DMA sizes, substream pointers, `open_lock`, `reg_lock`, `mixer_lock`, optional `csp`, and MPU callback fields. There is no persistent storage. The "16-bit DMA Allocation" control changes `force_mode16` only while PCM is idle and disables both DMA channels on change.

## Dependencies and Integration Points
The file depends on ALSA PCM/control APIs, ISA DMA helpers, SB command/ack/mixer helpers, optional CSP UAPI and callbacks, and optional MPU interrupt integration. It is constructed by SB16 card drivers through `snd_sb16dsp_pcm()` and used by compatible drivers through exported PCM ops.

## Risks and Edge Cases
Full duplex is constrained by asymmetric 8-bit and 16-bit DMA channels, and the code contains hardware-specific workarounds for buggy capture/playback transitions. Shared sample-rate locking means simultaneous playback and capture must use the same rate. The interrupt handler always returns `IRQ_HANDLED`, which is normal for non-shared ISA IRQs but can hide spurious signals on shared clone configurations. CSP state writes `chip->open` with CSP mode values, so CSP and PCM open state share a field with care.

## Test Signals
Verify supported format/rate constraints for 8-bit-only, 16-bit, and single-DMA configurations; playback/capture DMA starts only on trigger; pointer callbacks track DMA counters; "16-bit DMA Allocation" rejects changes while streams are active; simultaneous streams lock to one rate; and interrupts produce period elapsed callbacks for both 8-bit and 16-bit modes.
