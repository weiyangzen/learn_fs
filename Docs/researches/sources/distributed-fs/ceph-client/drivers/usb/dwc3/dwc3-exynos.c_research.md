# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-exynos.c

## Purpose
`dwc3-exynos.c` is the Samsung Exynos/Google GS101 DWC3 wrapper. It enables SoC-specific clocks and regulators, populates the child DWC3 core from device tree, and handles simple system suspend/resume by disabling/enabling those resources.

## Important APIs, Types, and Functions
The driver uses `struct dwc3_exynos_driverdata` to describe clock names, count, and the suspend clock index for each compatible. `struct dwc3_exynos` stores clock handles and `vdd33`/`vdd10` regulators. Core functions are `dwc3_exynos_probe()`, `dwc3_exynos_remove()`, `dwc3_exynos_suspend()`, and `dwc3_exynos_resume()`.

## Control Flow
Probe gets match data, acquires and enables all named clocks, optionally enables the suspend clock again when a `suspend_clk_idx` is configured, gets and enables `vdd33` then `vdd10`, and calls `of_platform_populate()` to instantiate the child DWC3 core. Error paths disable regulators and clocks in reverse order. Remove depopulates children, disables all clocks, disables the optional suspend clock, then disables regulators.

Suspend disables all clocks and both regulators. Resume enables regulators first, then enables all clocks. The child DWC3 core handles its own PM through the populated child device.

## State and Persistence Behavior
Only live resource handles are stored. There is no retained hardware context in this wrapper; clocks and regulators are restored on resume but wrapper-specific registers are not programmed here. Child core state is owned by the DWC3 child driver.

## Dependencies and Integration Points
Dependencies include OF match data, clk, regulator, platform child population, and system sleep PM. Compatible entries cover multiple Exynos generations and `google,gs101-dwusb3`, each with different clock sets.

## Risks
The suspend clock is enabled in addition to the main clock loop but remove/error handling may disable it separately, so reference counting must match clock provider semantics. Resume error paths can leave `vdd33` enabled if `vdd10` fails, and can leave regulators enabled if a later clock enable fails. Missing device node fails probe because this wrapper only supports OF child population.

## Test Signals
Probe on each compatible should confirm all clock names match bindings and both regulators enable. Suspend/resume should preserve child DWC3 operation and avoid clock/regulator imbalance warnings. Remove/reprobe should not leak child devices. Fault-injection of regulator/clock failures would validate unwind behavior.
