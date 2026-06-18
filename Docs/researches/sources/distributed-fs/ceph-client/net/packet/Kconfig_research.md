# sources/distributed-fs/ceph-client/net/packet/Kconfig

## Purpose
`net/packet/Kconfig` declares configuration options for Linux packet sockets in this source tree. Packet sockets let applications such as tcpdump communicate directly with network devices below normal protocol stacks.

## Important Options
`config PACKET` is a tristate option named "Packet socket". When built in or as a module, it enables the AF_PACKET protocol implementation; as a module it is named `af_packet`. The help text recommends enabling it for direct device communication and says to choose Y if unsure.

`config PACKET_DIAG` is a tristate option named "Packet: sockets monitoring interface". It depends on `PACKET`, defaults to `n`, and enables the PF_PACKET socket diagnostic interface used by tools such as `ss`.

## Control Flow and Integration
Kconfig selections feed the packet directory Makefile. `CONFIG_PACKET` controls compilation of `af_packet.o`; `CONFIG_PACKET_DIAG` controls `af_packet_diag.o` and its `diag.o` component.

## State and Persistence
This file has no runtime state. It affects kernel build configuration and module availability.

## Dependencies
It depends on the kernel Kconfig system. `PACKET_DIAG` depends on `PACKET`, ensuring diagnostics cannot be built without the base packet socket support.

## Risks
Disabling `PACKET` removes common tooling support for packet capture and raw L2 access. Enabling packet sockets exposes AF_PACKET attack surface, so downstream hardening may choose module-only or disabled builds. The diagnostic option must remain gated on `PACKET`.

## Test Signals
Configuration tests should verify all tristate combinations allowed by dependencies, module names in generated builds, and runtime availability of AF_PACKET sockets and `ss` packet diagnostics when enabled.
