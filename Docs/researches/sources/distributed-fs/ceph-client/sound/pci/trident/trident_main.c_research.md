# sources/distributed-fs/ceph-client/sound/pci/trident/trident_main.c

## Purpose
This is the shared hardware engine for Trident 4DWave DX/NX and SiS SI7018. It implements AC97 access, hardware initialization, voice allocation and register programming, ALSA PCM operations for playback/capture/foldback/S/PDIF, mixer and IEC958 controls, optional gameport support, `/proc` diagnostics, interrupt handling, and suspend/resume.

## Important APIs, types, and functions
External entry points include `snd_trident_create()`, `snd_trident_pcm()`, `snd_trident_foldback_pcm()`, `snd_trident_spdif_pcm()`, `snd_trident_alloc_voice()`, `snd_trident_free_voice()`, `snd_trident_start_voice()`, `snd_trident_stop_voice()`, and `snd_trident_write_voice_regs()`. AC97 ops are `snd_trident_codec_read()` and `snd_trident_codec_write()`, with device-specific register paths for DX, NX, and SI7018. Voice programming helpers write CSO, ESO, volume, pan, reverb, chorus, and full register sets.

PCM implementation includes memory allocation (`snd_trident_allocate_pcm_mem()`), extra interrupt voice allocation (`snd_trident_allocate_evoice()`), prepare callbacks for playback, legacy capture, SI7018 capture, foldback, and S/PDIF, the shared `snd_trident_trigger()`, and pointer callbacks. Mixer logic includes wave/music volume controls, per-PCM front/pan/reverb/chorus controls, S/PDIF default/mask/stream/switch controls, and NX rear-path control.

## Control flow
`snd_trident_create()` enables PCI, sets a 30-bit DMA mask, initializes locks and stream limits, requests regions and IRQ, allocates NX TLB state when needed, initializes S/PDIF defaults, runs the per-device hardware init, creates mixers, initializes the 64 voice objects and PCM mixer defaults, enables ESO/MIDLP interrupts, and creates proc diagnostics.

PCM open allocates a bank-B PCM voice and stores it in `runtime->private_data`. Playback prepare computes rate delta and spurious IRQ threshold, selects either TLB offset or DMA address, fills voice registers, and optionally prepares an extra muted voice as a period interrupt generator when the buffer is not exactly two periods. Legacy capture configures legacy DMA registers and uses a PCM voice to generate synchronized period interrupts. SI7018 capture uses voice attributes and optional extra voice instead of legacy DMA. Foldback routes a mixer capture channel through `T4D_RCI`. S/PDIF uses NX hardware S/PDIF registers on NX and SI serial/S/PDIF registers on SI7018.

The shared trigger walks ALSA synchronized stream groups, collects voice masks, toggles running state, starts/stops voices, enables/disables bank-B interrupts, updates S/PDIF registers, and starts/stops legacy capture DMA for non-SI capture. The IRQ handler filters `ADDRESS_IRQ` and `MPU401_IRQ`, reads bank interrupt status, drops spurious interrupts based on the sample timer threshold, adjusts sync voices when needed, calls `snd_pcm_period_elapsed()` outside the register lock, acknowledges interrupts, and delegates MPU-401 IRQs.

## State and persistence behavior
Persistent runtime state lives in `struct snd_trident`: AC97 handles, TLB table, voice maps, PCM mixer settings, S/PDIF bits, music/wave volume, spurious IRQ counters, and per-device flags. Per-voice state mirrors hardware register values and ALSA stream ownership. Suspend marks `in_suspend`, changes power state, and suspends AC97 codecs. Resume reruns per-device init, resumes codecs, restores music/wave volume, reenables ESO interrupts, and clears `in_suspend`; it does not restore each active PCM voice directly, relying on ALSA suspend semantics.

## Dependencies and integration points
This file depends on ALSA core, PCM, control, TLV, info, AC97, raw MIDI integration from the wrapper, Linux PCI/IRQ/I/O, optional gameport, and `trident_memory.c` for NX virtual memory. It provides module-internal services consumed by `trident.c` and TLB allocation services consumed during PCM hw_params.

## Risks and test signals
Risks include variant-specific register programming, complex extra-voice synchronization, spurious interrupt heuristics, legacy capture DMA setup, inconsistent S/PDIF hardware differences, TLB versus physical DMA address paths, and lock handoff around `snd_pcm_period_elapsed()`. There is a likely naming/assignment bug in `snd_trident_spdif_open()`: SI7018 selects `snd_trident_spdif` while non-SI selects `snd_trident_spdif_7018`, which appears reversed by the hardware definitions. Test signals include full probe on DX/NX/SI7018, playback across many period layouts, capture on DX/NX and SI7018, foldback channel naming and capture, S/PDIF control activation while stream is open, MIDI IRQ delivery, gameport raw/cooked reads, no spurious IRQ floods, TLB allocation/free under repeated hw_params changes, and suspend/resume followed by mixer and PCM reuse.
