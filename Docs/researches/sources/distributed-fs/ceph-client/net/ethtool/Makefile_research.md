# sources/distributed-fs/ceph-client/net/ethtool/Makefile

## Purpose
This Makefile defines how the kernel ethtool support objects are built. It always links the legacy ioctl and shared common implementation, and conditionally links the generic netlink ethtool implementation when `CONFIG_ETHTOOL_NETLINK` is enabled.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build variables are `obj-y`, `obj-$(CONFIG_ETHTOOL_NETLINK)`, and `ethtool_nl-y`. `ethtool_nl-y` lists the netlink feature objects, including bitsets, link settings, RSS, debug, features, private flags, rings, channels, coalescing, pause, EEE, timestamp info, cable test, tunnels, FEC, EEPROM, module firmware update, CMIS CDB, PSE/PD, PLCA, PHY, timestamp config, and MSE support.

## Control Flow
Kbuild always includes `ioctl.o` and `common.o`. If ethtool netlink is configured, it builds the composite `ethtool_nl.o` object from the listed `ethtool_nl-y` members and links that composite into the networking tree.

## State, Persistence, And Dependencies
The file has no runtime state. Its persistent effect is build graph selection based on kernel configuration. It depends on Kbuild variable semantics and on source/object names staying aligned.

## Integration Points
This file is the build integration point for all `net/ethtool` netlink request handlers. Adding a new ethtool netlink feature requires adding its object to `ethtool_nl-y`; shared code needed by both ioctl and netlink belongs in always-built objects such as `common.o`.

## Risks
Omitting a required object produces link failures or missing feature handlers under `CONFIG_ETHTOOL_NETLINK`. Adding a netlink-only object to `obj-y` could grow builds that do not enable the netlink interface. Renaming source files requires keeping this object list synchronized.

## Test Signals
Build coverage should include configurations with `CONFIG_ETHTOOL_NETLINK=y` and disabled. Link errors, undefined symbols from netlink dispatch tables, or missing message handlers are primary signals.
