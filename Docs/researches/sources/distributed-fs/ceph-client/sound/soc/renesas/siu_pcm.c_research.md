# sources/distributed-fs/ceph-client/sound/soc/renesas/siu_pcm.c

Purpose: PCM platform/component side of the Renesas SIU driver. It allocates DMA channels, schedules one-period DMA transfers through a high-priority workqueue, toggles SIU FIFOs, reports ALSA pointer/period progress, and creates/free SIU port state.

Important APIs, types, and functions: Global `siu_ports` stores per-port state. Stream start/stop helpers are `siu_pcm_stmwrite_start/stop` and `siu_pcm_stmread_start/stop`. DMA submission is in `siu_pcm_wr_set` and `siu_pcm_rd_set`; completion uses `siu_dma_tx_complete`; deferred queuing uses `siu_io_work`. Component callbacks are `siu_pcm_open`, `close`, `prepare`, `trigger`, `pointer`, `pcm_new`, and `pcm_free`. The exported `siu_component` is registered by `siu_dai.c`.

Control flow: `pcm_new` selects port by platform-device id, calls `siu_init_port`, configures a managed DMA buffer, stores the PCM pointer, and initializes work items. Open selects TX/RX slave ids from platform data and requests a DMA channel using a SuperH DMA filter. Prepare validates buffer-period divisibility, caches sizes/format/frame count, and trigger starts or stops stream-specific DMA. Each work item submits the current period; completion advances `cur_period`, queues the next work item, and calls `snd_pcm_period_elapsed`.

State and persistence: `siu_stream` stores substream, format, buffer size, period size, current period, transfer count, DMA channel/descriptor/cookie, and read/write flag. Hardware FIFO state is toggled by STFIFO masks derived from firmware. State is volatile and reset at close/free.

Dependencies and integration: Depends on `siu_i2s_data` from `siu_dai.c`, platform data `struct siu_platform` for DMA slave ids, SuperH DMAEngine, ALSA managed DMA buffers, and system high-priority workqueue.

Risks and edge cases: The DMA completion callback name is TX-specific but used for capture too. Workqueue scheduling after stop relies on `rw_flg` checks. `dma_request_channel` and platform-data slave ids are legacy and can fail silently on DT-only systems. Pointer granularity is one period, not actual DMA residue. `siu_pcm_free` assumes `siu_ports[pdev->id]` exists.

Test signals: Open should allocate the expected DMA channel per stream. Prepare should reject non-period-aligned buffers. START should produce repeated period elapsed events; STOP should clear FIFO enable bits and stop new work. Free should cancel both work items without use-after-free.
