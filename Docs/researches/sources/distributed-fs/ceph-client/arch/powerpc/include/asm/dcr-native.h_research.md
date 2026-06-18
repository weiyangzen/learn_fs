## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-native.h

Purpose: implements native Device Control Register access for PowerPC 4xx-style systems.

Important APIs/types/functions: `dcr_host_native_t`, `dcr_map_native()`, `dcr_read_native()`, `dcr_write_native()`, `mfdcr()`, `mtdcr()`, indexed accessors `mfdcrx()` and `mtdcrx()`, table fallbacks `__mfdcr()` and `__mtdcr()`, indirect helpers `mfdcri()`, `mtdcri()`, and `dcri_clrset()`.

Control flow: constant DCR numbers below 1024 use direct `mfdcr/mtdcr` inline assembly. Dynamic DCRs use indexed DCR instructions when `CPU_FTR_INDEXED_DCR` is available, otherwise table fallback functions. Indirect DCR reads/writes serialize the address/data register pair with `dcr_ind_lock`.

State and persistence: DCR registers are hardware control state. The only kernel synchronization state is `dcr_ind_lock`.

Dependencies and integration: depends on CPU feature tests, spinlocks, and generated DCR register names from `dcr-regs.h`. Used by 4xx platform and device drivers.

Risks and test signals: fallback selection and indirect locking are critical; unsynchronized indirect access can corrupt another register transaction. Test signals include 4xx platform boot, DCR-mapped device probe, indexed/non-indexed DCR CPU variants, and lockdep/IRQ-disabled indirect access tests.
