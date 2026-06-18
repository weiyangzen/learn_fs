# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukdump.c

Purpose: implements a diagnostic ioctl path that copies GRU chiplet state, TFM/TGH handles, context CCH/CB/TFH/CBE handles, and optional DSR data to a userspace buffer.

Important APIs and functions: `gru_dump_chiplet_request()` is the user entry point. Helpers include `gru_user_copy_handle()`, `gru_dump_tfm()`, `gru_dump_tgh()`, `gru_dump_context()`, and `gru_dump_context_data()`.

Control flow: request is copied from userspace, gid is bounds-checked and passed through `array_index_nospec()`, then TFM and TGH arrays are copied first. For each requested context, `gru_dump_context()` tries to lock the CCH up to `CCH_LOCK_ATTEMPTS`, copies the CCH, gathers owner pid/vaddr from `gs_gts`, computes allocated CBR/DSR counts, checks user buffer capacity, copies CB/TFH/CBE triplets and optional data segment, unlocks CCH, writes a `GRU_DUMP_MAGIC` header, and advances the output pointer. Return value is number of contexts dumped or a negative error.

State and persistence: read-only diagnostic snapshot except optional cache flushes and temporary CCH lock/delresp clearing in copied user image. No persistent state.

Dependencies and integration points: uses GRU handle layout helpers, `grutables.h` allocation-map iteration, nospec indexing, userspace dump request/header ABI from `grulib.h`, and ioctl dispatch in `grufile.c`.

Risks and test signals: buffer-size arithmetic and user-copy error handling are critical because large hardware state is copied to userspace. Tests should cover invalid gid, single/all-context dumps, too-small buffers, locked CCH behavior, `data_opt`, `flush_cbrs`, and concurrent context unload while dumping.
