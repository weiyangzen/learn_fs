# sources/distributed-fs/ceph-client/drivers/clk/mvebu/Makefile

Purpose: Kbuild object mapping for MVEBU clock drivers.

Important APIs/types: maps helper symbols to `common.o`, `clk-cpu.o`, `clk-corediv.o`, and `armada_ap_cp_helper.o`, and maps SoC symbols to Armada 37xx, AP806, CP110, Dove, Kirkwood, Orion, and Armada XP/370/375/38x/39x objects.

Control flow: Kbuild includes object files based on boolean config symbols. Some SoCs build multiple files, such as Armada 37xx xtal/TBG/periph and Dove core/divider.

State and persistence: build metadata only.

Dependencies and integration: must match Kconfig symbols and source filenames in the same directory.

Risks: Armada XP also builds `mv98dx3236.o`; this implicit pairing can surprise maintainers. Adding new SoC files requires Kconfig and Makefile synchronization.

Test signals: object list review for defconfigs, compile tests for each symbol, and missing-object/link-error CI.
