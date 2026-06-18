# sources/distributed-fs/ceph-client/drivers/ipack/carriers/Makefile

Purpose: Selects the TPCI200 carrier object for the IPACK carrier directory.

Important APIs/types/functions: `obj-$(CONFIG_BOARD_TPCI200) += tpci200.o`.

Control flow: Kbuild emits `tpci200.o` only when the carrier config symbol is enabled as built-in or module.

State and persistence: No runtime state; build artifact selection only.

Dependencies/integration: Hooks `drivers/ipack/carriers/tpci200.c` into the kernel/module build controlled by `BOARD_TPCI200`.

Risks and test signals: Verify `BOARD_TPCI200=m` produces a loadable `tpci200` module and `BOARD_TPCI200=y` links it into the kernel image without missing IPACK/PCI symbols.
