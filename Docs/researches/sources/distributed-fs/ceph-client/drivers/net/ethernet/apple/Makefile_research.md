## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/Makefile

Purpose: maps Apple Ethernet Kconfig symbols to their driver object files.

Important APIs, types, and functions: builds `mace.o` for `CONFIG_MACE`, `bmac.o` for `CONFIG_BMAC`, and `macmace.o` for `CONFIG_MACMACE`.

Control flow, state, and dependencies: Kbuild includes objects according to selected config symbols. No runtime state exists in this file.

Integration points: paired with Apple Kconfig module names and the parent Ethernet Makefile.

Risks: symbol/object drift prevents selected legacy drivers from building. Because the file is tiny, accidental unconditional objects are the main build risk.

Test signals: build each Apple Ethernet option as module and built-in; confirm object inclusion matches selected symbols.
