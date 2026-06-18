# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_ets.c

Purpose: implements TC ETS offload for LAN966x port schedulers using hardware DWRR costs.

Important APIs and functions: `lan966x_ets_add` validates `tc_ets_qopt_offload`, converts Linux weights to hardware costs with `lan966x_ets_hw_cost`, writes per-priority DWRR configuration, and sets scheduler DWRR count. `lan966x_ets_del` clears all DWRR costs and disables DWRR count.

Control flow: add accepts only root qdisc offload with exactly `NUM_PRIO_QUEUES` bands. It requires the priority map to match the hardware model, where DWRR applies to the lowest consecutive priorities in reverse priority order. It rejects nonzero quanta with zero weight. After finding the minimum active weight, it writes cost values for active bands and updates `QSYS_SE_CFG` for the port scheduler element.

State and persistence: no local software state is stored. Scheduler state persists in QSYS `SE_DWRR_CFG` and `SE_CFG` registers until deleted or overwritten.

Dependencies and integration points: called from TC qdisc setup. Depends on Linux ETS offload structures, LAN966x scheduler element numbering, and QSYS register macros.

Risks and test signals: unsupported priority maps or band counts are rejected, but users may expect more general ETS behavior than hardware supports. Cost rounding affects bandwidth share accuracy. Test add/delete, invalid maps, zero weights, all queues active/inactive combinations, and traffic share measurements.
