# sources/distributed-fs/ceph-client/sound/hda/common/controller.c

## Purpose
Provides common HD-audio controller logic for ALSA PCM streams, CORB/RIRB command transport, immediate-command fallback, interrupt handling, codec probing/configuration, DSP loader support, and stream object allocation for `struct azx` controllers.

## Important APIs, Types, And Functions
Exports `azx_get_pos_lpib()`, `azx_get_pos_posbuf()`, `azx_get_position()`, `snd_hda_attach_pcm_stream()`, DSP loader helpers under `CONFIG_SND_HDA_DSP_LOADER`, `azx_init_chip()`, `azx_stop_all_streams()`, `azx_stop_chip()`, `azx_interrupt()`, `azx_bus_init()`, `azx_probe_codecs()`, `azx_codec_configure()`, `azx_init_streams()`, and `azx_free_streams()`. Internal PCM ops implement open, close, hw_params, hw_free, prepare, trigger, pointer, and timestamp reporting.

## Control Flow
PCM open takes an HDA PCM ref, serializes through `open_mutex`, assigns an `hdac_stream`, powers the codec, calls codec stream open, and applies hardware constraints. `hw_params` computes buffer/period/BDL state. `prepare` resets and programs the DMA stream, derives the HDA format, adjusts stream tags for quirks, then calls codec prepare. `trigger` groups synchronized substreams, sets SSYNC bits, starts/stops streams under the register lock, clears sync, and initializes the timecounter. The command path sends verbs through CORB/RIRB unless single-command or PIO mode is active; RIRB timeouts progressively switch to polling, disable MSI, reset the bus, or fall back to immediate command mode. IRQ handling services stream interrupts and RIRB responses while avoiding endless active loops.

## State And Persistence Behavior
State lives in `struct azx`, `struct azx_dev`, embedded `hdac_stream`s, bus transport flags, stream tags, runtime PCM private data, polling/MSI/single-command fallback flags, and codec mask/probe state. Hardware persistence is register based: stream descriptors, position buffers, CORB/RIRB state, SSYNC, GTS timestamp registers, and controller init/stop state.

## Dependencies And Integration Points
Depends on ALSA PCM/core, hdac stream and bus helpers, HDA register definitions, runtime PM, tracepoints from `controller_trace.h`, optional x86 ART/TSC crosstimestamps, and codec core entry points in `codec.c`. PCI/platform drivers fill `struct azx` capabilities and ops, then call these helpers during probe, IRQ, suspend, and PCM registration.

## Risks And Test Signals
Risks include stream-tag allocation mistakes, trigger synchronization races, DSP-loader locking conflicts, invalid format generation, RIRB timeout fallback regressions, MSI reset behavior, timestamp rollover handling, and runtime-PM IRQ filtering. Test signals include PCM playback/capture under grouped triggers, period IRQ delivery, `trace_azx_*` events, codec probe logs, fallback mode warnings, suspend/resume audio continuity, and crosstimestamp validation on GTS-capable x86 hardware.
