<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h

## Purpose
`emac.h` is the central shared header for the Qualcomm EMAC driver. It defines register offsets, bit fields, clock IDs, link-speed masks, statistics layout, feature limits, IRQ and adapter state, and cross-file helper prototypes.

## Important APIs, Types, and Data
- Register offsets cover core DMA, MAC, descriptor, mailbox, interrupt, stats, timestamp, wrapper, and SGMII v2 lane/common blocks.
- Bit masks define DMA master control, interrupt status classes, mailbox indices, hardware version fields, timestamp/reset bits, and wrapper PHY controls.
- `enum emac_clk_id` indexes the driver clock array and must match `emac_clk_name[]` in `emac.c`.
- `struct emac_stats` stores accumulated RX/TX hardware counters plus a spinlock.
- `struct emac_irq` carries IRQ number and active mask.
- `struct emac_adapter` ties together netdev, MDIO PHY/bus, MMIO bases, SGMII state, stats, clocks, ring structures, DMA/ring tunables, flow control, work item, message mask, and reset lock.
- Declares `emac_reinit_locked()`, `emac_reg_update32()`, `emac_set_ethtool_ops()`, and `emac_update_hw_stats()`.

## Control Flow
The header has no executable flow. It defines the data and register contracts used by probe, MAC programming, SGMII initialization, ethtool, and PHY code.

## State and Persistence
Most persistent per-device runtime state is represented by `struct emac_adapter`. Statistics persist across hardware counter reads for the lifetime of the netdev. Ring and clock fields are initialized during probe and open.

## Dependencies and Integration Points
Includes Linux IRQ/netdev/clock/platform headers and the local MAC, PHY, and SGMII headers. Any EMAC source file that touches hardware registers or adapter state depends on these definitions.

## Risks and Edge Cases
- Register and bit definitions are hardware-specific and shared widely; mistakes have broad impact.
- `EMAC_CLK_CNT` must remain synchronized with `emac_clk_name[]`.
- Descriptor limits and MTU constants constrain ethtool, netdev, and ring allocation behavior.
- The adapter struct has no explicit ownership annotations; cleanup paths must follow probe/open ordering.

## Test Signals
Build coverage across all EMAC objects, successful hardware register programming, correct MTU/offload limit reporting, and stable ring/stat behavior after reset are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac.h -->
