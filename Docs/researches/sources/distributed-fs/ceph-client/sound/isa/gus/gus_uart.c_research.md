<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c

Purpose: ALSA RawMIDI driver for the GF1 MIDI UART, modeled like a 6850 UART.

Important APIs/types/functions: exported `snd_gf1_rawmidi_new()`, `snd_gf1_uart_suspend()`, and `snd_gf1_uart_resume()`. RawMIDI ops implement input/output open, close, and trigger. IRQ callbacks are `snd_gf1_interrupt_midi_in()` and `snd_gf1_interrupt_midi_out()`.

Control flow: creating rawmidi registers one input and one output substream and stores the GUS card as private data. Open resets UART if needed, installs IRQ handlers, and stores active substream pointers. Input trigger toggles Rx IRQ bit; output trigger sends an initial byte when FIFO is free and enables Tx IRQ. IRQ handlers drain received bytes, report errors, transmit queued bytes, or disable Tx IRQ when empty. Close resets UART if the opposite side is inactive and restores default handlers.

State and persistence: `gus->gf1.uart_cmd`, framing/overrun counters, substream pointers, and handler callbacks are volatile. Suspend writes reset; resume restores handlers, clears pending input, and restores saved command when a substream remains active.

Dependencies and integration: main IRQ dispatcher invokes MIDI handlers. Board drivers call `snd_gf1_rawmidi_new()` when MIDI is supported/enabled. Depends on ALSA RawMIDI and low-level UART inline helpers.

Risks: receive handler reads a status/data byte pair and uses a bounded spin loop; unexpected FIFO behavior can drop bytes. Output trigger briefly unlocks to wait for Rx empty. Test signals include full-duplex MIDI, trigger start/stop, overrun/framing counters, close while other direction active, and suspend/resume with open substreams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c -->
