## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_rxnfc.c

## Purpose
Implements TSNEP ethtool RX network flow classification for steering packets by EtherType to RX queues. It manages the in-memory ordered rule list and programs hardware RX assignment slots.

## Important APIs, Types, and Functions
Exports `tsnep_rxnfc_init`, `tsnep_rxnfc_cleanup`, `tsnep_rxnfc_get_rule`, `tsnep_rxnfc_get_all`, `tsnep_rxnfc_add_rule`, and `tsnep_rxnfc_del_rule`. Internal helpers enable/disable a hardware rule, find/add/delete list entries, choose a free location, initialize `struct tsnep_rxnfc_rule`, and reject duplicates. Rules use `struct tsnep_rxnfc_filter` with `TSNEP_RXNFC_ETHER_TYPE`.

## Control Flow and State
Initialization clears all hardware assignment slots. Add validates that the ethtool flow is `ETHER_FLOW` with only a full EtherType mask, validates queue cookie and location, allocates a rule, assigns an automatic location when requested, rejects duplicate filters at different locations, replaces any old rule at the same location, programs hardware, and inserts the rule in ascending location order. Delete disables hardware, removes from the list, decrements count, and frees memory. All list operations are protected by `adapter->rxnfc_lock`.

## Dependencies and Integration Points
Depends on ethtool RXNFC command structures, Linux list helpers, TSNEP RX assignment MMIO registers, queue count limits encoded by hardware masks, and ethtool glue in `tsnep_ethtool.c`.

## Risks and Test Signals
Risks include accepting a queue cookie that fits the hardware mask but exceeds the currently configured RX queues, duplicate filter replacement semantics surprising users, hardware/list divergence if MMIO writes fail silently, and no persistence across driver reload. Test with `ethtool -N/-n` for add/get/list/delete, automatic locations, duplicate EtherTypes, invalid masks, out-of-range queues and locations, full table behavior, and packet steering validation across multiple RX queues.
