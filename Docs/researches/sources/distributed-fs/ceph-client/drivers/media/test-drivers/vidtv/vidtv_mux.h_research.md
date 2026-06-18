# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.h

Purpose: muxer data structures and public interface for vidtv.

Important APIs/types/functions: defines `struct vidtv_mux_timing`, `struct vidtv_mux_si`, `struct vidtv_mux_pid_ctx`, `struct vidtv_mux`, `struct vidtv_mux_init_args`, and prototypes for init/destroy/start/stop.

Control flow: header only; implementation uses timing fields to decide PCR/SI cadence, SI fields to write PAT/PMT/SDT/NIT/EIT, PID contexts for continuity counters, and callback fields to deliver generated TS packets.

State and persistence: all mux runtime state is in `struct vidtv_mux` for the lifetime of a stream. `pid_ctx` hash table persists continuity counters per PID.

Dependencies and integration points: includes Linux hashtable/workqueue, DVB frontend, and `vidtv_psi.h`. Referenced by bridge and channel code.

Risks: initialization args pass raw pointers/callbacks; lifetime must outlive mux. Adding more channels/encoders must ensure PID contexts and SI metadata remain consistent.

Test signals: build coverage, mux init/destroy with and without supplied channels, and TS analyzer validation of emitted streams.
