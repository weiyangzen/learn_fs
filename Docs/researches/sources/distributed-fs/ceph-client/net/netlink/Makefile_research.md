# sources/distributed-fs/ceph-client/net/netlink/Makefile

## Purpose
Build rules for the core netlink subsystem directory.

## Important APIs, Types, And Functions
Always builds `af_netlink.o`, `genetlink.o`, and `policy.o` into the networking core. Conditionally builds `netlink_diag.o` when `CONFIG_NETLINK_DIAG` is set, with `netlink_diag-y := diag.o`.

## Control Flow
No runtime control flow. Kbuild expands `obj-y` and `obj-$(CONFIG_NETLINK_DIAG)` based on the configuration.

## State And Persistence Behavior
Build output composition persists into the resulting kernel image or modules. Core netlink and Generic Netlink are always present for this tree.

## Dependencies And Integration Points
Integrates the netlink socket implementation, Generic Netlink support used by NetLabel, netlink policy validation, and optional diagnostic support.

## Risks And Test Signals
Risks include accidental omission of core objects breaking broad networking users, or diagnostic object mismatches with Kconfig. Test signals are allmodconfig/allyesconfig builds, boot smoke tests for Generic Netlink families, and `CONFIG_NETLINK_DIAG=m/y` module or built-in checks.
