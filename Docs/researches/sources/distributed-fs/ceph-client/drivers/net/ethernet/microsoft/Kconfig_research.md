# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/Kconfig

## Purpose
This Kconfig file adds the Microsoft Ethernet vendor menu and the `MICROSOFT_MANA` option for the Microsoft Azure Network Adapter driver.

## Important APIs, Types, and Data
- `NET_VENDOR_MICROSOFT` is a vendor-gating boolean, defaults to `y`, and only controls visibility of Microsoft device choices.
- `MICROSOFT_MANA` is a tristate option labeled "Microsoft Azure Network Adapter (MANA) support".
- Dependencies are `PCI_MSI`, `PCI_HYPERV`, and architecture support `X86_64 || (ARM64 && !CPU_BIG_ENDIAN)`.
- Selected subsystems are `AUXILIARY_BUS`, `PAGE_POOL`, and `NET_SHAPER`.

## Control Flow
Kconfig conditionally exposes `MICROSOFT_MANA` inside `if NET_VENDOR_MICROSOFT`. Build selection then drives the Microsoft Makefiles through `CONFIG_MICROSOFT_MANA`.

## State and Persistence
The file affects persistent kernel configuration state in `.config`. It has no runtime state.

## Dependencies and Integration Points
- Integrates the MANA Ethernet driver into the kernel networking driver configuration hierarchy.
- The `PCI_HYPERV` dependency reflects Azure/Hyper-V PCI device integration.
- `AUXILIARY_BUS` supports associated auxiliary devices such as RDMA integration, while `PAGE_POOL` and `NET_SHAPER` support data-path features used by the driver.

## Risks and Edge Cases
- The help text says the driver is "so far" only supported on X86_64 while the dependency also permits little-endian ARM64; documentation may lag platform support.
- Missing `PCI_MSI` or `PCI_HYPERV` prevents the option from appearing even if the source is present.
- Selecting support libraries can enlarge the configured kernel feature set.

## Test Signals
- `allyesconfig`, `allmodconfig`, and targeted MANA configs should confirm the option builds as built-in and module.
- Config tests should verify the option is hidden on unsupported architectures and big-endian ARM64.
