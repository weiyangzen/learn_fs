# sources/distributed-fs/ceph-client/drivers/char/ipmi/Makefile

Purpose: kernel build rules for IPMI host, system-interface, BMC, and helper objects.

Important APIs, types, and functions: builds composite `ipmi_si.o` from SI core, KCS/SMIC/BT state machines, hotmod/hardcode/platform, memory I/O, and optional port I/O, PCI, LS2K, and PARISC pieces. It maps Kconfig symbols to object files for message handler, device interface, DMI/platform data, SSIF, IPMB, watchdog, poweroff, BMC KCS/BT/SSIF, and IPMB device interface.

Control flow: Kbuild conditionals add objects based on `CONFIG_*` values; `ipmi_si-y` aggregation creates the single system-interface module/built-in object.

State and persistence: no runtime state; build state is determined by Kconfig.

Dependencies and integration: depends on symbol names from `Kconfig` and source file names in this directory. It integrates host-side and BMC-side drivers into Linux char driver builds.

Risks and test signals: missing object mappings silently omit features; optional object conditionals must match source dependencies. Tests should run build matrices for host IPMI, BMC KCS/BT, IPMB, SSIF, PCI/IOPORT/no-IOPORT, and module vs built-in combinations.
