# sources/distributed-fs/ceph-client/net/psample/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_PSAMPLE`, the tristate option for the packet-sampling generic netlink channel.

## Important APIs, types, and functions
There are no C APIs here. The important interface is the `PSAMPLE` menuconfig symbol, prompt, default `n`, help text, and module naming note (`psample`).

## Control flow and state
Kconfig controls whether `net/psample/Makefile` builds `psample.o`. There is no runtime state in this file.

## Dependencies and integration points
The symbol enables the exported `psample_group_*` and `psample_sample_packet()` APIs used by networking components that sample packets and forward metadata to userspace.

## Risks and edge cases
Enabling psample adds a generic netlink family and multicast channels. Configuration regressions would show up as missing symbols for drivers/features that depend on packet sampling or as unwanted attack surface in minimal builds.

## Test signals
Build with `CONFIG_PSAMPLE=n/m/y`, verify module generation and exported symbols, and run generic netlink family discovery when enabled.
