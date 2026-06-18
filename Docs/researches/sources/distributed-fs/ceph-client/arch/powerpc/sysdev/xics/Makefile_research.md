<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile

Purpose: Selects XICS common code and backend objects for PowerPC builds.

Important APIs/types/functions: Always builds `xics-common.o` in the directory; conditionally builds `icp-native.o`, `icp-hv.o`, `ics-rtas.o`, `ics-native.o`, and PowerNV `ics-opal.o`/`icp-opal.o`.

Control flow: No runtime behavior; object inclusion follows Kconfig symbols.

State and persistence: No state.

Dependencies and integration points: Ties `PPC_XICS` backend selections to object files used by pseries and PowerNV interrupt setup.

Risks: `xics-common.o` depends on exactly one usable ICP and usually one ICS being registered at runtime; build selection must match firmware/hardware.

Test signals: Link/build tests for LPAR HV, native XICS, RTAS ICS, native ICS, and PowerNV OPAL fallback combinations.

Source read size: 8 lines, 281 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile -->
