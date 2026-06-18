# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-stream.c

Purpose: ACP stream resource allocation and ATU/PTE programming for PCM, firmware trace, and probe DMA buffers.

Important APIs/types/functions: `acp_dsp_stream_config()` maps a stream tag 1-8 to an ATU group, scratch PTE array, and firmware-visible physical offset. `acp_dsp_stream_get()` allocates an inactive stream by requested or any tag. `acp_dsp_stream_put()` releases a stream. `acp_dsp_stream_init()` initializes stream tags and ownership.

Control flow: stream config switches on the stream tag to choose ATU registers and PTE scratch offsets. It writes the stream's firmware-visible physical offset into scratch `reg_offset[]`, enables the ATU group, writes one PTE per DMA page using `snd_sgbuf_get_addr()`, marks high dword valid, and invalidates ATU cache.

State and persistence: stream state lives in `acp_dev_data.stream_buf[]`: active flag, tag, DMA buffer, page count, runtime/substream/compressed stream pointers, register offset, and position offset.

Dependencies and integration points: used by PCM, trace, and probe paths. Relies on scratch layout in `scratch_reg_conf`, ATU registers, SG DMA buffer helpers, and firmware interpreting tag/offset arrays.

Risks: no locking protects stream allocation, so callers must serialize via ALSA/SOF lifecycle. Config writes as many pages as requested; scratch arrays have 16 PTEs per group, so callers must keep buffer pages within hardware/firmware assumptions. Invalid tags return `-EINVAL`.

Test signals: mapping validation for all stream tags, DMA buffer page counts, trace stream tag 8 reservation, and concurrent PCM/probe allocation paths.
