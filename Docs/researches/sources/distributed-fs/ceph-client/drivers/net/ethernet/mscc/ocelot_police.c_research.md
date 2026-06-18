# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_police.c

## Purpose
Configures Ocelot QoS policers and validates tc police actions for offload. It translates software policer parameters into ANA policer registers and provides port policer add/delete.

## Important APIs/types/functions
Exports `qos_policer_conf_set`, `ocelot_policer_validate`, `ocelot_port_policer_add`, and `ocelot_port_policer_del`. Constants define hardware rate modes, port/queue policer index bases, and default policer order.

## Control flow, state, persistence
`qos_policer_conf_set` converts line/data/frame modes into hardware rate/burst units, handles DLB/CIR/coupling/discard states, bounds-checks values, and writes mode, PIR, PIR state, CIR, and CIR state registers. Port add programs a data-rate PIR policer and enables port policing. Delete programs disabled mode and clears enable. State is entirely in ANA policer and port config registers.

## Dependencies and integration
Depends on Ocelot ANA macros and flow action/extack APIs. Used by matchall policing in `ocelot_net.c` and flower policing in `ocelot_flower.c`.

## Risks and test signals
Risks are unit conversion mistakes, unsupported tc semantics being accepted, and burst/rate hardware limits. Test valid/invalid tc police, zero-rate discard, flower `hw_index` policers, add/delete, and register values.
