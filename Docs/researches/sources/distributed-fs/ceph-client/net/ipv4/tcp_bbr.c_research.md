# sources/distributed-fs/ceph-client/net/ipv4/tcp_bbr.c

## Purpose

`tcp_bbr.c` implements the BBR congestion-control module. BBR models the path using recent bottleneck bandwidth and minimum RTT rather than directly treating loss or delay as the primary congestion signal. On ACKs it updates its model, sets pacing rate, and sets congestion window. It registers as the `"bbr"` TCP congestion algorithm and exposes selected callbacks as BPF struct-ops kfuncs.

The implementation is the classic BBR mode machine: `STARTUP` rapidly probes for bandwidth, `DRAIN` removes startup queue, `PROBE_BW` cycles pacing gain to share/probe bandwidth, and `PROBE_RTT` periodically caps inflight to refresh the min-RTT estimate. It also includes long-term bandwidth sampling for policer detection and ACK aggregation compensation.

## Important APIs, Types, and Functions

Core state and constants:

- `enum bbr_mode` defines `BBR_STARTUP`, `BBR_DRAIN`, `BBR_PROBE_BW`, and `BBR_PROBE_RTT`.
- `struct bbr` is stored in `inet_csk_ca(sk)` and tracks min RTT, max bandwidth filter, round counting, mode, recovery state, gain cycle, long-term bandwidth sampling, full-pipe detection, prior cwnd, and ACK aggregation windows.
- Constants define bandwidth/rate scaling (`BW_SCALE`, `BW_UNIT`, `BBR_SCALE`, `BBR_UNIT`), gain values, min RTT window, PROBE_RTT duration, min TSO behavior, cwnd floor, full-bandwidth threshold, policer thresholds, and ACK aggregation clamps.

Rate, pacing, and cwnd helpers:

- `bbr_max_bw()`, `bbr_bw()`, and `bbr_full_bw_reached()` expose the current bandwidth model, using long-term bandwidth when policer mode is active.
- `bbr_rate_bytes_per_sec()` and `bbr_bw_to_pacing_rate()` convert BBR packet-per-usec bandwidth estimates into byte-per-second pacing rates with gain and a pacing margin.
- `bbr_init_pacing_rate_from_rtt()` seeds pacing from initial cwnd and SRTT/default RTT.
- `bbr_set_pacing_rate()` updates `sk_pacing_rate`, allowing increases before full bandwidth is reached and normal gain-driven changes afterward.
- `bbr_min_tso_segs()` and `bbr_tso_segs_goal()` choose TSO sizing from pacing rate.
- `bbr_bdp()`, `bbr_quantization_budget()`, `bbr_inflight()`, and `bbr_packets_in_net_at_edt()` estimate BDP/cwnd/inflight targets and account for packets already scheduled by EDT pacing.
- `bbr_ack_aggregation_cwnd()` and `bbr_update_ack_aggregation()` add bounded cwnd allowance for ACK aggregation.
- `bbr_set_cwnd_to_recover_or_restore()` and `bbr_set_cwnd()` implement recovery packet conservation, loss adjustment, slow-start toward target, cwnd restoration, global clamp enforcement, and PROBE_RTT cwnd cap.

Mode and model updates:

- `bbr_update_bw()` consumes `struct rate_sample`, advances packet-timed rounds, updates long-term policer sampling, and refreshes the windowed max bandwidth filter.
- `bbr_lt_bw_sampling()`, `bbr_lt_bw_interval_done()`, `bbr_reset_lt_bw_sampling()`, and `bbr_reset_lt_bw_sampling_interval()` detect token-bucket policers and temporarily pace at a long-term rate.
- `bbr_check_full_bw_reached()` determines when STARTUP has likely filled the pipe.
- `bbr_check_drain()` moves STARTUP to DRAIN and DRAIN to PROBE_BW when inflight has drained to target.
- `bbr_is_next_cycle_phase()`, `bbr_advance_cycle_phase()`, `bbr_update_cycle_phase()`, and `bbr_reset_probe_bw_mode()` implement PROBE_BW gain cycling.
- `bbr_update_min_rtt()` refreshes min RTT, enters/exits PROBE_RTT, marks low-rate samples app-limited, and clears idle restart.
- `bbr_update_gains()` maps mode to pacing/cwnd gain.
- `bbr_update_model()` runs the full ACK-time model pipeline.

