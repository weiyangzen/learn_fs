# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.c

Purpose: core PCI/ALSA driver for the CS5535/CS5536 companion audio function. It wires PCI resources, AC97 codec access, IRQ handling, mixer creation, PCM creation, and ALSA card registration.

Important APIs and types: `snd_cs5535audio_ids` matches NS CS5535 and AMD CS5536 audio. `snd_cs5535audio_codec_read/write` implement memory-mapped AC97 command/status transactions. `snd_cs5535audio_mixer` creates the ALSA AC97 bus/mixer and applies generic plus OLPC quirks. `snd_cs5535audio_interrupt`, `process_bm0_irq`, and `process_bm1_irq` dispatch bus-master playback/capture period interrupts. `snd_cs5535audio_create` owns PCI enable, DMA mask, region request, IRQ request, and bus mastering.

Control flow: probe allocates a devm ALSA card, sets `private_free`, creates hardware resources, initializes AC97 mixer, creates PCM via `snd_cs5535audio_pcm`, names/registers the card, and stores drvdata. Codec read/write submit commands to `ACC_CODEC_CNTL`, wait for `CMD_NEW` to clear, and for reads poll `ACC_CODEC_STATUS` until `STS_NEW` matches the requested register.

State and persistence: `struct cs5535audio` stores card, AC97, PCM, IRQ, PCI, I/O port, register spinlock, substream pointers, and playback/capture DMA state. Hardware state is in BAR0 registers; AC97 mixer state is managed by ALSA. No on-disk persistence.

Dependencies and integration: depends on Linux PCI, IRQ, I/O port access, ALSA core/control/PCM/AC97, and `cs5535audio_pcm.c`. Optional `cs5535audio_olpc.c` extends AC97 capabilities and controls.

Risks and test signals: timeout-only AC97 transactions can leave stale values; `process_bm0_irq` assumes `playback_substream` is valid when EOP arrives; unexpected BM1 IRQs are silently ignored if not EOP. Tests: probe/remove, AC97 read/write timeout behavior, playback/capture period interrupts, shared IRQ returning `IRQ_NONE` when status is zero, and card registration with both supported PCI IDs.
