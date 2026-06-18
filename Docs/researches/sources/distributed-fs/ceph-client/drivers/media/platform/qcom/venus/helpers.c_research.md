# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.c

## Purpose
`helpers.c` is the main bridge between V4L2/vb2 mem2mem queues and HFI session operations. It handles codec/format validation, buffer-size calculations, DPB and internal DMA buffer allocation, buffer registration, timestamp metadata, profile/level translation, dynamic buffer mode, stream start/stop sequencing, and queued buffer processing.

## Important APIs And Functions
- Codec/format and sizing: `venus_helper_check_codec()`, `venus_helper_check_format()`, `venus_helper_get_out_fmts()`, `venus_helper_get_framesz_raw()`, `venus_helper_get_framesz()`, `venus_helper_get_opb_size()`.
- Buffer requirements and allocations: `venus_helper_get_bufreq()`, `venus_helper_alloc_dpb_bufs()`, `venus_helper_queue_dpb_bufs()`, `venus_helper_free_dpb_bufs()`, `venus_helper_intbufs_alloc()`, `venus_helper_intbufs_free()`, `venus_helper_intbufs_realloc()`, `venus_helper_unregister_bufs()`.
- V4L2/vb2 callbacks: `venus_helper_vb2_buf_init()`, `venus_helper_vb2_buf_prepare()`, `venus_helper_vb2_buf_queue()`, `venus_helper_vb2_start_streaming()`, `venus_helper_vb2_stop_streaming()`, `venus_helper_buffers_done()`, `venus_helper_vb2_queue_error()`.
- Mem2mem callbacks: `venus_helper_m2m_device_run()`, `venus_helper_m2m_job_abort()`.
- HFI property setup: resolution, work mode, format constraints, buffer counts, raw/color format, multistream, dynamic buffer mode, buffer size, stride, profile/level.
- Session utilities: `venus_helper_session_init()`, `venus_helper_init_instance()`, `venus_helper_process_initial_cap_bufs()`, `venus_helper_process_initial_out_bufs()`, timestamp metadata get/put, buffer reference acquire/release, DPB owner changes.

## Control Flow
Stream setup allocates internal buffers based on HFI/platform buffer requirements, registers capture buffers when static buffer mode is required, updates load scaling, loads HFI resources, and starts the session. Queued buffers are put into the V4L2 mem2mem queues, payloads are cached for clock/BW scaling, and if streaming is active they are converted into `hfi_frame_data` and sent through `hfi_session_process_buf()`. Output queues become HFI input buffers; capture queues become HFI output/secondary-output buffers depending on encoder/decoder and OPB type.

DPB handling allocates DMA buffers for decoder picture buffers, assigns tags from `ida`, queues only driver-owned buffers to firmware, and changes ownership back when HFI releases buffer references. Internal scratch/persist buffers are allocated from version-specific type lists and sent to firmware through `set_buffers`; realloc skips persistent buffers and refreshes scratch buffers after format changes.

Stop streaming runs HFI stop, unload resources, unregisters static buffers, frees internal buffers, deinitializes the session, aborts on errors, frees DPBs, rescales PM load, returns all queued V4L2 buffers with error, clears stream flags, releases the PM core, and clears session error state.

## State And Persistence
- Uses `inst->dpbbufs`, `internalbufs`, `registeredbufs`, and `delayed_process` lists.
- Stores timestamp metadata in `inst->tss[]`, payload sizes in `inst->payloads[]`, firmware minimum counts in `inst->fw_min_cnt`, output/input sizes, DPB/OPB formats and buffer types, bit depth, picture structure, and clock data.
- DMA allocations are transient and tied to stream/session lifetime.
- No persistent storage is written.

## Dependencies And Integration Points
- Linux DMA attrs, IDA, lists, mutexes, vb2-dma-contig, V4L2 mem2mem.
- HFI session APIs from `hfi.c`, HFI constants/types from `hfi_helper.h`, platform buffer/frequency data from `hfi_platform*`, PM scaling from `pm_helpers`.
- Called heavily by decoder/encoder queue ops and control setup code outside this subset.

## Risks And Edge Cases
- Buffer lifecycle is intricate: static versus dynamic buffer mode, DPB ownership, readonly buffer references, delayed work, and error returns must not double-free or leave firmware with stale DMA addresses.
- `delayed_process_buf_func()` returns immediately on `session_process_buf()` error without unlocking in that path, which is a subtle control-flow risk if reached.
- Timestamp metadata has a fixed `VIDEO_MAX_FRAME` slot array; slot exhaustion only logs and loses metadata association.
- Platform buffer requirements are preferred, with firmware query fallback; mismatches can cause under-allocation or stream-on failure.
- Frame-size formulas are alignment-heavy and must remain consistent with firmware for UBWC, P010, TP10, and compressed sizes.
- Stop streaming combines multiple return values with bitwise OR and may abort sessions after partial cleanup.

## Test Signals
- V4L2 compliance for queue setup, reqbufs, streamon/off, flush/drain, and buffer error paths.
- Decode tests with dynamic resolution change, secondary output, DPB-only paths, 10-bit UBWC, and delayed buffer-reference release.
- Encoder tests for profile/level mapping, bitrate/QP controls, stride/format programming, and EOS handling.
- DMA leak checks and lockdep under repeated stream start/stop, error injection, and system-error recovery.
