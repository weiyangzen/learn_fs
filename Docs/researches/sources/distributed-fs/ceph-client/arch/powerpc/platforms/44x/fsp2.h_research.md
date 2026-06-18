<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h

Purpose: defines FSP-2 DCR addresses, L2/PLB/DDR/CMU register offsets, reset-status bit masks, and helper macros for indirect CMU and L2 register access.

Important APIs/types/functions: exposes `DCRN_*` constants for PLB4/PLB6 bridges, PLB-OPB bridges, PLB-AHB/AHB-PLB, configuration logic, DDR3/4 controller, core wrapper, and L2 controller; defines CMU register IDs such as `CMUN_CRCS`, `CMUN_TVS1`, and `CMUN_FIR0`; defines `CRCS_STAT_*` reset causes; provides `mtcmu()`, `mfcmu()`, `mtl2()`, and `mfl2()` macros.

Control flow: no standalone execution. Callers write selector DCRs then data DCRs through the macros to access indirect CMU/L2 spaces.

State and persistence: no C state; constants describe persistent hardware state used by `fsp2.c` diagnostics and initialization.

Dependencies and integration: depends on `<asm/dcr.h>` and is used by FSP2 board error handling and early setup.

Risks and test signals: wrong DCR offsets can corrupt unrelated hardware; duplicate `DCRN_DDR34_ECC_CHECK_PORT1/2` value looks suspicious and should be checked against documentation. Test by reading known registers during FSP2 boot and validating error dumps against hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/fsp2.h -->
