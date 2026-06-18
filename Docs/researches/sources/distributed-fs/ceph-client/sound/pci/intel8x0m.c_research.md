# sources/distributed-fs/ceph-client/sound/pci/intel8x0m.c

## Purpose
`intel8x0m.c` is the ALSA modem-class PCI driver for Intel ICH-family AC'97 modem controllers and compatible SiS/NVIDIA/AMD variants. It is derived from the audio driver but narrows the implementation to modem in/out streams and modem AC97 codec handling.

## Important APIs, Types, and Functions
- `struct ichdev` stores one modem DMA stream's BDL, buffer geometry, indices, interrupt mask, and attached modem AC97 codec.
- `struct intel8x0m` stores PCI/card/MMIO/IRQ state, two modem streams, AC97 bus/codec, descriptor pages, lock, interrupt masks, and position shift.
- `snd_intel8x0m_codec_{semaphore,read,write}()` implement AC97 register access with ready and semaphore checks.
- `snd_intel8x0m_setup_periods()`, `snd_intel8x0m_update()`, and `snd_intel8x0m_interrupt()` manage BDL programming, period advancement, and IRQ dispatch.
- `snd_intel8x0m_pcm_prepare()` writes modem line rate/level AC97 registers and sets up DMA.
- `snd_intel8x0m_mixer()` creates an AC97 bus with `AC97_SCAP_SKIP_AUDIO`, selects primary or secondary codec, and binds modem codecs to both streams.
- `snd_intel8x0m_chip_init()`, PM callbacks, proc helpers, and `__snd_intel8x0m_probe()` implement lifecycle.

## Control Flow
Probe creates the ALSA card, names it as an ICH modem, maps PCI regions, initializes two BDL streams for modem input/output, resets AC-link and DMA registers, requests IRQ, creates the AC97 modem mixer, creates one modem PCM device, registers proc diagnostics, and registers the card. PCM open constrains rates to 8000/9600/12000/16000 Hz mono S16. Prepare programs AC97 line rate and line level, then fills the BDL. Trigger starts/stops DMA. IRQ handling advances the matching modem stream ring and calls `snd_pcm_period_elapsed()`.

## State and Persistence
Runtime state is held in `struct intel8x0m`, two `ichdev` entries, descriptor pages, and the AC97 codec object. The driver has no persistent storage; module parameters select card index/id and optional AC97 clock. Resume rebuilds controller state and resumes the AC97 codec.

## Dependencies and Integration Points
The driver integrates with Linux PCI, ALSA card/PCM, AC97 modem codec support, IRQ, DMA, PM, and proc info. Its PCM device is marked `SNDRV_PCM_CLASS_MODEM`, which helps userspace distinguish it from audio PCM devices.

## Risks and Test Signals
Risks include assumptions that modem is only primary or secondary, no ALi path despite dormant code, spinlock release/reacquire around `snd_pcm_period_elapsed()`, busy waits on stop, and limited rate constraints. Test signals include successful detection of modem AC97 codec, one modem PCM with capture/playback, valid low-rate mono operation, period interrupts, suspend/resume, and proc reporting of codec-ready bits.
