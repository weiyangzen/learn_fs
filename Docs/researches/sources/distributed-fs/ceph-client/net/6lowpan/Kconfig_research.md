# sources/distributed-fs/ceph-client/net/6lowpan/Kconfig

## Purpose
`net/6lowpan/Kconfig` defines the configuration surface for the 6LoWPAN subsystem, optional debugfs controls, and next-header/generic-header compression modules.

## Important symbols
`6LOWPAN` is a tristate menuconfig depending on `IPV6`. `6LOWPAN_DEBUGFS` depends on `6LOWPAN` and `DEBUG_FS`. `6LOWPAN_NHC` is a tristate compression framework defaulting to enabled when 6LoWPAN is enabled. Under it, RFC6282 options include destination, fragment, hop-by-hop, IPv6, mobility, routing, and UDP NHC modules. RFC7400 generic header compression options cover hop, UDP, ICMPv6, destination, fragment, and routing headers.

## Control flow
Kconfig selection controls compilation only. The core module later requests common RFC6282 NHC modules with `request_module_nowait()`, while individual `obj-*` lines in the Makefile decide whether compression helpers are built-in, modules, or absent.

## State and persistence
There is no runtime state. Persistent effects are build configuration choices in kernel config files.

## Dependencies and integration points
The configuration integrates with IPv6, debugfs, the 6LoWPAN core module, the NHC registry, and link-layer providers such as IEEE 802.15.4 and Bluetooth 6LoWPAN.

## Risks and invariants
Disabling NHC modules can reduce compression coverage and cause IPHC to carry next headers inline. `6LOWPAN_DEBUGFS` exposes runtime context manipulation, so it must remain gated by `DEBUG_FS`.

## Test signals
Build matrix coverage should include 6LoWPAN built-in and module modes, debugfs on/off, `6LOWPAN_NHC=n`, and individual NHC/GHC modules as built-ins or modules.
