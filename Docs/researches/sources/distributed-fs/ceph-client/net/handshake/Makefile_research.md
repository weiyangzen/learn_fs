<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/Makefile -->
# sources/distributed-fs/ceph-client/net/handshake/Makefile

## Purpose
Builds the generic kernel handshake service and optional KUnit tests.

## APIs, Types, and Functions
Declares `obj-y += handshake.o`, composes `handshake-y` from `alert.o`, `genl.o`, `netlink.o`, `request.o`, `tlshd.o`, and `trace.o`, and conditionally builds `handshake-test.o` under `CONFIG_NET_HANDSHAKE_KUNIT_TEST`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Its build aggregation determines which source files form the always-built handshake object and whether test code is compiled.

## Dependencies and Integration
Integrates the handshake directory with kbuild. The unconditional `obj-y` means the service is part of the networking build when this directory is included, while the KUnit object depends on its config symbol.

## Risks and Test Signals
Risks include missing new handshake implementation files from `handshake-y`, generated `genl.*` drift not reflected in the build, or test object linkage assumptions. Test signals are successful link of `handshake.o`, presence of tracepoints, and optional KUnit suite discovery when `CONFIG_NET_HANDSHAKE_KUNIT_TEST` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/Makefile -->
