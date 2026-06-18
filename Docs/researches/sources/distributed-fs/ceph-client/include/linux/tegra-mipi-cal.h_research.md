<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h -->
# sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h

## Purpose
declares the Tegra MIPI calibration provider/consumer API for CSI/DSI PHY calibration control.

## Important APIs, Types, and Functions
The file is 58 lines and exports these visible symbol families: types/enums `tegra_mipi_device`, `tegra_mipi_ops`; macros/constants `__TEGRA_MIPI_CAL_H_`; function-like macros none; inline helpers none; external prototypes `devm_tegra_mipi_add_provider`, `tegra_mipi_free`, `tegra_mipi_enable`, `tegra_mipi_disable`, `tegra_mipi_start_calibration`, `tegra_mipi_finish_calibration`.

## Control Flow
A calibration provider registers with `devm_tegra_mipi_add_provider()`. Consumers request a `tegra_mipi_device` by phandle/index, then enable, start calibration, finish calibration, disable, and free the handle through provider operations.

## State and Persistence Behavior
`tegra_mipi_device` carries provider ops, device pointer, MMIO register block, index, and opaque provider data. Calibration state lives in the provider hardware and driver data, not in this header.

## Dependencies and Integration Points
It depends on platform devices, OF nodes, MMIO pointers, and the provider-specific `tegra_mipi_ops`; it integrates with Tegra camera/display PHY drivers. Direct includes are none.

## Risks and Edge Cases
Consumers must pair request/free and enable/disable, and calibration sequencing must match the PHY lane state. Wrong index/regmap wiring can calibrate the wrong MIPI pad.

## Test Signals
Build Tegra CSI/DSI users, validate OF lookup failures, test enable/calibrate/disable order on hardware, and run suspend/resume with active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-mipi-cal.h -->
