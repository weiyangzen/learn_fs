# sources/distributed-fs/ceph-client/drivers/firmware/samsung/Kconfig

## Purpose
This Kconfig file declares `EXYNOS_ACPM_PROTOCOL`, the Samsung Exynos Alive Clock and Power Manager mailbox protocol driver.

## Important Symbol
- `EXYNOS_ACPM_PROTOCOL`: tristate, depends on `ARCH_EXYNOS || COMPILE_TEST` and `MAILBOX`. It provides client-driver interfaces to APM/ACPM firmware features.

## Control Flow And Integration
Selecting this option builds the composite ACPM protocol object. The help text positions ACPM as an APM firmware communication protocol for AP, AOC, and other masters.

## State And Persistence
No runtime state is stored here; the option controls availability of ACPM protocol code and downstream PMIC/DVFS operations.

## Risks
The driver requires mailbox support and Exynos-compatible firmware shared-memory layout. Enabling under `COMPILE_TEST` verifies buildability but not firmware behavior.

## Test Signals
Build output should include `acpm-protocol.o`, and runtime probing should match compatible ACPM IPC nodes such as `google,gs101-acpm-ipc`.