Congestion-control callbacks and registration:

- `bbr_main()` is the `cong_control` callback; it updates the model, pacing rate, and cwnd on ACK processing.
- `bbr_init()` initializes per-flow BBR state and requests pacing.
- `bbr_cwnd_event_tx_start()` handles idle restart, resets ACK aggregation epoch, and refreshes pacing or PROBE_RTT completion.
- `bbr_sndbuf_expand()`, `bbr_undo_cwnd()`, `bbr_ssthresh()`, and `bbr_set_state()` implement TCP congestion-control callbacks for send-buffer sizing, undo, loss recovery threshold, and state changes.
- `bbr_get_info()` exposes `INET_DIAG_BBRINFO` fields: bandwidth, min RTT, pacing gain, and cwnd gain.
- `tcp_bbr_cong_ops` registers the algorithm name `"bbr"` and its callbacks.
- BTF kfunc registration exposes BBR callbacks to `BPF_PROG_TYPE_STRUCT_OPS`; `bbr_register()` registers both kfunc IDs and congestion control, and `bbr_unregister()` unregisters the congestion control module.

## Control Flow

When a socket selects BBR, `bbr_init()` clears the private control block, sets infinite ssthresh, initializes RTT/bandwidth filters and round counters, seeds pacing rate, resets long-term sampling, enters STARTUP, clears ACK aggregation state, and moves `sk_pacing_status` to `SK_PACING_NEEDED` if no pacing was active.

ACK processing calls `bbr_main()`. The control flow is deliberately staged: `bbr_update_model()` updates bandwidth, ACK aggregation, gain-cycle phase, full-pipe state, drain transition, min RTT/PROBE_RTT state, and mode gains. Then `bbr_main()` reads the selected bandwidth estimate, updates `sk_pacing_rate` with the current pacing gain, and updates cwnd using the current cwnd gain and ACKed packet count.

The STARTUP path uses high pacing/cwnd gain while bandwidth grows. `bbr_check_full_bw_reached()` watches non-app-limited packet-timed rounds; when bandwidth fails to grow by 25 percent for three rounds, `full_bw_reached` is set. `bbr_check_drain()` then enters DRAIN with inverse high gain and sets ssthresh to estimated BDP. Once packets in network fall to the unit-gain inflight target, BBR enters PROBE_BW.

The PROBE_BW path cycles through an eight-phase pacing-gain array. A high-gain phase attempts to increase inflight to probe for more bandwidth; a low-gain phase drains; the rest cruise at unit gain. Phase advancement depends on elapsed min RTT and, for non-unit gains, inflight relative to target and loss.

The PROBE_RTT path starts when the min-RTT filter expires and the flow is not idle-restarting. It saves prior cwnd, caps cwnd to four packets, marks samples app-limited, waits for at least 200 ms and a packet-timed round at low inflight, then restores cwnd and returns to STARTUP or PROBE_BW depending on whether full bandwidth had been reached.

Long-term policer detection starts only after loss. It samples delivered/lost packets over bounded round intervals, requires high loss ratio and consistent measured rates across intervals, then sets `lt_use_bw` so `bbr_bw()` uses `lt_bw` and PROBE_BW pacing gain becomes unit gain. After a fixed number of rounds, it resets policer mode and restarts gain cycling.

Loss recovery is handled as an overlay rather than a primary mode. `bbr_set_cwnd_to_recover_or_restore()` reduces cwnd by observed losses, applies packet conservation on the first recovery round, then restores the saved cwnd when recovery exits. `bbr_set_state()` treats RTO loss as a round boundary and feeds long-term sampling.

## State and Persistence Behavior

All BBR per-connection state persists in the congestion-control private area (`ICSK_CA_PRIV_SIZE`) as `struct bbr`. It is initialized once per algorithm selection and updated on ACKs, TX-start events, and TCP CA state transitions.

The key persistent model fields are:

