<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h -->
# sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h

Purpose: is the private cross-file declaration hub for the SSB subsystem. It exposes host-bus operations, scan/SPROM helpers, core helpers, optional subsystem hooks, and configuration-dependent stubs to keep callers buildable when features are disabled.

Important APIs/types/functions: declarations cover PCI, PCMCIA, SDIO, SoC host, scan, SPROM, core bus lookup, freeze/thaw, B43 PCI bridge, PMU clocks, watchdog hooks, serial/parallel flash, EXTIF, embedded watchdog, and GPIO initialization. `struct ssb_freeze_context` tracks frozen devices for SPROM writes.

Control flow: there is no executable flow except inline stubs. Compile-time `CONFIG_*` gates decide whether a symbol is externally resolved or becomes a no-op/constant-return inline helper.

State and persistence: no state is owned here. It defines the shape of transient freeze context and references subsystem runtime state owned by other files.

Dependencies and integration: includes public `linux/ssb/ssb.h`, types, and BCM47xx watchdog definitions. It is included by SSB implementation files to avoid exposing internals through public headers.

Risks: stub behavior matters: disabled host helpers often return success or zero, so callers must be behind matching bustype/config checks. Prototype drift between this header and implementations is compile-time visible. Returning `-ENOTSUPP` for disabled GPIO differs from no-op success stubs.

Test signals: build SSB with PCI, PCMCIA, SDIO, GPIO, SFLASH, EXTIF, MIPS, and embedded options both enabled and disabled; verify no unresolved symbols and expected stub behavior in disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h -->
