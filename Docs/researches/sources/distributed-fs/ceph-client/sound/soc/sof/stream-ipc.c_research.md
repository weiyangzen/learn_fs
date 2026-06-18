# sources/distributed-fs/ceph-client/sound/soc/sof/stream-ipc.c

Purpose: implements generic mailbox-based stream position IPC helpers and PCM stream private-data setup for SOF.

Important APIs/functions: `sof_ipc_msg_data()` reads stream position data either from the legacy DSP mailbox or from a stream-specific offset stored in PCM/compress runtime private data. `sof_set_stream_data_offset()` validates stream-box bounds/alignment, converts a stream-relative offset to absolute mailbox offset, and stores it in PCM or compressed stream private data. `sof_stream_pcm_open()` allocates `struct sof_stream`, attaches it to `substream->runtime->private_data`, and applies ALSA period constraints. `sof_stream_pcm_close()` detaches and frees that state.

Control flow/state: PCM runtime private data persists between open and close and stores only `posn_offset`. Compressed streams use `struct sof_compr_stream` from `sof-priv.h`. Closed streams return `-ESTRPIPE` when position data is requested after private data is cleared.

Dependencies/integration: depends on SOF mailbox ops, ASoC PCM/compress state, and firmware-provided stream box layout. Exports all helper symbols for platform/IPC users.

Risks/test signals: `sof_set_stream_data_offset()` checks `posn_offset > stream_box.size`, so an offset equal to size passes before adding base, which may be one element past the stream window depending on caller size. Tests should cover no stream box fallback, PCM and compress paths, close-while-position-update race, offset alignment/bounds, and period constraint behavior.
