# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-hw-filter.c

Purpose: implements FlexCop transport-stream hardware filtering: receive-data gating, smartcard and null-packet filter bits, MAC filter programming, PID slot programming, and full-TS fallback.

Important APIs/functions: exported `flexcop_pid_feed_control()` is the DVB demux start/stop hook target. `flexcop_hw_filter_init()` clears all supported PID filters and enables null filtering. `flexcop_set_mac_filter()`, `flexcop_mac_filter_ctrl()`, and `flexcop_smc_ctrl()` configure MAC/SMC bits. Internal helpers map the first six named PID registers and optional 32 extra slots via `index_reg_310`/`pid_n_reg_314`.

Control flow: feed start/stop adjusts `fc->feedcount` and `fc->extra_feedcount`, programs a slot unless PID filtering is bypassed, then toggles group filtering/full-TS mode when filter capacity is exceeded or PID `0x2000` is requested. First feed enables receiver data and optional bus stream control; last feed disables streaming, resets block 300, and reinitializes filters.

State/persistence: state is volatile hardware register state plus in-memory counters (`feedcount`, `extra_feedcount`, `fullts_streaming_state`). No durable persistence.

Dependencies/integration: relies on `flexcop_ibi_value` register bitfields, `fc->read_ibi_reg`/`write_ibi_reg`, DVB demux feed indices, and bus-specific `stream_control`.

Risks/test signals: counter underflow or mismatched start/stop calls could leave full TS enabled. Boundary tests should cover six-slot mode, `skip_6_hw_pid_filter`, 32-slot mode, filter overflow, PID `0x2000`, first/last feed transitions, and MAC byte placement in registers `0x418`/`0x41c`.
