<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile

**Purpose:** Builds Broadcom Common Firmware Environment support into the MIPS firmware library.

**Important APIs/types/functions:** The only object rule is `lib-y += cfe_api.o`, so this directory contributes the CFE IOCB wrapper implementation whenever included by the parent build.

**Control flow:** Kbuild adds `cfe_api.o` to the built-in library; no conditional logic exists in this file.

**State, dependencies, integration:** Integrates CFE wrappers with the arch library build. Selection is controlled by higher-level Makefiles/Kconfig, not this file.

**Risks and test signals:** Build failures here indicate missing CFE headers or wrong directory inclusion. Test by enabling a CFE-using Broadcom MIPS configuration and confirming `cfe_api.o` links once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile -->
