# sources/distributed-fs/ceph-client/net/netfilter/ipvs/Makefile

## Purpose

`Makefile` maps IPVS Kconfig symbols to kernel object files. It defines the core `ip_vs` composite object, optional protocol objects, optional conntrack integration, scheduler modules, application helpers, and persistence engines.

## Important APIs, types, and functions

`ip_vs_proto-objs-y` is built from protocol-specific objects selected by `CONFIG_IP_VS_PROTO_TCP`, `UDP`, `AH_ESP`, and `SCTP`. `ip_vs-extra_objs-y` adds `ip_vs_nfct.o` when `CONFIG_IP_VS_NFCT` is enabled. `ip_vs-objs` combines connection management, core packet handling, control plane, scheduler framework, transmitters, app helpers, sync, estimator, protocol and persistence framework, plus selected protocol/extra objects. `obj-$(CONFIG_IP_VS)` builds the core composite. Individual `obj-$(CONFIG_IP_VS_*)` entries build scheduler and helper modules.

## Control flow

Kbuild evaluates the selected configuration symbols and expands the composite object lists. Core IPVS always includes common framework files when `IP_VS` is enabled, then appends enabled transport protocol and conntrack objects. Scheduler, FTP helper, and SIP persistence files are built as separate objects/modules according to their tristate symbols.

## State and persistence behavior

The file has no runtime state. It determines which code exists in the built kernel or modules and therefore which runtime features can register themselves.

## Dependencies and integration points

It integrates directly with the adjacent `Kconfig` symbols and the kernel Kbuild system. Runtime dependencies appear as link-time inclusion of files such as `ip_vs_conn.o`, `ip_vs_app.o`, `ip_vs_proto_tcp.o`, `ip_vs_rr.o`, `ip_vs_ftp.o`, and `ip_vs_pe_sip.o`.

## Risks

Missing an object in `ip_vs-objs` can produce unresolved symbols or silently remove core runtime behavior. Scheduler/helper entries must match Kconfig symbol names. Optional protocol object aggregation must stay synchronized with protocol registration expectations in IPVS core.

## Test signals

Build tests should enable each protocol, scheduler, helper, and persistence engine as built-in and module where allowed; verify `ip_vs.o` links with and without `IP_VS_NFCT`; and ensure module aliases/load paths work for scheduler and helper modules.
