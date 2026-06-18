# sources/distributed-fs/ceph-client/sound/soc/sof/compress.c

Purpose: SOF compressed audio operations for ALSA compressed streams, including buffer/page-table setup, IPC params/triggers, data copy, elapsed notification, and timestamp reporting.

Important APIs/types/functions: `sof_compressed_ops` exports `.open`, `.free`, `.set_params`, `.get_params`, `.trigger`, `.pointer`, and `.copy`. Helpers include `snd_sof_compr_fragment_elapsed()`, `snd_sof_compr_init_elapsed_work()`, `sof_set_transferred_bytes()`, `create_page_table()`, copy helpers for playback/capture, and IPC setup in `sof_compr_set_params()`.

Control flow: open allocates `sof_compr_stream`, associates it with `snd_sof_pcm_stream`, and resets positions. set_params checks firmware ABI >= 3.22.0, boots DSP on demand, allocates SG pages, creates a page table, builds `sof_ipc_pcm_params` with codec data as ext data, sends `SOF_IPC_STREAM_PCM_PARAMS`, stores stream data offset, and marks prepared. trigger maps ALSA commands to SOF stream IPC commands. free sends PCM_FREE if prepared, cancels elapsed work, clears stream, and frees private data.

State and persistence: per-compressed-runtime `sof_compr_stream` stores codec params, sampling rate, channels, sample container bytes, and cumulative copied bytes. SOF PCM stream state holds cstream pointer, page table, posn, and prepared flag.

Dependencies and integration points: ALSA compressed framework, SOF IPC3 stream messages, SOF page-table helpers, PM/on-demand boot, and platform `set_stream_data_offset`.

Risks: set_params has several resource steps and returns without explicitly freeing compressed pages on later failures in this file. ABI gating protects unsupported firmware. Unknown trigger commands log but still send a base stream command, which may not be intended. Copy returns partial counts based on user-copy failures.

Test signals: compressed playback/capture open-set_params-trigger-copy-pointer-free, ABI rejection, wraparound copied byte accounting, and elapsed work scheduling.
