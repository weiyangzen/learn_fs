# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl2/hw_atl2_internal.h

## Purpose
This internal ATL2 header defines hardware limits, ring sizes, traffic-class/RSS constants, interrupt masks, action resolver tags, action encodings, RSS hash type masks, and the private ATL2 state structure used by `hw_atl2.c`.

## Important APIs, types, and functions
Key constants include MTU values, TX/RX ring counts, descriptor sizes, buffer sizes, maximum/minimum descriptors, maximum MAC filters, maximum TCs/RSS queues, interrupt moderation bounds, and ART semaphore ID `HW_ATL2_FW_SM_ACT_RSLVR`. The RPF tag offset/mask macros encode UC, all-multicast, VLAN, untagged, L3/L4, flexible, and PCP match fields. `HW_ATL2_ACTION*` macros encode drop, disable, assign-queue, and assign-TC actions. `enum HW_ATL2_RPF_ART_INDEX` defines driver-owned ART offsets, and `struct hw_atl2_priv` stores the last firmware stats snapshot and ART base index.

## Control flow
There is no executable code, but these constants shape the control flow in `hw_atl2.c`. For example, VLAN and promiscuous control writes ART entries at offsets from `art_base_index`, QoS maps PCP values to TCs using `HW_ATL2_ACTION_ASSIGN_TC`, and multicast/VLAN filters construct tags with the defined RPF masks.

## State and persistence
`struct hw_atl2_priv` is the only state definition. It persists in `aq_hw_s->priv` for the device lifetime and is reset by `hw_atl2_hw_reset`. The rest of the header describes hardware state layouts programmed into registers and resolver tables.

## Dependencies and integration points
The header includes `hw_atl2_utils.h` for `struct statistics_s`, tying private state to the firmware stats ABI. It also depends on shared Atlantic configuration constants such as `AQ_CFG_SKB_FRAGS_MAX`, `AQ_HW_RXD_MULTIPLE`, and `HW_ATL_VLAN_MAX_FILTERS` through included headers.

## Risks
Incorrect tag offsets, ART indexes, or action encodings can misroute or drop packets. The private ART index plan assumes firmware reserves entries before the driver base; if firmware capabilities differ, driver entries could overlap reserved resolver records. Ring and descriptor constants must match hardware and B0 helper assumptions.

## Test signals
Exercise promiscuous, VLAN, PCP-to-TC, queue assignment, and RSS flows. Resolver table readback on supported hardware, if available, can confirm that action encodings and masks produce expected filter behavior.
