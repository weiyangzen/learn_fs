# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/Kconfig

## Purpose
This Kconfig file exposes the Rocker switch driver configuration menu. It defines the vendor gate `NET_VENDOR_ROCKER` and the actual driver option `ROCKER`.

## Important APIs, Types, And Functions
There is no executable code. `NET_VENDOR_ROCKER` is a boolean menu selector defaulting to `y`; disabling it hides Rocker device questions. `ROCKER` is a tristate option named "Rocker switch driver (EXPERIMENTAL)".

## Control Flow
Kconfig control flow is simple: the `ROCKER` option is visible only inside `if NET_VENDOR_ROCKER`. When enabled, it allows built-in or module compilation depending on `y` or `m`.

## State And Persistence
Configuration state persists in the kernel `.config`, not in runtime code. `CONFIG_ROCKER` drives Makefile inclusion and module availability.

## Dependencies And Integration Points
`ROCKER` depends on `PCI`, `NET_SWITCHDEV`, and `BRIDGE`, and selects `CRC32`. These dependencies indicate the driver is a PCI switchdev/bridge integration driver rather than a simple Ethernet MAC.

## Risks
If dependencies are incomplete, the driver may compile without required switchdev/bridge APIs. If `NET_VENDOR_ROCKER` defaults or prompts are changed, defconfig visibility changes. The help text marks the driver experimental but does not enforce experimental config gating.

## Test Signals
Kconfig tests include `CONFIG_ROCKER=m`, `CONFIG_ROCKER=y`, and disabled dependency combinations. Build output should include `rocker.ko` for module builds.
