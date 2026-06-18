# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_async_events.h

## Purpose
`gaudi2_async_events.h` is an auto-generated enumeration of Gaudi2 asynchronous event IDs. It gives driver and firmware code stable numeric IDs for ECC, PCIe, AXI, PLL, MMU, HBM, TPC, MME, DMA, NIC, rotator, CPU, ARC, GPIO, and queue-manager events.

## Important APIs, Types, And Functions
The file defines `enum gaudi2_async_event_id` and terminates with `GAUDI2_EVENT_SIZE`. Event ranges include PCIe core/interface/PHY errors, TPC ECC and kernel/BMON/QM events, MME SBTE/control/WAP ECC and AXI/QM events, HDMA/KDMA/PDMA ECC/BMON/QM/core events, PSOC and SRAM events, HBM MC ECC/CATTRIP/SEI/SPI events, HMMU/PMMU ECC/page-fault/security/AXI events, decoder ECC/SPI/BMON/AXI events, HIF/NIC/SM/XBAR ECC/fatal/AXI events, PLL lock failures, PCIe reset/power-management/fatal events, rotator SERR/DERR/AXI/BMON/QM events, CPU firmware/status events, NIC engine status, ARC power/heartbeat, and `GAUDI2_EVENT_SIZE` for array sizing.

## Control Flow
There is no function logic. Runtime event handling uses these IDs as array indexes, switch keys, log identifiers, and firmware event numbers. Cross-references show `gaudi2P.h` allocating arrays sized by `GAUDI2_EVENT_SIZE` and `gaudi2.c` mapping queue IDs to QMAN async event IDs.

## State, Persistence, And Dependencies
The enum has no state, but its numeric values are an ABI-like contract with firmware, interrupt/event queues, and diagnostic tables. Event statistics arrays persist counts indexed by these values. The file depends on generated hardware event assignments remaining stable.

## Integration Points
It integrates with async event queue handling, interrupt reporting, health monitoring, reset/escalation policy, queue-manager error attribution, user-visible event logs, and firmware-to-host notifications.

## Risks
Renumbering or deleting enum values breaks firmware/driver interpretation and corrupts event-stat indexing. Sparse ranges and explicit gaps mean code must use `GAUDI2_EVENT_SIZE`, not assume dense subsystem-local ranges. Typos in generated names, such as `RSPONSE`, can become part of the source contract.

## Test Signals
Tests and diagnostics should verify event queue decoding, correct QMAN event mapping per queue, bounds checks against `GAUDI2_EVENT_SIZE`, event-stat increments for injected events, severity-specific recovery for SERR/DERR/fatal cases, and user logs naming the expected subsystem.
