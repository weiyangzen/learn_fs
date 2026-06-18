# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Makefile

Purpose: kbuild file for the shared Broadcom NAND core and platform glue drivers.

Important APIs/types/functions: it maps `CONFIG_MTD_NAND_BRCMNAND_*` symbols to glue objects, builds `brcmnand.o` for the core, and notes that link order matters so specific drivers such as iProc precede generic STB glue.

Control flow: build-time only. Object order influences platform-driver registration order on systems with potentially overlapping matches.

State and persistence: no runtime state; generated object/module set persists as build output.

Dependencies/integration: integrates with `brcmnand/Kconfig` and MTD raw NAND kbuild.

Risks/test signals: registration-order regressions and unresolved symbols if glue/core combinations are wrong. Test by building each glue as module and built-in and checking module load/probe order.
