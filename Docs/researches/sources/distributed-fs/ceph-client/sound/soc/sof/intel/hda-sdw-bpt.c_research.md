# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-sdw-bpt.c

Purpose: implements SoundWire Bulk Payload Transport helpers over HDA DMA. It prepares paired TX/RX HDA data streams, maps SoundWire channels, optionally programs IPC4 CHAIN_DMA when the DSP is active, starts asynchronous transfer, waits for IOC completion, and tears down resources.

Important APIs: `hda_sdw_bpt_get_buf_size_alignment()` computes FIFO-safe buffer alignment from requested bandwidth. `hda_sdw_bpt_open()` prepares playback and capture streams and writes PCMSyCM channel mapping. `hda_sdw_bpt_send_async()` starts both DMAs. `hda_sdw_bpt_wait()` waits up to `HDA_BPT_IOC_TIMEOUT_MS`, checks flushed positions, disables both DMAs, and returns timeout/disable errors. `hda_sdw_bpt_close()` deprepares streams. Internal `chain_dma_trigger()` sends IPC4 global CHAIN_DMA messages for RUNNING/PAUSED/RESET.

Control flow: open calculates channel counts from bandwidth at 192 kHz/32-bit, calls `hda_data_stream_prepare(... pair=true)`, decouples host/link DMA for DSP mode, and sets stream IDs on SoundWire playback links. send_async starts TX then RX, rolling TX back if RX fails. wait blocks on per-stream `ioc` completions produced by the stream IRQ path, verifies positions return to zero, then disables RX and TX. close deprepares RX then TX and releases CHAIN_DMA/resources.

State and persistence: state is limited to the two `hdac_ext_stream` objects, supplied BDL DMA buffers, PCMSyCM register mapping, link stream ID, and IPC4 CHAIN_DMA allocation. No state persists across close.

Dependencies and integration: depends on `hda_data_stream_prepare/cleanup`, `hda_cl_trigger`, `hdac_bus_eml_sdw_map_stream_ch()`, SoundWire multi-link helpers, SOF IPC4, and dspless mode checks.

Risks and test signals: risks include BPT requiring IPC4 for DSP mode, mismatched bandwidth-to-channel rounding, partially prepared TX/RX cleanup, IOC timeout, position flush timeout, paired stream link lock leaks, and incorrect PDI indices. Test BPT firmware transfers in dspless and DSP modes, forced failures at RX prepare/start, CHAIN_DMA reset on close, buffer alignment, and repeated open/send/wait/close cycles.
