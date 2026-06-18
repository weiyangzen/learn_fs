# sources/distributed-fs/ceph-client/sound/sparc/dbri.c

## Purpose
This file is the ALSA SBus driver for Sun DBRI audio hardware paired with a CS4215 multimedia codec. It programs the DBRI command queue, interrupt queue, CHI time-slot fabric, data pipes, and DMA descriptors, then exposes the CS4215 as one full-duplex ALSA PCM plus mixer controls and proc diagnostics.

## Important APIs, types, and functions
`struct snd_dbri` owns the mapped DBRI registers, coherent `struct dbri_dma` command/interrupt/descriptor block, command pointer and lock, interrupt queue cursor, 32 pipe records, descriptor links, CS4215 state, and playback/capture `dbri_streaminfo`. `struct dbri_pipe` tracks each DBRI pipe's SDP word, time-slot linkage, active descriptor, descriptor ring head, and fixed-data receive target. `struct cs4215` stores data/control time-slot images, codec status/version, detected onboard/speakerbox selection, frame offset, precision, and channels.

DBRI command synchronization is handled by `dbri_cmdlock`, `dbri_cmdsend`, `dbri_cmdwait`, `dbri_reset`, and `dbri_initialize`. Pipe and time-slot setup flows through `setup_pipe`, `reset_pipe`, `link_time_slot`, `xmit_fixed`, `recv_fixed`, `setup_descs`, and `xmit_descs`. CS4215 control is implemented by `cs4215_setup_pipes`, `cs4215_init_data`, `cs4215_setdata`, `cs4215_setctrl`, `cs4215_open`, `cs4215_prepare`, and `cs4215_init`. ALSA callbacks are collected in `snd_dbri_ops`.

## Control flow
`dbri_probe` allocates an ALSA card, maps the SBus resource, allocates the coherent command/interrupt/descriptor block, requests the shared IRQ, initializes DBRI, probes/configures CS4215, then creates PCM, mixer, proc entries, and registers the card. `dbri_initialize` resets DBRI, initializes pipe state, sets the circular interrupt queue, writes the first command pointer to register 8, and waits for completion.

The CS4215 probe detects onboard versus speakerbox codec through PIO bits, creates fixed and memory pipes for control/data modes, enables fixed receive for status/version slots, sends control mode frames, then leaves the codec in data mode. PCM open initializes per-stream state, installs format/channel constraints, and opens CS4215 data mode. `hw_params` programs CS4215 rate/format/channels and maps the ALSA runtime buffer for DBRI DMA. `prepare` selects pipe 4 for playback or pipe 6 for capture, builds a descriptor ring split by period and DBRI maximum descriptor size, and resets the stream offset. `trigger START` submits descriptor rings with SDP commands; `STOP` clears the pipe.

Interrupts read DBRI register 1 to acknowledge and detect SBus errors, then drain nonzero words from the circular interrupt buffer. Buffer-ready interrupts advance receive descriptors and call `snd_pcm_period_elapsed`; transmit-complete and marker interrupts walk completed transmit descriptors, reset status, update offsets, and notify ALSA. Fixed-data-change interrupts reverse bit order if needed and update CS4215 status/version memory.

## State and persistence behavior
There is no filesystem persistence. Device-visible state lives in the coherent `dbri_dma` block and hardware registers. Host state tracks a circular command buffer terminated by WAIT/JUMP pairs, an interrupt queue pointer, descriptor rings, pipe linkages, CS4215 register images, and ALSA stream offsets. Mixer controls update cached CS4215 data/control bytes and send fixed CHI data, muting briefly before changes to reduce clicks. Runtime DMA mappings are established in `hw_params` and released in `hw_free`.

## Dependencies and integration points
The driver depends on SPARC SBus register access, Open Firmware platform resources, DMA mapping APIs, ALSA card/PCM/control/proc APIs, and MIDI-independent CS4215 audio formatting knowledge. It integrates with `SNDRV_DMA_TYPE_CONTINUOUS` buffers, shared IRQ handling, and `/proc/asound` diagnostics. The code is specific to DBRI+CS4215 timing, PIO wiring, and CHI frame layout.

## Risks and edge cases
Command queue wrapping and DBRI reread semantics are subtle; wrong command lengths or locking can corrupt the queue. Descriptor accounting mixes descriptor byte counts, period sizes, and `runtime->buffer_size`; DMA unmap uses frame count as a byte length, which is a risk to audit. `snd_cs4215_put_single` computes `changed` after overwriting cached bytes, so change reporting can be wrong. CS4215 mode switching relies on microsecond delays and fixed offsets, with a known limitation for 8-bit stereo. Interrupt handlers drop and reacquire `dbri->lock` around ALSA callbacks, so close/stop races need care. Underrun recovery is mostly a FIXME.

## Test signals
Test probe on DBRIe/DBRIf nodes with onboard and speakerbox codecs, successful CS4215 version detection, playback/capture for supported rates and formats, constraints forcing stereo to S16_BE, descriptor ring wrap without pointer jumps, period interrupts on both directions, mixer volume/switch updates with audible changes, proc `regs` output, clean remove, and behavior under underrun/SBus error logs. Fault injection around DMA allocation, register mapping, IRQ request, and CS4215 no-response paths is valuable.
