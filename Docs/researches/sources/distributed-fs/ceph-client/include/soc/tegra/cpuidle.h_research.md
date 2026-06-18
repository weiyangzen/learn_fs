# sources/distributed-fs/ceph-client/include/soc/tegra/cpuidle.h

## Purpose

`cpuidle.h` exposes a Tegra cpuidle coordination hook used to notify cpuidle code that PCIe IRQs are in use.

## Important APIs, Types, and Functions

With `CONFIG_ARM_TEGRA_CPUIDLE`, it declares `tegra_cpuidle_pcie_irqs_in_use()`. Otherwise it provides an empty inline stub. There are no data structures.

## Control Flow

Callers invoke the hook after PCIe IRQ usage becomes relevant. The enabled implementation can adjust idle or wake constraints; the disabled implementation is a no-op.

## State and Persistence

No state is defined in the header. Any cpuidle policy or IRQ bookkeeping is owned by the implementation.

## Dependencies and Integration Points

The header has no includes and is gated only by `CONFIG_ARM_TEGRA_CPUIDLE`. It integrates with Tegra PCIe, IRQ, idle, and suspend paths.

## Risks

The hook silently compiles away when cpuidle support is disabled, so callers must not depend on side effects in all builds.

## Test Signals

Build with and without `CONFIG_ARM_TEGRA_CPUIDLE`; on enabled systems test PCIe IRQ wake behavior and idle-state selection after the notification.
