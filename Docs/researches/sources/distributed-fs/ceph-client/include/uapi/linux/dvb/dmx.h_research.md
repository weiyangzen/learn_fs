## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/dmx.h

Purpose: This header defines the DVB demux UAPI for MPEG transport stream section/PES filtering, PID management, STC reads, and streaming buffers including mmap and DMABUF export.

Important APIs and types: `enum dmx_output`, `enum dmx_input`, and `enum dmx_ts_pes` select data routing, source, and PES class. `struct dmx_filter` and `struct dmx_sct_filter_params` describe 16-byte section header filters, masks, modes, PID, timeout, and flags such as CRC checking, one-shot, and immediate start. `struct dmx_pes_filter_params` configures PES filtering. `struct dmx_stc` returns system time counter data. `struct dmx_buffer`, `struct dmx_requestbuffers`, and `struct dmx_exportbuffer` define streaming buffer queue, mmap offset/cookie, status flags, counters, and DMABUF export fd.

Control flow and state: Userspace sets a section or PES filter, optionally starts it immediately or via `DMX_START`, reads filtered data or uses buffer queue ioctls, then stops/removes PIDs. `DMX_OUT_TS_TAP` routes selected filters into the logical DVR device, while `DMX_OUT_TSDEMUX_TAP` exposes transport stream data through the demux device. Buffer lifecycle follows request, query, queue, dequeue, and optional export.

Persistence and dependencies: Filter state, PID subscriptions, buffer mappings, and counters live in the demux driver until stop, close, or reconfiguration. The header depends on `<linux/types.h>` and includes `<time.h>` for non-kernel legacy compatibility.

Integration points: It integrates with DVB frontend tuning, DVR devices, audio/video decoders, network encapsulation, and dma-buf consumers.

Risks and test signals: Risks include filter mask/mode mistakes, PID leaks, CRC discard handling, TS continuity errors, buffer counter wrap, mmap offset misuse, and DMABUF fd ownership. Tests should cover section and PES filter setup, immediate and explicit start, timeout and one-shot behavior, multi-PID add/remove, STC reads, buffer queue underflow/overflow, flag reporting for TEI/discontinuity/CRC, and DVR routing.
