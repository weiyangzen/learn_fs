# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.c

## Purpose
Implements the `bnx2x` statistics engine. It initializes DMA-backed statistics buffers, builds firmware statistics ramrod requests, posts DMAE and storm statistics queries, validates firmware completion counters, folds hardware/firmware/driver counters into `bp->eth_stats`, updates `net_device_stats`, preserves counters across unload/reset, and offers a safe execution gate for operations that must not race with outstanding stats.

## Important APIs, Types, and Functions
Public entry points are `bnx2x_memset_stats`, `bnx2x_stats_init`, `bnx2x_stats_handle`, `bnx2x_save_statistics`, `bnx2x_afex_collect_stats`, and `bnx2x_stats_safe_exec`. Important internal functions include `bnx2x_get_port_stats_dma_len`, `bnx2x_storm_stats_post`, `bnx2x_hw_stats_post`, `bnx2x_stats_comp`, `bnx2x_stats_pmf_update`, `bnx2x_port_stats_init`, `bnx2x_func_stats_init`, `bnx2x_stats_start`, `bnx2x_stats_pmf_start`, `bnx2x_stats_restart`, `bnx2x_hw_stats_update`, `bnx2x_storm_stats_validate_counters`, `bnx2x_storm_stats_update`, `bnx2x_net_stats_update`, `bnx2x_drv_stats_update`, `bnx2x_stats_update`, `bnx2x_port_stats_stop`, `bnx2x_stats_stop`, `bnx2x_port_stats_base_init`, and `bnx2x_prep_fw_stats_req`.

## Control Flow and State
Statistics are driven by a two-state finite-state machine `bnx2x_stats_stm`, keyed by `STATS_STATE_DISABLED`/`STATS_STATE_ENABLED` and events `STATS_EVENT_PMF`, `STATS_EVENT_LINK_UP`, `STATS_EVENT_UPDATE`, and `STATS_EVENT_STOP`. `bnx2x_stats_handle` serializes transitions with `bp->stats_lock`; timer updates return immediately on contention while non-timer events wait briefly.

`bnx2x_stats_init` reads management shared-memory addresses for port/function statistics, handles PMF migration, seeds old NIG counters, prepares the firmware stats query list, optionally clears host function stats, and calls `bnx2x_memset_stats`. `bnx2x_prep_fw_stats_req` lays out port, PF, optional FCoE, and queue query entries; each storm stats post lets `bnx2x_iov_adjust_stats_req` append enabled non-malicious VF queue stats.

On update, PFs first require DMAE completion, update hardware MAC/NIG counters if PMF, validate storm counters for the last stats ramrod, fold per-queue tstorm/ustorm/xstorm counters into queue, function, and Ethernet totals, then post the next hardware and storm requests. VFs skip hardware stats and completion handling, using only storm stats updates. Stop drains DMAE, does a final update, copies final port/function stats to MCP memory, posts DMAE, and waits for completion.

## State and Persistence Behavior
Persistent software counters live in `bp->eth_stats`, `bp->func_stats`, `bp->dev->stats`, `bp->fp_stats[*].eth_q_stats`, and the corresponding `_old` snapshots used to preserve or delta counters across firmware reset/unload. Hardware and firmware snapshots live in slowpath DMA memory (`port_stats`, `func_stats`, `mac_stats`, `nig_stats`, `fw_stats_req`, `fw_stats_data`, `stats_comp`). `bp->stats_counter` sequences storm ramrods, `bp->stats_pending` tracks outstanding storm updates and triggers a panic after repeated missed updates, and `bp->stats_init` controls whether full counters are reset or old values are preserved.

## Dependencies and Integration Points
Depends on `bnx2x_stats.h` macros and structures, `bnx2x_cmn.h`, `bnx2x_sriov.h`, DMAE helpers, storm firmware statistics layouts, MCP shared memory, link MAC type selection, queue/fastpath iteration macros, FCoE/VIC AFEX structures, and SR-IOV stats query adjustment. Callers include link-up/link-down and PMF paths, the periodic timer, ethtool test paths that stop stats, unload paths that call `bnx2x_save_statistics`, and VF close code that uses `bnx2x_stats_safe_exec`.

## Risks and Test Signals
Risks include DMA length miscalculation from management firmware size fields, counter wrap/delta errors in macro-heavy update code, missing storm completions causing stale stats or panic, PMF migration copying stale port stats, stats DMA racing with VF teardown, FCoE query index shifts, and different MAC type register layouts. Test signals include link-up stats start, periodic stats updates, link flap/restart, PMF handoff, unload/reload counter preservation, VF stats with enabled/malicious/closed VFs, FCoE and non-FCoE builds, EMAC/BMAC/UMAC/XMAC hardware, ethtool stats/register tests, and forced storm timeout or DMAE completion timeout paths.
