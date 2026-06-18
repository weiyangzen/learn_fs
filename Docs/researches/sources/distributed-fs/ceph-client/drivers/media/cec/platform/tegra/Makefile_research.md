# sources/distributed-fs/ceph-client/drivers/media/cec/platform/tegra/Makefile

## Purpose
This Makefile builds the NVIDIA Tegra CEC platform driver.

## Important APIs, Types, and Functions
It maps `CONFIG_CEC_TEGRA` to `tegra_cec.o`.

## Control Flow
Kbuild compiles the Tegra implementation when the config option is enabled.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The implementation depends on platform MMIO, Tegra CEC clocking, IRQs, and CEC notifier integration.

## Risks and Test Signals
Build tests with `CONFIG_CEC_TEGRA` verify object selection.
