<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig

Purpose: Defines the top-level FDDI network driver menu and the individual DEC and SysKonnect FDDI adapter build options.

Important APIs/types/functions: `FDDI` is a tristate umbrella depending on `PCI || EISA || TC`. Under it, `DEFZA` supports DEC FDDIcontroller 700/700-C TURBOchannel cards and depends on `FDDI && TC`; `DEFXX` supports Digital DEFTA/DEFEA/DEFPA adapters and depends on `FDDI && (PCI || EISA || TC)`; `SKFP` supports SysKonnect FDDI PCI adapters, depends on `FDDI && PCI`, and selects `BITREVERSE`.

Control flow: Enabling `FDDI` exposes the concrete adapter choices. Each child tristate controls whether its driver is built-in, built as a module, or omitted. `SKFP` also forces bit-reversal helpers through Kconfig selection.

State and persistence behavior: No runtime state. The file only encodes build-time availability for legacy FDDI drivers.

Dependencies and integration points: Integrates with PCI, EISA, and TURBOchannel bus support and the sibling Makefile mapping to `defxx.o`, `defza.o`, and `skfp/`. Documentation points users to the SysKonnect FDDI driver guide.

Risks and test signals: Build matrix should cover bus-specific visibility: no FDDI menu without PCI/EISA/TC, `DEFZA` only with TC, `DEFXX` with any supported bus, and `SKFP` only with PCI plus `BITREVERSE` selected. Module names should match help text (`defza`, `defxx`, `skfp`).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Kconfig -->
