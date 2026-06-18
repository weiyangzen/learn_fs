# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-pcie-msm8996.c

## Purpose
This driver implements the Qualcomm QMP PCIe PHY block for MSM8996 using the `qcom,msm8996-qmp-pcie-phy` binding. It exposes up to three per-lane generic PHYs sharing a common SerDes/common block, regulators, resets, and clocks.

## Important APIs, Types, and Functions
`struct qmp_phy_cfg` describes the number of PHYs, SerDes/TX/RX/PCS init tables, clock/reset/regulator names, and register layout offsets. `struct qmp_phy` represents one lane with TX/RX/PCS MMIO, pipe clock, lane reset, index, and backpointer. `struct qcom_qmp` stores shared clocks, resets, regulators, lane array, mutex, and `init_count`.

Common sequencing is in `qmp_pcie_msm8996_com_init()` and `qmp_pcie_msm8996_com_exit()`. `qmp_pcie_msm8996_serdes_init()` writes SerDes tables and polls common PCS ready. `qmp_pcie_msm8996_power_on()` initializes SerDes, releases lane reset, enables pipe clock, writes lane tables, powers up PCS, starts PCS/SerDes, and polls lane status. Creation/probe helpers allocate lanes, map child resources, register fixed 125 MHz pipe clock providers, and register the PHY provider.

## Control Flow
Probe maps the shared SerDes resource, initializes bulk clocks/resets/regulators, counts available child nodes, allocates lane slots, and for each child maps TX/RX/PCS resources, obtains a child pipe clock and lane reset, creates a generic PHY, and registers that child's pipe clock source. The exported `.power_on` callback wraps common init plus lane power-on; `.power_off` powers off the lane and exits the common block.

The common init path is reference-counted by `init_count` under `phy_mutex`. The first lane enables regulators, asserts/deasserts shared resets, enables shared clocks, and powers the common block. The last exit asserts resets, disables clocks, and disables regulators. Lane power-on writes TX/RX/PCS tables and polls `PHYSTATUS` clear.

## State and Persistence
Shared state is `init_count` and the per-lane objects. Hardware state is reprogrammed on power-on and cleared through resets or power-down. Pipe clock providers persist for each child node until device removal.

## Dependencies and Integration Points
The driver depends on QMP common table helpers, QMP register definitions, Linux PHY, platform, OF child-node resource mapping, reset, regulator, clock-provider, and iopoll APIs. Device tree must provide one parent SerDes resource and lane child nodes with TX/RX/PCS resources, lane reset, pipe clock, and `clock-output-names`.

## Risks and Edge Cases
`qmp_pcie_msm8996_power_on()` calls `qmp_pcie_msm8996_serdes_init()` without checking its return value, so common SerDes timeout can be ignored and lane init can proceed. Child count is only rejected when greater than the expected lane count; fewer children are allowed. The common exit sequence sets start/reset/power bits in a way that depends on hardware semantics and should be verified against MSM8996 documentation. The fixed pipe clock is 125 MHz, unlike the separate PCIe2 driver's 250 MHz source.

## Test Signals
Signals include probe with one to three lane child nodes, successful pipe clock provider registration per child, shared init reference counting across simultaneous lanes, PCS ready and PHYSTATUS polling success, and PCIe link training on each lane. Negative tests should cover missing child resources, missing `clock-output-names`, lane reset failures, and SerDes timeout propagation.
