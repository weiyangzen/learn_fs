# sources/distributed-fs/ceph-client/arch/mips/dec/ecc-berr.c

Purpose: handles bus errors on DECstation systems with ECC logic, including KN02, KN03, KN05, and related DECsystem variants.

Important APIs: `dec_ecc_be_handler()` is installed as the MIPS bus-error exception handler; `dec_ecc_be_interrupt()` handles asynchronous bus error IRQs; `dec_ecc_be_init()` selects KN02 or KN03/KN05 register setup. Private helpers read error address/check syndrome registers, acknowledge errors, classify CPU/DMA events, and correct single-bit ECC reads by rewriting the affected word.

Control flow: the backend reads `ERRADDR` and `CHKSYN`, acknowledges non-ECC errors early, classifies CPU timeout, DMA overrun, memory read/write ECC, adjusts read addresses for pipeline behavior, and returns `MIPS_BE_FIXUP`, `MIPS_BE_DISCARD`, or fatal. Single-bit ECC errors are rewritten and discarded; double/multiple errors remain fatal. Interrupt context fatal errors call `die()`.

State and persistence: static volatile pointers hold model-specific error registers. KN02 and KN03 init routines program ECC correction/diagnostic bits and clear firmware leftovers. There is no persistent storage state.

Dependencies and integration: integrates with `dec/setup.c` bus-error initialization and interrupt request. Depends on DEC ECC/KNxx register definitions, MIPS trap bus-error action codes, ratelimited logging, and IRQ register access.

Risks and test signals: incorrect syndrome classification can mislabel or mishandle ECC. Fixup is allowed only for CPU errors; DMA errors remain fatal. Test with simulated or hardware ECC/parity errors, ensure corrected single-bit errors log and continue, and fatal paths report EPC/RA.
