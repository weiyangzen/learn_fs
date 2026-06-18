# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_irq_handler.c

## Purpose
`link_dp_irq_handler.c` implements DP HPD short-pulse IRQ handling. It reads sink/service IRQ status, detects link loss, handles PSR and Panel Replay errors, dispatches automated test work, handles MST sideband readiness, processes USB4 tunneling bandwidth IRQs, and retrains links when needed.

## Important APIs And Functions
- `dp_parse_link_loss_status()` checks lane CR/channel-eq/symbol-lock and interlane alignment status, then verifies the sink is powered D0 before reporting link loss.
- `dp_handle_link_loss()` turns DPMS off for master pipes, optionally restores verified max settings, and turns DPMS back on to retrain/re-enable.
- `dp_read_hpd_rx_irq_data()` reads the correct DPCD IRQ/status block for pre-DP1.4 or DP1.4+ ESI layouts and fills `union hpd_irq_data`.
- `dp_should_allow_hpd_rx_irq()` gates IRQ handling on established link settings, branch devices, or active DPIA bandwidth allocation.
- `dp_handle_hpd_rx_irq()` is the top-level short-pulse handler.
- Internal PSR/replay handlers: `handle_hpd_irq_psr_sink()`, `handle_hpd_irq_vesa_replay_sink()`, `handle_hpd_irq_replay_sink()`.
- `dp_handle_tunneling_irq()` reads `DP_TUNNELING_STATUS`, forwards bandwidth allocation bits to `link_dp_dpia_handle_bw_alloc_status()`, and clears the DP tunneling service IRQ.

## Control Flow
Top-level IRQ handling logs the event, reads IRQ data, returns false on DPCD read failure, and first handles automated test IRQs by clearing the service bit and either deferring work or invoking `dc_link_dp_handle_automated_test()`. It then applies the allow gate, processes PSR errors early, processes Replay errors, reports/defer-handles MST upstream/downstream message readiness, checks link loss, dispatches USB4 tunneling IRQs, detects SST branch sink-count changes, and re-enables Replay when the earlier handler requested it.

Link-loss parsing scans lane nibbles based on `cur_link_settings.lane_count`, handles DP2 EQ/CDS interlane bits separately from legacy interlane alignment, and suppresses handling if the sink is not in D0. Link-loss recovery toggles DPMS for all active master pipes on the link.

PSR handling reads PSR configuration and error/status DPCD registers. CRC/RFB/VSC errors are acknowledged and PSR is disabled/re-enabled when active; active self-refresh without error returns handled to avoid treating the powered-down main link as loss. Replay handling has VESA Panel Replay and AMD FreeSync Replay paths, acknowledges error/status DPCD bits, increments desync counters, may disable Replay, and asks the top-level handler to re-enable it after link-status handling.

## State And Persistence
State changes include:
- `out_hpd_irq_dpcd_data`, `out_link_loss`, and `has_left_work` outputs.
- `link->skip_fallback_on_link_loss` for USB4 automated test workaround.
- `link->psr_settings` active toggles via `edp_set_psr_allow_active()`.
- `link->replay_settings` error status, desync fail count, active toggles, and re-enable state.
- `link->dpia_bw_alloc_config` through delegated bandwidth status handling.
- `link->dpcd_sink_count` comparison determines return status for downstream change detection.
- DPCD service/status bits are cleared for automated test and DP tunneling IRQs.

## Dependencies And Integration Points
This file depends on DPCD helpers, generic training helpers for lane status parsing, capability predicates, eDP panel control, Panel Replay APIs, DP trace, DPMS helpers, DM helpers, and DPIA bandwidth status handling. Higher-level detection and IRQ paths use the boolean return from `dp_handle_hpd_rx_irq()` to decide whether detection work is needed.

## Risks And Edge Cases
- Ordering is important: automated test is handled before the allow gate; PSR is handled before normal link-loss checks.
- DP 1.4+ ESI reads compact a larger block into legacy `union hpd_irq_data`; offset mistakes would misroute IRQ causes.
- `dp_read_hpd_rx_irq_data()` uses a static `retval`, which is unusual for a status local.
- Replay DPCD reads have retry only for one status register and best-effort behavior elsewhere.
- Link-loss DPMS toggling assumes current state pipes remain valid across off/on.
- Deferred handling must set `has_left_work` correctly or sideband/automated-test work can be dropped.

## Test Signals
Test HPD short pulses for automated test, MST upstream/downstream messages, SST branch sink count changes, PSR active/error states, VESA and FreeSync Replay error/desync states, DP2 128b/132b EQ/CDS alignment loss, legacy lane alignment loss, sink D3 suppression, USB4 tunneling bandwidth IRQ bits, deferred handling behavior, and DPMS retraining after link loss.
