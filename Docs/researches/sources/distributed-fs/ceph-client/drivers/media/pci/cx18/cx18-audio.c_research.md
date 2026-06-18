<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c

Purpose: Selects cx18 board audio input routing across external muxes, audio control subdevices, and the internal CX23418 audio input mux.

Important APIs/functions: `cx18_audio_set_io()` chooses the current audio input from radio or selected video audio input, routes any external mux subdevice, calls the board's audio control hardware through `cx18_call_hw_err(... audio, s_routing ...)`, and programs `CX18_AUDIO_ENABLE` AI1 mux bits for serial1, serial2, or internal 843/I2S path.

Control flow: When input changes, the function selects the board audio descriptor, routes external devices, then updates the internal register. If the desired mux bits already match, it first toggles to an alternate mux value using `cx18_write_reg_expect()` to force hardware state, then writes the desired value.

State/persistence: Uses `cx->audio_input`, radio flag in `cx->i_flags`, card audio input descriptors, and hardware `CX18_AUDIO_ENABLE` register. No durable state.

Dependencies/integration: Depends on cx18 card tables, V4L2 subdevice audio routing, cx18 MMIO helpers, and constants from the cx18 AV decoder.

Risks: Routing is board-table dependent; wrong `audio_input`/`muxer_input` values produce silence or wrong source. The forced toggle is hardware-specific and must preserve unrelated register bits through masks.

Test signals: TV/radio/line-in audio switching, serial audio source selection, external mux calls, register write-expect success, and no-audio regressions across card variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.c -->
