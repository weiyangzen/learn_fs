<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig

Purpose: Defines the Xircom Ethernet vendor configuration menu and the build option for the 16-bit PCMCIA Xircom Ethernet driver.

Important APIs/types/functions: `NET_VENDOR_XIRCOM` is a bool vendor gate that defaults to yes but depends on `PCMCIA`. `PCMCIA_XIRC2PS` is the tristate option for Xircom 16-bit PCMCIA Ethernet/Fast Ethernet cards and depends on `PCMCIA && HAS_IOPORT`. Its module name is documented as `xirc2ps_cs`.

Control flow: Kconfig first exposes the vendor bucket only when PCMCIA is available. If enabled, it exposes the concrete driver option. Selecting `PCMCIA_XIRC2PS=y` builds the driver in, `m` builds a module, and `n` omits it.

State and persistence behavior: No runtime state. The file persists build-time policy only: whether the PCMCIA Xircom source is compiled and whether I/O port APIs are allowed.

Dependencies and integration points: Integrates with the parent Ethernet Kconfig tree, the PCMCIA subsystem, architecture `HAS_IOPORT`, and the sibling Makefile entry that maps `CONFIG_PCMCIA_XIRC2PS` to `xirc2ps_cs.o`.

Risks and test signals: Build coverage should verify all three tristate values, especially architectures without `HAS_IOPORT` where the option must be hidden. Menu visibility should be tested with `PCMCIA=n` and `PCMCIA=y`. Runtime testing belongs to `xirc2ps_cs.c`, but Kconfig tests should confirm module naming and dependency pruning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xircom/Kconfig -->
