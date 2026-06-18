# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene-dvb.c

Purpose: Contains nGene DVB-facing stream exchange and demux helper code, plus a CI transport-stream character device used when a CI expansion is present.

Important APIs, types, and functions: `ngene_dvbdev_ci` defines a DVB device with `ci_fops` for read/write/poll of TS ringbuffers. `tsin_exchange()` receives TS input buffers from the core DMA bottom half and feeds demux or CI ringbuffers. `tsout_exchange()` supplies TS output buffers from userspace ringbuffer data or filler packets. `ngene_start_feed()` and `ngene_stop_feed()` control hardware transfer based on demux users. `my_dvb_dmx_ts_card_init()` and `my_dvb_dmxdev_ts_card_init()` initialize DVB demux and dmxdev plumbing.

Control flow: Userspace reads and writes CI TS data through DVB device file operations backed by `dev->tsin_rbuf` and `dev->tsout_rbuf`. DMA bottom halves call `tsin_exchange()` for TS input; if CI is enabled on channel 2, it strips filler packets, optionally repairs 188-byte packet offset shifts, and writes complete packets to `tsin_rbuf`. Otherwise it calls `dvb_dmx_swfilter()`. TS output reads whole-packet-aligned data from `tsout_rbuf`, fills missing capacity with `TS_FILLER`, optionally swaps words, and returns the buffer to firmware.

State and persistence: State includes `ci_tsfix` module parameter, device ringbuffers, per-channel `tsin_offset` and `tsin_buffer`, demux user counts, and channel running state controlled by the core. There is no persistent hardware configuration in this file.

Dependencies and integration points: Called by `ngene-core.c` as buffer exchange callbacks. Uses DVB ringbuffer, DVB demux, DVB dmxdev, DVB net, and generic DVB device open/release helpers. The CI path depends on `dev->ci.en` being set by core CXD2099 attachment.

Risks: `ts_write()` waits for ringbuffer free space >= `count`; very large writes can block indefinitely if `count` exceeds buffer capacity. CI offset repair uses filler-packet matching and a small scratch buffer; malformed streams can cause repeated offset changes or packet drops. `ngene_start_feed()` honors `cmd_timeout_workaround` and `running`, so firmware-version behavior differs. Helper init functions overwrite `ret` and do not check every intermediate demux frontend operation.

Test signals: Exercise CI read/write/poll readiness, large and unaligned write counts, TS output filler insertion, DF_SWAP32 paths, demux start/stop user counts, CI offset repair on shifted packet boundaries, disabled `ci_tsfix`, filler stripping, and demux init failure propagation.
