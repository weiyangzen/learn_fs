<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile

Purpose: Kbuild object mapping for MTD partition parsers.

Important APIs/types/functions: Maps parser config symbols to objects: `bcm47xxpart.o`, `bcm63xxpart.o`, `brcm_u-boot.o`, `cmdlinepart.o`, composite `ofpart.o`, `parser_imagetag.o`, `afs.o`, `tplink_safeloader.o`, `parser_trx.o`, `scpart.o`, `sharpslpart.o`, `redboot.o`, and `qcomsmempart.o`. The composite OF parser adds `ofpart_core.o` and optional BCM4908/Linksys NS helpers.

Control flow: When a parser symbol is enabled, Kbuild compiles and links the matching parser into the kernel/module. Composite `ofpart` conditionally includes platform-specific child object files.

State and persistence: No runtime state. Build inclusion controls which parsers register with MTD at runtime.

Dependencies/integration: Couples `parsers/Kconfig` with source compilation. The object names correspond directly to parser registration files.

Risks: A Kconfig symbol without an object mapping results in a parser that never builds. Optional OF subobjects must remain aligned with header declarations and Kconfig symbols.

Test signals: Build matrix enabling each parser individually and in combinations, especially composite `ofpart` with and without BCM4908/Linksys NS extensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Makefile -->
