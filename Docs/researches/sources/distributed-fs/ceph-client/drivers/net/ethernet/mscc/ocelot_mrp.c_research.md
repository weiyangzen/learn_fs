# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_mrp.c

## Purpose
Handles switchdev MRP objects for Ocelot. It records ring membership, traps MRP frames to CPU, redirects MRP test frames between ring partner ports for MRC, and blackholes standard MRP multicast MACs.

## Important APIs/types/functions
Exports `ocelot_mrp_add`, `ocelot_mrp_del`, `ocelot_mrp_add_ring_role`, and `ocelot_mrp_del_ring_role`. Helpers find partner ports, add/delete IS2 redirect VCAP rules, create trap keys, and learn/forget locked MRP MAC entries.

## Control flow, state, persistence
MRP add stores `mrp_ring_id` only for ports referenced by the MRP object. Ring-role add validates supported role/backup, installs blackhole MACs, then either traps frames or, for MRC, finds the partner, installs redirect, and installs trap with rollback on trap failure. Delete removes trap/redirect and removes blackhole MACs when no ring remains. State is `ocelot_port->mrp_ring_id`, VCAP filters, and MAC table entries.

## Dependencies and integration
Called from switchdev object handlers in `ocelot_net.c`; depends on bridge MRP UAPI, VCAP helpers, trap helpers, and MAC table operations.

## Risks and test signals
Risks include global blackhole MAC behavior across rings, ambiguous partner lookup if more than two ports share a ring, and partial delete failures. Test MRC pairs, non-MRC trap-only roles, rollback, multiple rings, and packet forwarding/trapping.
