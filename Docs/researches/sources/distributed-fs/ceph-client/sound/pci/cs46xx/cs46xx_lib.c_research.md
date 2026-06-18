# sources/distributed-fs/ceph-client/sound/pci/cs46xx/cs46xx_lib.c

## Purpose
`cs46xx_lib.c` is the main ALSA support library for Cirrus Logic CS461x/CS46xx cards. It owns PCI resource mapping, chip initialization, AC97 access, firmware loading, DSP startup, PCM devices, mixer controls, raw MIDI, optional gameport/proc interfaces, board-specific amplifier/CLKRUN quirks, interrupt handling, power management, and final card teardown. It supports both the legacy monolithic BA1 firmware path and the `CONFIG_SND_CS46XX_NEW_DSP` modular SPOS path.

## Important APIs and functions
Exported or externally called entry points include `snd_cs46xx_create()`, `snd_cs46xx_start_dsp()`, `snd_cs46xx_pcm()`, `snd_cs46xx_pcm_rear()`, `snd_cs46xx_pcm_center_lfe()`, `snd_cs46xx_pcm_iec958()`, `snd_cs46xx_mixer()`, `snd_cs46xx_midi()`, `snd_cs46xx_gameport()`, `snd_cs46xx_download()`, and, for the new DSP path, `snd_cs46xx_clear_BA1()`. Internal pillars include AC97 read/write helpers, firmware parsers, reset/start/stop helpers, sample-rate calculators, PCM open/prepare/hw_params/trigger/pointer methods, mixer control callbacks, MIDI triggers, procfs IO mapping, card quirk handlers, suspend/resume, and IRQ demux.

## Control flow
Probe code in `cs46xx.c` calls `snd_cs46xx_create()` to enable PCI, request regions, map BA0/BA1 windows, install IRQ, create a SPOS instance when configured, initialize the chip, and register proc entries. Later `snd_cs46xx_mixer()` creates AC97 bus/codecs and mixer controls, PCM helper functions create ALSA devices, and `snd_cs46xx_start_dsp()` resets the processor, loads firmware, initializes SCBs/tasks for the new DSP path or downloads the legacy image, starts the processor, and enables stream interrupts. PCM trigger paths link/unlink DSP PCM SCBs for playback and toggle capture DMA. The interrupt handler clears device IRQ state, reports PCM period elapsed events, services MIDI RX/TX, and re-enables PCI interrupts.

## State and persistence behavior
State lives in `struct snd_cs46xx`: mapped memory regions, AC97 bus/codecs, IRQ, PCM and capture buffers, mixer callbacks, active/amplifier counters, MIDI state, DSP modules, SPOS instance, saved PM registers, and optional gameport. Runtime DMA buffers are allocated per open or preallocated for devices. Suspend saves selected registers, suspends AC97, powers down amplifier and hardware; resume reinitializes the chip, reloads DSP/firmware state, restores registers, AC97, sample rates, proc start, IRQs, and amplifier state.

## Dependencies and integration points
The file integrates heavily with ALSA core, PCM, control, rawmidi, AC97, procfs, Linux PCI, firmware loader, IRQ, PM, gameport, and MMIO APIs. It includes `cs46xx.h`, `cs46xx_lib.h`, and `dsp_spos.h`; new DSP behavior depends on `dsp_spos.c` and `dsp_spos_scb_lib.c` for SCB graph management.

## Risks
Risk clusters are hardware timing loops, unchecked firmware format assumptions, fragile magic constants for SPDIF/AC97/board quirks, race-sensitive register access split between `reg_lock` and `spos_mutex`, and the dual legacy/new DSP compile-time paths. Some known bugs are documented in the file, especially SPDIF input desynchronization and Hercules amplifier glitches. PCM paths switch ops dynamically based on period count, so buffer ownership must remain exact.

## Test signals
High-value tests are device probe/remove, firmware load failures, AC97 primary/secondary detection, playback/capture at varied rates/formats/period counts, indirect-buffer transfers, MIDI duplex operation, mixer control get/put behavior, SPDIF output/input toggles and IEC958 status updates, interrupt period accounting, board quirk paths, procfs reads, and suspend/resume with active PCM/SPDIF states.
