# sources/distributed-fs/ceph-client/sound/mips/snd-n64.c

Purpose: Implements built-in ALSA playback support for Nintendo 64 audio hardware. It programs AI and MI MMIO registers, uses a private coherent buffer to satisfy AI double-buffering behavior, and exposes one S16_BE stereo playback PCM device.

Important APIs/types/functions: `struct n64audio` stores AI/MI register bases, coherent ring buffer, ALSA card, and channel state. Core functions are `n64audio_push()`, `n64audio_isr()`, `hw_rule_period_size()`, `n64audio_pcm_open()`, `n64audio_pcm_prepare()`, `n64audio_pcm_trigger()`, `n64audio_pcm_pointer()`, `n64audio_probe()`, and `n64audio_init()`.

Control flow: Init uses `platform_driver_probe()` so probe code can be discarded. Probe allocates an ALSA card with private state, allocates a 32 KiB coherent ring buffer, maps MI and AI resources, creates one playback PCM, requests the platform IRQ, and registers the card. Open applies integer periods, even period size, and a custom period-size rule to avoid DMA errata. Prepare sets AI rate/bitclock and resets software pointers. Trigger pushes the first period, enables AI and MI interrupts; the ISR acknowledges AI interrupt, advances position, reports elapsed period, and queues the next period if still running.

State and persistence: State is card-private and not module-unloadable. Channel fields `pos`, `nextpos`, `writesize`, `bufsize`, and `substream` track software copy progress. Hardware state is AI control/rate/bitclock/address/length plus MI interrupt mask.

Dependencies/integration: Depends on platform resources for MI/AI MMIO, coherent DMA under 32-bit/GFP_DMA constraints, ALSA PCM core, and MIPS/N64 platform support. Risks include no remove path, substream pointer races at close/ISR boundaries, reliance on runtime delay as one period, period constraint logic needing to avoid empty intervals, and only NTSC DAC clock support. Test signals are successful built-in probe, accepted hw_params avoiding power-of-two period sizes, correct sample rate register values, continuous period interrupts, and clean stop masking AI interrupts.
