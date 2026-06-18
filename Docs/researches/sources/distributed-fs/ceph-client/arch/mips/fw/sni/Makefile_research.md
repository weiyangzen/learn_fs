<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile

**Purpose:** Conditionally builds SNI PROM monitor routines.

**Important APIs/types/functions:** `lib-$(CONFIG_FW_SNIPROM) += sniprom.o` links SNI PROM support when the configuration selects it.

**Control flow:** Kbuild-only conditional object selection.

**State, dependencies, integration:** Ties SNI RM firmware support to the MIPS firmware build.

**Risks and test signals:** Incorrect config selection either omits required PROM support or links unused firmware code. Test SNI RM defconfig/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile -->
