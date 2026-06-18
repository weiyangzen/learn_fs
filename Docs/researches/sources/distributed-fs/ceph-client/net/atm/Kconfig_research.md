# sources/distributed-fs/ceph-client/net/atm/Kconfig

Purpose: declares the core ATM protocol option and RFC2684 bridging/routed-over-ATM options.

Important APIs, types, and functions: key symbols are `ATM`, `ATM_BR2684`, and `ATM_BR2684_IPFILTER`. `ATM` is a tristate for the Asynchronous Transfer Mode networking core. `ATM_BR2684` is a tristate depending on `ATM && INET`. `ATM_BR2684_IPFILTER` is a bool depending on `ATM_BR2684`.

Control flow: when sourced by top-level `net/Kconfig`, these symbols control inclusion of the ATM core composite object and optional `br2684.o`. The BR2684 option enables an Ethernet-like or routed netdevice over ATM PVCs; the IP filter option enables an experimental per-VC filter ioctl and receive-path filtering.

State and persistence: configuration persists in `.config`; no runtime state is held in this file.

Dependencies and integration points: coordinates with `net/atm/Makefile`, ATM socket core, ATM drivers, INET protocol support, and userspace tooling documented by the help text.

Risks: BR2684 depends on INET because routed and bridged packet handling uses IP/Ethernet semantics. Enabling experimental IP filtering adds receive-path policy code with limited scope and should be treated as a compatibility feature.

Test signals: build matrices for `ATM=y/m`, `ATM_BR2684=y/m/n`, and `ATM_BR2684_IPFILTER=y/n`; verify dependency enforcement when `INET=n`; ensure module names and object inclusion match the selected tristates.
