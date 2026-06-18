<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c

## Purpose
Implements the EF100 Match-Action Engine MCDI interface for mports, counter streams, firmware table descriptors, capability validation, counters, encapsulation metadata, pedit MAC resources, action sets/lists, outer/action rules, conntrack table entries, and MAE init/fini.

## Important APIs, types, and functions
- Mport APIs: allocation/free, selector construction, firmware lookup, rhashtable enumeration, local VF lookup, and `efx_mae_remove_mport`.
- Counter APIs: `efx_mae_start_counters`, `efx_mae_stop_counters`, `efx_mae_counters_grant_credits`, counter allocate/free.
- Capability/table APIs: `efx_mae_get_tables`, `efx_mae_free_tables`, `efx_mae_get_caps`, match/encap capability checks, table descriptor hooks.
- Resource APIs: encap header allocate/update/free, pedit MAC allocate/free, action set/list allocate/free.
- Rule APIs: encap match register/unregister, LHS rule insert/remove, CT insert/remove, action rule insert/update/delete.
- Lifecycle: `efx_init_mae` and `efx_fini_mae`.

## Control flow
Most public operations build fixed or variable MCDI buffers, populate protocol fields, call `efx_mcdi_rpc`, validate output lengths, store firmware IDs, and verify returned IDs on free/delete. Startup allocates an `efx_mae`, initializes an mport rhashtable, and later enumerates mports from the firmware journal. Capability discovery reads base MAE caps and AR/OR field flags; match checks classify masks as zero, all-ones, prefix, or arbitrary and reject masks unsupported by firmware. Rule insertion populates either outer-rule or action-rule match criteria, assigns action-set or action-set-list responses, and stores returned firmware IDs. Conntrack support first discovers and hooks table descriptors, then packs key/response rows according to firmware-provided field positions before table insert/delete.

## State and persistence behavior
Driver state lives in `efx->mae`, `efx->mae->mports_ht`, `efx->tc->caps`, `efx->tc->meta_ct`, counter flush generations, RX queue credit counters, and firmware IDs stored in TC objects. Hardware/firmware owns allocated mports, counters, encap headers, MAC address entries, action sets, action set lists, outer rules, action rules, and table rows until explicit free/delete calls. Many free paths clear local IDs after successful deletion to reduce stale-ID reuse.

## Dependencies and integration points
Depends on `ef100_nic.h`, MAE and MCDI protocol headers, TC offload objects, tunnel encap action objects, conntrack objects, rhashtable, devlink port descriptors, wait queues, and RX queues for counter streaming. It is the firmware boundary for TC flower/conntrack/tunnel offload on EF100.

## Risks and test signals
High-risk areas are firmware ABI length checks, resource lifetime rollback after partial allocation, ID namespace confusion between AS and ASL high-bit encodings, CT table packing from dynamic descriptors, counter stream drain timeouts, and mport journal duplicate handling. The encap match population should be reviewed carefully because the code writes the L4 destination-port field for both destination and source UDP port values, which may be intentional protocol aliasing or a field-name bug. Test signals include TC offload add/update/delete, tunnel encap/decap, counter packet drain and credit behavior, conntrack insert/delete for IPv4 and IPv6, firmware ID mismatch warnings, unsupported mask extack messages, and unload with all resources freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae.c -->
