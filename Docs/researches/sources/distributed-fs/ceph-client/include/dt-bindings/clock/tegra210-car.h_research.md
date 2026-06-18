# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra210-car.h

## Purpose
Defines Tegra210 CAR clock identifiers for DT clock consumers. It extends the classic Tegra CAR binding model with IDs for Tegra210 peripheral, PLL, audio, display, camera, memory, and synchronization clocks.

## Important APIs, Types, and Constants
The exported `TEGRA210_CLK_*` constants include module IDs beginning around the legacy CAR range, PLL outputs, display/DSI/SOR clocks, XUSB clocks, audio hub and I2S clocks, EMC, MIPI calibration, and DMIC sync clocks. `TEGRA210_CLK_CLK_MAX` is 394. No C types or callable helpers are defined.

## Control Flow and State
The header has include-guard-only preprocessor control flow. Runtime control is performed by Tegra210 clock/reset hardware and kernel providers; this file only names indexes.

## Dependencies and Integration Points
No includes. Device-tree files include it for `clocks`, `resets`, and assigned clock properties, while the Tegra210 clock driver consumes the same ID space.

## Risks and Test Signals
Clock IDs are ABI. Gaps and historical numbering should not be compacted. Tests should include DT compilation, `dtbs_check`, and board boot coverage for high-risk domains such as display, audio, USB, storage, camera, and EMC rate control.
