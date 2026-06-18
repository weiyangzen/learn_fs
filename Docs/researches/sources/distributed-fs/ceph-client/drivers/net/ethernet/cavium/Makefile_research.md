# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/Makefile

## Purpose
This top-level Cavium Ethernet Makefile enters Cavium driver subdirectories when `CONFIG_NET_VENDOR_CAVIUM` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. The important build rules append `common/`, `thunder/`, `liquidio/`, and `octeon/` to `obj-*` under the vendor symbol.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_NET_VENDOR_CAVIUM)` and recursively descends into the four Cavium subdirectories for enabled builds. Subdirectory Makefiles then decide individual object/module composition.

## State And Persistence
The file affects only build graph state. It has no runtime persistence.

## Dependencies And Integration Points
It integrates with Kbuild and the Cavium Kconfig menu. It assumes each listed subdirectory has its own Makefile and handles disabled internal symbols correctly.

## Risks
Because all Cavium subdirectories are entered under the vendor umbrella, broken disabled-code build rules in a subdirectory can still affect builds. Directory addition/removal must keep this file, Kconfig, and source tree in sync.

## Test Signals
Build with `CONFIG_NET_VENDOR_CAVIUM=y`, `m`, and disabled, and verify the common, Thunder, LiquidIO, and Octeon subtrees are only compiled as their nested symbols require.
