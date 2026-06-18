# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.c

Purpose: MPEG-TS muxer for vidtv. It periodically emits PCR, PSI/SI sections, encoder payloads packetized as PES, and null packets into a mux buffer, then hands complete TS packets to the bridge callback.

Important APIs/types/functions: exported functions are `vidtv_mux_init()`, `vidtv_mux_destroy()`, `vidtv_mux_start_thread()`, and `vidtv_mux_stop_thread()`. Internal pieces manage per-PID continuity counters (`vidtv_mux_get_pid_ctx()`, `vidtv_mux_create_pid_ctx_once()`, `vidtv_mux_pid_ctx_init()`), timing (`vidtv_mux_update_clk()`, `vidtv_mux_should_push_pcr()`, `vidtv_mux_should_push_si()`), SI output (`vidtv_mux_push_si()`), PCR output (`vidtv_mux_push_pcr()`), encoder packetization (`vidtv_mux_packetize_access_units()`), polling (`vidtv_mux_poll_encoders()`), null padding, and the workqueue loop `vidtv_mux_tick()`.

Control flow: init allocates mux state and buffer, copies config, initializes channels if none supplied, builds SI tables, initializes work item, and builds PID contexts for PCR/null/PAT/SDT/NIT/EIT/PMT PIDs. Starting sets streaming, records start jiffies, and schedules work. Each tick updates a 27 MHz clock, emits PCR/SI if due, polls encoders and packetizes access units into PES/TS packets, pads 256 null packets, validates TS alignment, invokes the bridge callback with packet count, clears the buffer, updates DVB frontend counters, simulates low pre-BER, and sleeps. Stop clears streaming and cancels work; destroy stops and frees PID contexts, SI/channels, network name, buffer, and mux.

State and persistence: `struct vidtv_mux` owns timing counters, PID continuity hash table, mux buffer/offset, channel list, SI tables, streamed PCR/SI counts, work item, streaming flag, network IDs/name, and callback private data. State is per active stream and recreated when feeds restart.

Dependencies and integration points: depends on channel/SI constructors, PSI/TS/PES writers, encoder abstraction, DVB frontend stats, Linux workqueue/jiffies/vmalloc/hash APIs, and bridge callbacks.

Risks: `vidtv_mux_poll_encoders()` adds `au_nbytes` to `m->mux_buf_offset` after `vidtv_mux_packetize_access_units()` already advanced the offset, which appears to double-count encoder bytes. TS writer overflow guards may mask rather than fail buffer exhaustion. Workqueue loop is cooperative via `streaming`; long writer paths delay stop. PID context creation must include every PID used or null dereferences are possible. Timing and mux-rate padding are approximate, not broadcast-grade.

Test signals: transport stream packet alignment, continuity counter monotonicity per PID, PCR/SI cadence, DVB stats increments, service scan success, mux start/stop under repeated feed changes, buffer-overflow log tests with small buffers, and review/test around encoder offset accounting.
