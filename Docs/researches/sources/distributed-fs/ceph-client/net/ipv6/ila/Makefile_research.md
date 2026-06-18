# sources/distributed-fs/ceph-client/net/ipv6/ila/Makefile

## Purpose
Builds the IPv6 Identifier Locator Addressing (ILA) module when `CONFIG_IPV6_ILA` is enabled.

## Important APIs, Types, and Functions
The Makefile declares `obj-$(CONFIG_IPV6_ILA) += ila.o` and composes `ila.o` from `ila_main.o`, `ila_common.o`, `ila_lwt.o`, and `ila_xlat.o`.

## Control Flow
Kbuild includes this directory's module objects only when the IPv6 ILA configuration symbol is selected. The linked object combines generic-netlink/pernet setup, checksum/address translation helpers, lwtunnel integration, and xlat mapping support.

## State and Persistence
The file itself has no runtime state. It determines whether ILA runtime state from the C sources is built and linkable.

## Dependencies and Integration Points
Depends on Kbuild and the `CONFIG_IPV6_ILA` symbol. It integrates ILA into the IPv6 networking build as a single module/object.

## Risks and Test Signals
Risks are limited to missing object membership or config mismatch. Test signals are successful builds with `CONFIG_IPV6_ILA=m/y`, module symbol availability, and link failures if any required object is omitted.
