<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h

## Purpose
Declares EF100 netdevice lifecycle and transmit entry points shared between the PF/VF netdevice implementation and representor code.

## Important APIs, Types, And Functions
- `__ef100_hard_start_xmit()` is the common transmit helper accepting an optional `struct efx_rep *` to tag representor-originated traffic.
- `ef100_netdev_event()` is the netdevice notifier callback declaration.
- `ef100_probe_netdev()` and `ef100_remove_netdev()` expose netdevice setup/teardown to the PCI driver.

## Control Flow
No logic is implemented here. `ef100.c` calls probe/remove declarations during PCI lifecycle, and `ef100_rep.c` calls the shared TX helper when a representor transmits.

## State And Persistence
No state is owned. The prototypes operate on `struct efx_probe_data`, `struct efx_nic`, `struct net_device`, `struct sk_buff`, and optional representor state managed in implementation files.

## Dependencies And Integration Points
Includes Linux netdevice declarations and `ef100_rep.h` for the representor pointer type. It is a dependency bridge between `ef100_netdev.c`, `ef100.c`, and `ef100_rep.c`.

## Risks And Edge Cases
The header includes `ef100_rep.h`, while `ef100_rep.h` includes common driver types; care is needed to avoid future circular include growth. The shared TX helper must preserve semantics for both physical netdev and representor callers.

## Test Signals
Build coverage validates prototypes. Runtime validation comes from both normal PF/VF TX and representor TX paths reaching `__ef100_hard_start_xmit()` successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_netdev.h -->
