# sources/distributed-fs/ceph-client/drivers/net/ovpn/Makefile

Purpose: declares the kernel build composition for the OpenVPN data channel offload module.

Important APIs/types/functions: `obj-$(CONFIG_OVPN) := ovpn.o` builds the module when enabled. `ovpn-y` lists component objects: bind, crypto, AEAD crypto, main, io, netlink, generated netlink, peer, packet ID, socket, stats, TCP, and UDP.

Control flow: Kbuild links the listed objects into `ovpn.o`; there is no runtime logic in this file. Object ordering makes core pieces and generated netlink code part of the same module image.

State and persistence: no state. It defines build-time module membership only.

Dependencies and integration: integrates the ovpn directory with the kernel `CONFIG_OVPN` option and includes both hand-written and generated sources. The selected files in this work item are only a subset of the module.

Risks: omitting a required object breaks unresolved symbols across the module; adding generated code requires keeping `netlink-gen.*` synchronized with the YAML spec and hand-written netlink handlers.

Test signals: compile with `CONFIG_OVPN=m` and built-in, check all listed objects link into `ovpn.o`, and verify module load resolves init/exit and netlink references.
