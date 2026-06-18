# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-common.h

## Purpose
This header provides the common register-initialization table format and helper functions used by Qualcomm QMP PHY drivers. It standardizes table-driven MMIO programming and optional per-lane filtering.

## Important APIs, Types, and Functions
`struct qmp_phy_init_tbl` contains a register offset, value, debug name, and lane mask. `QMP_PHY_INIT_CFG()` creates an entry for all lanes, while `QMP_PHY_INIT_CFG_LANE()` restricts an entry to a specific lane mask. `qmp_configure_lane()` writes entries whose `lane_mask` intersects the requested mask. `qmp_configure()` applies a table to all lanes by passing mask `0xff`.

## Control Flow
Drivers define static arrays of `qmp_phy_init_tbl` entries. During init, they pass the target MMIO base and table length to `qmp_configure()` or `qmp_configure_lane()`. The helper skips null tables, emits a debug log per write, and writes the value directly with `writel()`.

## State and Persistence
The header has no state. Persistence is entirely in the caller's static tables and in hardware registers after writes.

## Dependencies and Integration Points
It requires `struct device`, MMIO accessors, and debug logging from the kernel environment. It is included by QMP combo and PCIe drivers and depends on register offsets from other QMP headers.

## Risks and Edge Cases
There is no readback, masking, delay, or error return. Callers must ensure register offsets are valid for the selected hardware revision, table lengths are correct, and lane masks match the target lane numbering. Because values are full-register writes, tables must avoid unintentionally clobbering preserved bits.

## Test Signals
Debug logs can confirm register ordering and lane-mask filtering. Functional tests depend on the parent PHY drivers: successful PLL lock, PCS ready, USB/DP/PCIe link training, and no hardware timeout after applying tables.
