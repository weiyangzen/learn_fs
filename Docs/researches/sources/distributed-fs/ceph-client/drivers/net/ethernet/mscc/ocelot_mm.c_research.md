# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mm.c

## Purpose
Implements MAC Merge and frame preemption support for TSN-capable Ocelot switches, including ethtool MM set/get, verification state tracking, active preemptible TC updates, and MM IRQ handling.

## Important APIs/types/functions
Public functions are `ocelot_port_set_mm`, `ocelot_port_get_mm`, `ocelot_mm_irq`, `ocelot_mm_init`, `ocelot_port_change_fp`, and `ocelot_port_update_active_preemptible_tcs`. State is per-port `struct ocelot_mm_state`.

## Control flow, state, persistence
Init allocates `ocelot->mm` when supported and reads initial verify state. Set programs RX/TX enable, verification timing, verification disable, and extra fragment size under `fwd_domain_lock`; disabling TX processes pending sticky status first to avoid IRQ storms. IRQ scans ports, updates verify/TX-active state, acknowledges sticky errors, and recomputes active preemptible TCs. Active TCs require MM TX active and, for QSGMII, 1 Gbps speed. State is in per-port MM memory and DEV/QSYS registers.

## Dependencies and integration
Depends on ethtool MM APIs, DEV/QSYS register fields, phylink speed/mode, and `tas_guard_bands_update`. Stats integration is in `ocelot_stats.c`.

## Risks and test signals
Risks include stale TX-active state, QSGMII hangs below gigabit, and incorrect guard-band/cut-through interaction. Test ethtool MM get/set, verify transitions, IRQ sticky acks, link speed changes, QSGMII, PMAC traffic, and MM stats.
