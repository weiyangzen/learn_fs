# sources/distributed-fs/ceph-client/net/x25/Kconfig

Purpose: defines `CONFIG_X25`, the build-time option for the Linux CCITT X.25 Packet Layer Protocol implementation.

Important symbols: `X25` is a tristate option named "CCITT X.25 Packet Layer". Its help text explains virtual circuits, PLP versus LAPB, WAN use cases, and the module name `x25`.

Control flow: Kconfig selection determines whether the `net/x25` packet-layer objects are built into the kernel, built as a module, or excluded. There are no subordinate options in this file; optional sysctl support is controlled by global `CONFIG_SYSCTL` in the Makefile.

State and persistence: the selected value persists in the kernel configuration and controls protocol availability, module packaging, and whether AF_X25 can be registered at runtime.

Dependencies and integration: integrates with the networking Kconfig tree and relies on related lower-layer choices such as LAPB and X.25 async or LAPB-over-Ethernet drivers, documented in `Documentation/networking/x25*.rst`.

Risks and test signals: the main risk is discoverability or build mismatch with the Makefile/module help. Test signals are `all{yes,mod,no}config`, randconfig builds with and without LAPB drivers, and confirming `CONFIG_X25=m` produces module `x25`.
