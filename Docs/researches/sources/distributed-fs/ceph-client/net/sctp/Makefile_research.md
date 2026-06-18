# sources/distributed-fs/ceph-client/net/sctp/Makefile

Purpose: declares how the SCTP protocol and diagnostic objects are built.

Important entries: `obj-$(CONFIG_IP_SCTP) += sctp.o` builds main SCTP support. `obj-$(CONFIG_INET_SCTP_DIAG) += sctp_diag.o` builds diagnostics. `sctp-y` aggregates state-machine, protocol, endpoint, association, transport, chunk, queue, socket, primitive, auth, offload, stream scheduler, and interleaving objects. `sctp_diag-y := diag.o` maps diagnostics. Conditional additions include `objcnt.o`, `proc.o`, `sysctl.o`, and `ipv6.o`.

Control flow: Kbuild links `sctp-y` into `sctp.o` when SCTP is enabled and appends optional objects based on config. IPv6 is included whenever `CONFIG_IPV6` is built-in or modular via `subst m,y`.

State and persistence: no runtime state; build decisions persist in the produced kernel/module.

Dependencies/integration: maps Kconfig symbols to source files, including this subset's `endpointola.o`, `associola.o`, `chunk.o`, `bind_addr.o`, `debug.o`, `auth.o`, and `diag.o`.

Risks: missing objects can break symbols or remove protocol behavior. IPv6 conditional must match module linkage expectations. Diagnostic support is independent from the main SCTP object.

Test signals: SCTP built-in/module builds, IPv6 built-in/module/off, diag on/off, proc/sysctl toggles, and debug object count builds.
