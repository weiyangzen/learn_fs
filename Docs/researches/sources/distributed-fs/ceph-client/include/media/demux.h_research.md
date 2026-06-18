# sources/distributed-fs/ceph-client/include/media/demux.h

Purpose: Defines the hardware-independent DVB demux kABI used between low-level demux hardware/software implementations and DVB clients.

Important APIs/types/functions: Core types are `dmx_ts_feed`, `dmx_section_filter`, `dmx_section_feed`, callback typedefs `dmx_ts_cb` and `dmx_section_cb`, `dmx_frontend`, `dmx_demux_caps`, and `dmx_demux`. Feed methods set PIDs/types/timeouts, allocate/release section filters, and start/stop filtering. Demux callbacks open/close/write, allocate/release feeds, manage frontends, connect/disconnect inputs, and expose PES PIDs or private STC.

Control flow: A client opens a demux, allocates a TS or section feed, configures PID/filter parameters, starts filtering, then receives data through callbacks using one or two buffers for circular-buffer wrap. Frontend registration and connection determine whether TS data comes from memory or hardware.

State and persistence: Feed structures track filtering state, private pointers, CRC/section assembly buffers, and parent demux links. Demux state is implementation-owned and referenced through callback methods.

Dependencies and integration: Depends on DVB userspace `dmx.h`, list APIs, errno, and ktime. It is the foundation used by `dvb_demux.h`, `dmxdev.h`, network, CA, and device-node wrappers.

Risks and test signals: Risks include callback buffer lifetime, section CRC and wrap handling, overflow propagation, PID/filter resource exhaustion, frontend removal while connected, and unclear `get_stc` private behavior. Test allocation failures, concurrent feeds, memory write filtering, circular wrap callbacks, section timeouts, and connect/disconnect edge cases.