- `bw`: windowed max delivery-rate filter over roughly ten packet-timed rounds.
- `min_rtt_us` and `min_rtt_stamp`: min RTT and freshness window.
- `mode`, `pacing_gain`, `cwnd_gain`, and `cycle_idx`: current mode and gain-cycle state.
- `rtt_cnt`, `next_rtt_delivered`, and `round_start`: packet-timed round tracking.
- `full_bw`, `full_bw_cnt`, and `full_bw_reached`: STARTUP exit detection.
- `lt_*`: long-term policer sampling and selected long-term bandwidth.
- `prior_cwnd`, `prev_ca_state`, and `packet_conservation`: recovery overlay state.
- `ack_epoch_*` and `extra_acked[]`: ACK aggregation window state.

BBR also persists effects into generic TCP/socket fields: `sk_pacing_rate`, `sk_pacing_status`, `tp->snd_ssthresh`, `tp->snd_cwnd`, `tp->app_limited`, and TCP delivery/loss counters consumed from `struct tcp_sock`.

There is no on-disk persistence. Module registration persists globally until module unload or kernel shutdown. BTF kfunc IDs persist while the module is loaded.

## Dependencies and Integration Points

BBR depends on generic TCP congestion-control infrastructure (`struct tcp_congestion_ops`, `tcp_register_congestion_control()`), TCP delivery-rate sampling (`struct rate_sample`, `tp->delivered`, `tp->delivered_mstamp`, `tp->lost`, app-limited marking), pacing support (`sk_pacing_rate`, fq/EDT or internal pacing), `win_minmax`, inet_diag, BTF/kfunc registration, random cycle start selection, and module infrastructure.

Integration points:

- Users select BBR with `TCP_CONGESTION` or sysctl/default congestion-control configuration.
- TCP ACK processing invokes `cong_control` and passes rate samples.
- TCP recovery invokes `ssthresh`, `undo_cwnd`, and `set_state`.
- TCP transmit start invokes `cwnd_event_tx_start`.
- TSO sizing calls `min_tso_segs`.
- `TCP_CC_INFO`/inet_diag call `get_info`.
- BPF struct-ops programs can call the registered BBR kfuncs; local BPF selftests reference these symbols.

## Risks and Edge Cases

- Rate math uses fixed-point scaling and carefully ordered 64-bit operations. Changing order or types can overflow at high rates or underflow low-rate paths.
- BBR depends on accurate delivery-rate samples. App-limited filtering, ACK aggregation, delayed ACKs, GSO/TSO, EDT scheduling, and loss recovery can bias bandwidth estimates if fields are updated incorrectly elsewhere.
- PROBE_RTT intentionally reduces cwnd; bugs in exit conditions can leave flows stuck at four packets or prevent min RTT refresh.
- `bbr_packets_in_net_at_edt()` estimates inflight at scheduled departure time; pacing timestamp or `tcp_clock_cache` mistakes can cause too much or too little inflight.
- Long-term policer detection can suppress bandwidth probing for many rounds. Threshold changes risk underutilization or excessive policer loss.
- Loss recovery deliberately does not behave like Reno/CUBIC multiplicative decrease. External code expecting loss-driven ssthresh behavior may misinterpret BBR state.
- `BUILD_BUG_ON(sizeof(struct bbr) > ICSK_CA_PRIV_SIZE)` constrains future state growth.
- BPF kfunc exposure means callback signatures and BTF registration are ABI-like for BPF struct-ops users in this tree.

## Test Signals

Build-time signals include `CONFIG_TCP_CONG_BBR`, module build/load, `BUILD_BUG_ON` private-state size, and BTF kfunc registration success. Runtime smoke tests can set `TCP_CONGESTION` to `"bbr"`, verify pacing is active, inspect `TCP_INFO` and `TCP_CC_INFO`/inet_diag BBR info, and compare throughput/latency behavior under paced and unpaced qdiscs.

Local BPF selftest signals include `sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tcp_ca_kfunc.c`, which imports BBR kfuncs, and broader TCP CA struct-ops tests under `tools/testing/selftests/bpf`. Network emulation tests should cover STARTUP-to-DRAIN-to-PROBE_BW, PROBE_RTT after min-RTT expiry, idle restart, loss recovery, app-limited samples, ACK aggregation, and policer-like loss/rate caps.
