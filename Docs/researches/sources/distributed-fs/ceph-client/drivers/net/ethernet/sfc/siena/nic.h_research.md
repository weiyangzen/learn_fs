# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/nic.h

## Purpose

`nic.h` is the Siena/Falcon-architecture hardware interface header. It declares PHY type IDs, Siena MAC stat indexes, Siena-specific private NIC state, the exported Siena NIC type, and the farch queue/event/filter/interrupt/global-resource helper APIs implemented across the driver.

## Important APIs, Types, and Functions

The PHY enum names firmware PHY types such as TXC43128, 88E1111, SFX7101, QT202x, PM8358, and SFT9001. The Siena stat enum extends generic software stats with MAC TX/RX counters and ends at `SIENA_STAT_COUNT`.

`struct siena_nic_data` holds hardware-specific state behind `efx->nic_data`: back pointer, WoL filter ID, stats array, and optional SR-IOV state including VFs, VFDI channel/status buffer, VF buffer table base, local address broadcast lists, a mutex, and peer work.

The header declares farch TX/RX/event operations, filter table operations, interrupt handlers, DMA queue flush/reset helpers, stats controls, resource dimensioning, RSS indirection push/pull, register tests, and software event generation.

## Control Flow and Integration

NIC type tables use these prototypes to populate `struct efx_nic_type`. Common wrappers in `nic_common.h` then dispatch queue/event/filter operations through `efx->type`, landing in farch implementations declared here. Higher-level probe, reset, self-test, SR-IOV, RX, TX, and ethtool code include this header when they need Siena-specific operation names or private state.

## State and Persistence Behavior

The header defines persistent Siena private state and stat array size but does not store data itself. Many declared functions mutate hardware descriptor rings, event queues, filter tables, interrupt enable registers, flush counters, SRAM resource dimensions, WoL filters, and stats state.

## Dependencies, Risks, and Test Signals

It includes `nic_common.h` and `efx.h`, making it part of the cross-driver include graph. Risk comes from prototype drift and enum-index coupling: stat descriptors and arrays must match `SIENA_STAT_COUNT`, and NIC type callbacks must match declared signatures. Tests are mostly compile/integration: all Siena build configs, SR-IOV enabled/disabled, RFS enabled/disabled, register self-test, queue flush during reset, and filter insert/remove/restore.
