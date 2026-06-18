# sources/distributed-fs/ceph-client/sound/pci/lola/lola.c

## Purpose
This is the core PCI, codec-command, interrupt, and probe implementation for the Digigram Lola PCIe ALSA driver. It initializes BAR0/BAR1, implements an HD-audio-like CORB/RIRB command transport, parses the card widget tree, and wires PCM/mixer/debug helpers into an ALSA card.

## Important APIs, Types, and Functions
Module parameters provide ALSA card index/id/enable plus Lola-specific `granularity` and `sample_rate_min`. `corb_send_verb()`, `lola_codec_write()`, `lola_codec_read()`, and `lola_codec_flush()` are the exported codec verb transport used by clock, PCM, mixer, and proc code. `lola_update_rirb()` consumes responses and unsolicited clock events. `lola_interrupt()` handles stream, controller, FIFO, and microcontroller interrupts. `reset_controller()`, `setup_corb_rirb()`, `lola_irq_enable()`, and `lola_parse_tree()` form the hardware bring-up path.

## Control Flow
`lola_probe()` delegates to `__lola_probe()` through `snd_card_free_on_error()`. Probe creates the card, calls `lola_create()` for PCI enable, BAR mapping, reset, IRQ request, stream count discovery, CORB/RIRB allocation, and IRQ enablement. Then `lola_parse_tree()` validates Digigram vendor/function IDs, discovers capture/playback widgets, pins, clock, and mixer, enables clock events, and restores setup after warm reset. Finally it creates PCM devices, mixer controls, optional debug proc files, and registers the card.

## State and Persistence
`struct lola` stores register locks, CORB/RIRB buffers and pointers, pending command count, last command/debug responses, stream arrays, pin/clock/mixer metadata, sample-rate constraints, granularity, cold-reset status, and polling fallback state. There is no disk persistence. Runtime state is hardware-resident in BAR registers and firmware widget state, with driver shadows used for restoration.

## Dependencies and Integration Points
This file is the hub for Linux PCI managed resources, ALSA card lifecycle, IRQs, DMA ring buffers, the other Lola source files through `lola.h`, and Digigram PCI ID `0x0001`. The CORB/RIRB helpers are the integration contract used by `lola_clock.c`, `lola_mixer.c`, `lola_pcm.c`, and `lola_proc.c`.

## Risks
CORB/RIRB command completion is serialized with `reg_lock` and a command count; lost RIRB interrupts switch to polling, which is useful but can hide IRQ failures. `lola_create()` enables interrupts before full widget parsing, so partial initialization must unwind through managed resources. Stream-count and widget-count values are hardware-provided and must stay bounded by `MAX_*` constants. Warm-reset restoration replays mixer/clock/granularity state and can fail if helpers assume fully initialized widgets.

## Test Signals
Probe should log valid stream counts and vendor/function IDs, then register an ALSA card named Digigram Lola. Codec verb reads should not time out or set `LOLA_RIRB_EX_ERROR`. Interrupt tests should show period elapsed callbacks for input/output streams and no repeated FIFO/microcontroller error bits. Warm reboot or driver reload should preserve functional clock, gain, SRC, and stream setup.
