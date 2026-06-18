## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_psfp.c

### Purpose
`sparx5_psfp.c` implements IEEE 802.1Qci-style PSFP resources: stream filters, stream gates, flow meters, ISDX mappings, and initialization of service dual leaky bucket groups. It is primarily driven by TC flower gate and police actions.

### Important APIs, Types, And Functions
Exports include resource lookup helpers `sparx5_psfp_isdx_get_sf()`, `sparx5_psfp_isdx_get_fm()`, `sparx5_psfp_sf_get_sg()`, `sparx5_isdx_conf_set()`, add/delete functions for stream filters, gates, and flow meters, and `sparx5_psfp_init()`. Static pools `sparx5_psfp_sf_pool`, `sparx5_psfp_sg_pool`, and `sparx5_psfp_fm_pool` track software resource references.

### Control Flow
Adding a stream gate obtains or shares a gate by TC index, computes a future base time using `sparx5_new_base_time()`, writes admin gate parameters and cumulative gate-control intervals, then triggers a hardware config-change copy to operational state. Flow meter add obtains or shares a meter, selects an SDLB group by rate/burst, programs policer registers, and links the meter into the group. Stream filter add allocates a filter and writes gate/max-SDU/block settings. TC flower maps ISDX to stream filter and optional flow meter.

### State, Persistence, And Dependencies
State spans static software pools, hardware ANA_AC TSN stream filter/gate registers, ANA_L2 ISDX mapping registers, and SDLB policer/list registers. Dependencies include pool helpers, SDLB helpers, policer programming, PTP time via QoS base-time calculation, generated register macros, and chip constants for resource counts.

### Integration Points
`sparx5_tc_flower.c` creates and frees PSFP resources for `FLOW_ACTION_GATE` and `FLOW_ACTION_POLICE`. `sparx5_qos_init()` calls `sparx5_psfp_init()` to initialize SDLB groups, enable SG cycle-time updates, and enable ISDX lookup.

### Risks
Resource pools are static and unprotected; concurrent TC changes need external serialization. Delete paths respect reference counts, so wrong IDs can leak or prematurely reset shared resources. Hardware gate intervals are cumulative, which differs from TC input intervals. Timeout in config-change wait is logged only with `pr_debug()`.

### Test Signals
Test gate add/delete with shared TC indices, flow meter add/delete with shared police indices, always-open gate fallback for police-only filters, ISDX mapping cleanup, max-SDU programming, invalid gate parameters from TC, and SDLB group selection under load.
