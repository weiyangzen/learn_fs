# sources/distributed-fs/ceph-client/net/netlink/Kconfig

## Purpose
Kconfig entry for optional Netlink socket diagnostics.

## Important APIs, Types, And Functions
Defines `CONFIG_NETLINK_DIAG` as a tristate named `NETLINK: socket monitoring interface`, defaulting to `n`, with help text identifying `ss` as a consumer.

## Control Flow
No runtime control flow. At configuration time this symbol determines whether the netlink diagnostic module/object is built.

## State And Persistence Behavior
The selected config value persists in kernel build configuration and drives Makefile object inclusion.

## Dependencies And Integration Points
Integrated by the networking Kconfig tree. The paired Makefile uses `obj-$(CONFIG_NETLINK_DIAG)` to include `netlink_diag.o`.

## Risks And Test Signals
Risks are minimal; the main concern is disabled diagnostic visibility unless selected. Test signals are Kconfig menu visibility, module/built-in builds, and `ss` netlink-monitoring functionality when enabled.
