# sources/distributed-fs/ceph-client/net/ncsi/Makefile

## Purpose
This Makefile wires the NCSI implementation into the kernel build when `CONFIG_NET_NCSI` is enabled.

## APIs, Types, and Functions
It appends `ncsi-cmd.o`, `ncsi-rsp.o`, `ncsi-aen.o`, `ncsi-manage.o`, and `ncsi-netlink.o` to `obj-$(CONFIG_NET_NCSI)`.

## Control Flow
There is no runtime logic. The object list defines the implementation units for command construction, response parsing, asynchronous event handling, device/channel management, and generic netlink control.

## State and Persistence
The only state is build-system state. If `CONFIG_NET_NCSI` is disabled, none of these translation units are built.

## Dependencies and Integration
The object grouping must stay aligned with declarations in `internal.h`, packet definitions in `ncsi-pkt.h`, public UAPI netlink definitions, and callers from NCSI-aware Ethernet drivers.

## Risks
Missing any listed object would leave unresolved symbols or a partially functional subsystem. Adding new NCSI implementation files requires this Makefile to be updated under the same config symbol.

## Test Signals
Build tests with `CONFIG_NET_NCSI=y` should link all NCSI symbols, including netlink registration, exported device lifecycle APIs, packet TX/RX handlers, and AEN handling.
