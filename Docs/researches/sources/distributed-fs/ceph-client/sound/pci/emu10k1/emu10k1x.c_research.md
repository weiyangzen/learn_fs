# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1x.c

## Purpose

This file is a complete ALSA PCI driver for Creative's Dell OEM EMU10K1X device (`PCI_VDEVICE(CREATIVE, 0x0006)`). It is separate from the larger EMU10K1/Audigy driver because the EMU10K1X has a simpler register model: three playback DMA channels, one capture DMA channel, AC97 codec access, S/PDIF routing/status controls, a `/proc` register debug interface, and one MPU-401 UART raw-MIDI port. The driver exposes three stereo playback PCM devices for front, rear, and center/LFE, plus capture on device 0.

## Important APIs, types, and functions

The main private state is `struct emu10k1x`, which holds the ALSA card, PCI device, I/O base, IRQ, AC97 pointer, PCM pointer, three playback `voices`, one `capture_voice`, cached `spdif_bits[3]`, a small DMA page used for playback period descriptor lists, and embedded MIDI state. `struct emu10k1x_voice` links hardware channel numbers to `struct emu10k1x_pcm`, while `struct emu10k1x_midi` stores rawmidi substreams, locks, interrupt bits, port offsets, and the dispatch callback.

Register helpers `snd_emu10k1x_ptr_read`, `snd_emu10k1x_ptr_write`, `snd_emu10k1x_intr_enable`, `snd_emu10k1x_intr_disable`, and `snd_emu10k1x_gpio_write` serialize MMIO/indexed register access with `emu_lock`. PCM operations are split into playback (`snd_emu10k1x_playback_open`, `snd_emu10k1x_pcm_hw_params`, `snd_emu10k1x_pcm_prepare`, `snd_emu10k1x_pcm_trigger`, `snd_emu10k1x_pcm_pointer`) and capture (`snd_emu10k1x_pcm_open_capture`, `snd_emu10k1x_pcm_hw_params_capture`, `snd_emu10k1x_pcm_prepare_capture`, `snd_emu10k1x_pcm_trigger_capture`, `snd_emu10k1x_pcm_pointer_capture`). Codec callbacks `snd_emu10k1x_ac97_read` and `snd_emu10k1x_ac97_write` implement the `snd_ac97_bus_ops`.

Top-level setup flows through `snd_emu10k1x_probe`, `__snd_emu10k1x_probe`, and `snd_emu10k1x_create`. `snd_emu10k1x_pcm` creates the ALSA PCM devices and channel maps. `snd_emu10k1x_mixer` installs IEC958 and analog/digital jack controls. `emu10k1x_midi_init` and `snd_emu10k1x_midi` register the rawmidi device. `snd_emu10k1x_interrupt` is the shared IRQ handler for PCM and MIDI events.

## Control Flow

Probe checks the module card slot, allocates an ALSA card with private `struct emu10k1x`, enables PCI, applies a 28-bit coherent DMA mask, requests BARs and the shared IRQ, allocates a 4 KiB descriptor page, initializes playback voices, programs default S/PDIF channel status words, selects analog routing/GPIO defaults, enables audio in `HCFG`, then creates PCM, AC97, mixer, MIDI, and proc entries before registering the card.

Playback open constrains period count to an integer and period bytes to a 64-byte step, allocates per-substream `struct emu10k1x_pcm`, and assigns fixed hardware capabilities: S16_LE, 48 kHz, stereo, up to 32 KiB buffer and 2 to 8 periods. `hw_params` binds the ALSA substream to `voices[pcm->device]`. `prepare` writes one 8-byte DMA list entry per period into the shared descriptor page at `1024 * voice`, then programs `PLAYBACK_LIST_ADDR`, `PLAYBACK_LIST_SIZE`, `PLAYBACK_LIST_PTR`, `PLAYBACK_POINTER`, `PLAYBACK_DMA_ADDR`, and `PLAYBACK_PERIOD_SIZE`. `trigger` enables loop or loop+half-loop interrupts depending on period count and sets the matching `TRIGGER_CHANNEL_*` bit; stop clears the bit and disables interrupts. `pointer` combines `PLAYBACK_LIST_PTR` with `PLAYBACK_POINTER`, rereading if the list pointer changed mid-sample, and wraps at the ALSA buffer size.

Capture open has the same format/rate constraints but fixes periods to 2. Only one capture voice exists, so `hw_params_capture` returns `-EBUSY` when already in use. Capture prepare programs `CAPTURE_DMA_ADDR`, `CAPTURE_BUFFER_SIZE`, `CAPTURE_POINTER`, and `CAPTURE_UNKNOWN`. Capture trigger toggles `TRIGGER_CAPTURE` and capture loop/half-loop interrupts. Capture pointer reads `CAPTURE_POINTER` and wraps to buffer frames.

The IRQ handler reads `IPR`, returns `IRQ_NONE` if no bit is pending, dispatches capture and playback period notifications through `snd_pcm_period_elapsed`, disables stale interrupts when no voice is active, calls the MIDI interrupt callback for TX/RX bits, then acknowledges by writing the original status back to `IPR`.

## State and Persistence Behavior

Runtime state is kept in the ALSA card private area and is reset on driver bind/unbind. PCM stream state lives in per-open `runtime->private_data`; voice ownership is recorded by `voice->use` and `voice->epcm`. The playback period descriptor page is device DMA memory allocated for the card lifetime. S/PDIF channel status is cached in `emu->spdif_bits[]` and mirrored to `SPCS0..2`; analog/digital output mode is represented directly by hardware `SPDIF_SELECT`, `ROUTING`, and `GPIO` values. MIDI open/close maintains `midi_mode`, substream pointers, and interrupt enable state. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Linux PCI, IRQ, DMA, and I/O port APIs plus ALSA core, PCM, AC97, rawmidi, control, channel-map, and proc-info APIs. It registers as a normal `pci_driver` via `module_pci_driver`. User-space integration is through ALSA PCM devices, AC97 mixer controls, IEC958 controls, rawmidi, and `/proc/asound/.../emu10k1x_regs`. The AC97 layer supplies most analog mixer controls; this file adds EMU10K1X-specific S/PDIF and routing controls.

## Risks

Hardware register programming is mostly undocumented, with `PLAYBACK_UNKNOWN*`, `CAPTURE_UNKNOWN`, `ROUTING`, and GPIO values encoded as magic constants. The playback pointer calculation depends on stable ordering between `PLAYBACK_LIST_PTR` and `PLAYBACK_POINTER` and may be sensitive to races around period rollover. Playback voice allocation for devices 0 to 2 lacks an explicit busy check comparable to capture; correctness depends on ALSA open semantics and device/substream topology. The proc register writer allows privileged proc users to poke indexed registers directly, which is useful for debugging but risky on live hardware. MIDI command paths busy-wait for ACKs under locks and report failure as `1` internally before callers map it to `-EIO`.

## Test Signals

Useful signals are successful module probe on the Dell SB0200/EMU10K1X PCI ID, ALSA card registration, clean interrupt handling with shared IRQs, `aplay` on all three playback devices, `arecord` on device 0, period elapsed timing at two-period and multi-period settings, XRUN-free pointer progression, AC97 mixer enumeration, analog/digital output switching, IEC958 status read/write round trips, rawmidi duplex loopback or hardware MIDI traffic, suspend/unbind cleanup that stops audio and interrupts, and manual proc register read coverage.
