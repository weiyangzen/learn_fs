## sources/distributed-fs/ceph-client/sound/hda/core/stream.c

Purpose: implements HD-audio stream lifecycle, DMA buffer descriptor programming, synchronization, timestamps, SPIB/DRSM helpers, and optional DSP firmware loading streams.

Important APIs, types, and functions: `snd_hdac_stream_init()`, `snd_hdac_stream_assign()`, `snd_hdac_stream_release()`, `snd_hdac_stream_reset()`, `snd_hdac_stream_setup()`, `snd_hdac_stream_set_params()`, `snd_hdac_stream_setup_periods()`, `snd_hdac_stream_start()`, `snd_hdac_stream_stop()`, `snd_hdac_stream_sync()`, `snd_hdac_stream_timecounter_init()`, SPIB/DRSM setters, and `snd_hdac_dsp_prepare()/trigger()/cleanup()` under `CONFIG_SND_HDA_DSP_LOADER`.

Control flow: streams move from unused to opened, prepared, running, stopped, cleaned, and released. Setup clears/reset registers, writes tag, buffer length, format, LVI, BDL addresses, position buffer, interrupts, FIFO size, and timing thresholds. BDL creation splits periods into hardware descriptors, including position-adjustment and 4K alignment quirks. Start/stop toggle interrupts and DMA start bits.

State and persistence: per-stream state includes opened/running/locked flags, assigned key, substream/compress stream, BDL DMA area, buffer and period sizes, format, stream tag, wallclock counters, SPIB/DRSM addresses, and cached thresholds. Bus-level locks protect assignment and DSP locks protect firmware loading.

Dependencies and integration points: used by HDA PCM and compressed paths, DSP loader, tracepoints, clocksource/timecounter, DMA helpers, and HDA controller register accessors.

Risks: descriptor count overflow, period adjustment greater than period size, register access-width quirks, and delayed RUN-bit clearing can break DMA. DSP loading must avoid races with normal PCM streams. Timestamp math assumes 24 MHz WALLCLK.

Test signals: run playback/capture across rates, channels, no-period-wakeup, SG buffers, 4K-aligned controllers, suspend/resume, synchronized multi-stream trigger, compressed streams, and DSP firmware loading; monitor tracepoints and underrun behavior.
