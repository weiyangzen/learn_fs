<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c

Purpose: ALSA ISA driver for Gravis UltraSound MAX, combining GF1 synth with an onboard WSS/CS4231-compatible codec and shared IRQ/DMA routing.

Important APIs/types/functions: `struct snd_gusmax` stores card, GUS, WSS, IRQ, and status registers. Key routines are `snd_gusmax_detect()`, `snd_gusmax_interrupt()`, `snd_gusmax_init()`, `snd_gusmax_mixer()`, `snd_gusmax_probe()`, and PM callbacks.

Control flow: probe allocates card private data, auto-selects IRQ/DMAs/port if needed, calls `snd_gus_create()` with negative IRQ to avoid common IRQ request, validates GF1 reset, initializes MAX routing latch, runs common GUS init, requires `max_flag`, requests a combined IRQ, creates WSS codec with shared IRQ/DMA flags at `port + 0x10c`, registers WSS PCM/mixer/timer, optional GF1 PCM, renames mixer controls for synth/CD routing, creates GF1 rawmidi, builds longname, and registers the card.

State and persistence: `max_cntrl_val` in `gus` preserves routing latch value for resume. `snd_gusmax_interrupt()` dispatches shared IRQs by polling GF1 and WSS status ports. `struct snd_gusmax` stores GUS/WSS pointers after successful registration.

Dependencies and integration: shared GUS library, ALSA WSS, ISA IRQ/DMA, and legacy resource auto-probe.

Risks: shared interrupt dispatch depends on correct status registers and bounded polling. Negative IRQ handoff between common creation and board IRQ request is subtle. Test signals include WSS playback/capture, GF1 synth PCM/rawmidi, shared IRQ activity for both chips, mixer renames, routing latch restore on resume, and cleanup on failed WSS creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c -->
