## sources/distributed-fs/ceph-client/drivers/mtd/devices/Makefile

Purpose: maps MTD device-driver Kconfig symbols to object files for the `drivers/mtd/devices` subtree.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_DOCG3) += docg3.o`, `obj-$(CONFIG_MTD_BLOCK2MTD) += block2mtd.o`, `obj-$(CONFIG_MTD_MCHP23K256) += mchp23k256.o`, `obj-$(CONFIG_MTD_MCHP48L640) += mchp48l640.o`, and `obj-$(CONFIG_MTD_BCM47XXSFLASH) += bcm47xxsflash.o` cover this work item. `CFLAGS_docg3.o += -I$(src)` supports local trace header inclusion.

Control flow: Kbuild evaluates each `obj-*` line according to configuration, compiling built-in or module objects as requested. The docg3 CFLAGS adjustment ensures `TRACE_INCLUDE_PATH .` can resolve `docg3.h`.

State and persistence: no runtime state. It persists the source-to-object build contract.

Dependencies and integration points: tightly coupled with Kconfig symbol names and source filenames. It integrates with kernel recursive Make and module packaging.

Risks: symbol/filename drift causes silent build omission. The docg3 include-path flag is important for tracepoint generation and can break if the trace header layout changes.

Test signals: all selected objects appear in build logs, modules have expected names, `docg3.o` builds with tracepoints, and unselected drivers do not compile unexpectedly.
