# sources/distributed-fs/ceph-client/sound/pci/lola/lola_pcm.c

## Purpose
This file implements Lola PCM stream discovery, ALSA PCM device creation, buffer descriptor programming, stream reset/prepare/trigger/pointer operations, and period notification handling.

## Important APIs, Types, and Functions
`lola_init_pcm()` and `lola_init_stream()` parse audio widget NIDs into `struct lola_stream`, determine DSD indices, validate widget caps, detect float support, and mark digital capture SRC capability. `lola_create_pcm()` allocates BDL DMA pages, creates a PCM with one substream per hardware stream, installs `lola_pcm_ops`, and preallocates SG buffers. Runtime operations include `lola_pcm_open/close`, `lola_pcm_hw_params/free`, `lola_pcm_prepare`, `lola_pcm_trigger`, `lola_pcm_pointer`, and IRQ helper `lola_pcm_update()`. Low-level helpers program BDL entries, stream formats, channel stream IDs, DSD registers, and synchronized timestamps.

## Control Flow
Open reserves a stream, constrains rate to either the locked card sample rate or min/max module settings, and constrains buffer/period sizes to granularity. Prepare resets prior state, reserves adjacent streams for multichannel use, builds BDL entries, selects sample rate, configures codec stream/channel IDs, writes DSD BDL/LVI/control registers, and waits for FIFO readiness. Trigger starts or stops all linked streams with a common LRC-based timestamp when needed. Interrupt handling in `lola.c` calls `lola_pcm_update()` to deliver `snd_pcm_period_elapsed()`.

## State and Persistence
Each `lola_stream` tracks NID, stream index, DSD index, substream pointer, master stream for multichannel, buffer size, period bytes, BDL fragment count, format verb, and opened/prepared/paused/running flags. `chip->sample_rate` is a card-wide lock released when the last stream closes via `ref_count_rate`.

## Dependencies and Integration Points
This file depends on BAR1 DSD register helpers, codec verbs for stream format/channel assignment, clock selection in `lola_clock.c`, PCM structures in ALSA, and IRQ status routing from `lola_interrupt()`.

## Risks
Multichannel playback/capture consumes adjacent hardware streams; inadequate cleanup can leave slave streams marked opened. BDL setup allows only eight entries and can fail for fragmented SG periods. Sample rate is locked globally while any stream is open, so close/refcount bugs can block later rates. Trigger synchronization depends on LRC/granularity math and linked-stream grouping. FIFO waits time out after 200 ms and should be treated as hardware/firmware failures.

## Test Signals
Open should reject reopening the same hardware stream and constrain channel counts to remaining streams. Prepare should fail cleanly when channels exceed available streams or BDL entries exceed limits. Linked playback/capture streams should start sample-synchronously. Pointer movement should match DSD LPIB and wrap at buffer size. IRQ period notifications should arrive once per completed BDL fragment and stop after trigger stop/hw_free.
