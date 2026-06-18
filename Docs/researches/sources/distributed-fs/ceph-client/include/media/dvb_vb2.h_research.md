# sources/distributed-fs/ceph-client/include/media/dvb_vb2.h

Purpose: Videobuf2-based streaming I/O helper for DVB demux/DVR mmap buffer operations.

Important APIs/types/functions: Defines `enum dvb_buf_type`, `enum dvb_vb2_states`, `dvb_buffer`, and `dvb_vb2_ctx`. Context state includes VB2 queue, spinlock, pending buffer list, current buffer, offsets, state bitmask, buffer size/count, nonblocking flag, demux buffer flags, monotonic count, and name. APIs initialize/release, check streaming, fill buffers, poll, stream on/off, request/query/export/queue/dequeue buffers, and mmap. When `CONFIG_DVB_MMAP` is disabled, init/release succeed and streaming/fill/poll stubs return inactive results.

Control flow: Demux/DVR code initializes a context, userspace requests and queues buffers, stream_on starts filling, producer callbacks call `dvb_vb2_fill_buffer`, and userspace dequeues completed buffers with flags/count metadata.

State and persistence: All state is per `dvb_vb2_ctx`; queued buffers and counters persist until streamoff/release. No disk persistence.

Dependencies and integration: Depends on DVB demux UAPI buffer structs and VB2 core, DMA-contig, and vmalloc memory backends. Used by `dmxdev` for mmap capture paths.

Risks and test signals: Risks include state-machine misuse, disabled-config behavior divergence, buffer flag/count loss, nonblocking dequeue semantics, and fill/streamoff races. Test reqbufs zero/nonzero, qbuf/dqbuf order, mmap/export, poll, streamoff while filling, discontinuity flags, and builds without DVB mmap.
