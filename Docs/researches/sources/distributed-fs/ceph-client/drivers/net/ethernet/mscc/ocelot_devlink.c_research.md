# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_devlink.c

## Purpose
Implements devlink shared-buffer support for Ocelot. It models packet-buffer cells and frame references as devlink SBs with ingress/egress pools, per-port reservations, per-TC reservations, sharing watermarks, and occupancy reporting.

## Important APIs/types/functions
Exports `ocelot_sb_pool_get/set`, `ocelot_sb_port_pool_get/set`, `ocelot_sb_tc_pool_bind_get/set`, occupancy helpers, `ocelot_devlink_sb_register/unregister`, and `ocelot_wm_enc/dec/stat`. Internal macros map four resource planes: ingress buffer, ingress references, egress buffer, egress references.

## Control flow, state, persistence
Registration publishes two devlink SBs, seeds `ocelot->pool_size`, then calls `ocelot_watermark_init()` to disable bad reset reservations and use DP0 sharing for all unreserved resources. Setters write the candidate value, validate aggregate reservations, roll back on failure, then recompute sharing watermarks. State lives in `QSYS_RES_CFG`, `QSYS_RES_STAT`, and `ocelot->pool_size`; it is rebuilt after reset.

## Dependencies and integration
Depends on Ocelot register helpers, chip `wm_enc/wm_dec/wm_stat` ops, and devlink callbacks wired in `ocelot_net.c`.

## Risks and test signals
Main risks are underflow/overcommit if validation is bypassed and confusion around ingress/egress pool indexes. Test with devlink SB pool, port pool, TC bind, invalid over-reservation rollback, occupancy clear, and congested traffic.
