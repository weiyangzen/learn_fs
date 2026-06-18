# sources/distributed-fs/ceph-client/include/media/dvb_demux.h

Purpose: Implements the software DVB demux-facing internal structures and exported filtering entry points built on top of the abstract `demux.h` API.

Important APIs/types/functions: Defines filter/feed type and state enums, PID/mask constants, `dvb_demux_filter`, `dvb_demux_feed`, and `dvb_demux`. Driver callbacks include `start_feed`, `stop_feed`, optional decoder write, CRC, and memcpy hooks. Exported APIs initialize/release demux internals and feed MPEG-TS buffers through software filtering: aligned 188-byte packets, resyncing 188-byte streams, 204-byte packets, and raw payload.

Control flow: Drivers configure capabilities, filter/feed counts, private data, and start/stop callbacks, then call `dvb_dmx_init`. Incoming packets enter one of the swfilter helpers, which selects active feeds by PID/type, handles continuity/section assembly, and invokes TS or section callbacks. `dvb_dmx_release` frees core-allocated arrays and continuity storage.

State and persistence: `dvb_demux` owns feed/filter arrays, frontend list, PES feed mappings, PID table, active feed list, TS staging buffer, mutex/spinlock, continuity storage, speed counters, users count, and legacy av7110 flags.

Dependencies and integration: Depends on `demux.h`, timers, ktime, mutexes, spinlocks, and DVB userspace PES/PID definitions. Used by hardware bridge drivers and `dmxdev`.

Risks and test signals: Risks include PID table bounds, continuity counter handling, TS resync on corrupt buffers, feed start/stop races, user count limits, and section CRC errors. Test init failure cleanup, feed allocation limits, corrupt sync bytes, 188/204/raw paths, discontinuity flags, CRC overrides, and concurrent start/stop.
