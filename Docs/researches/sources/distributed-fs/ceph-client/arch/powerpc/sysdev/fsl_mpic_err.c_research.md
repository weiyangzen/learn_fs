<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c

Purpose: support Freescale MPIC error interrupt banks as cascaded Linux IRQs.

Important APIs/types/functions: `mpic_setup_error_int()`, `mpic_map_error_int()`, `mpic_err_int_init()`, cascade handler `fsl_error_int_handler()`, IRQ chip callbacks `fsl_mpic_mask_err()` and `fsl_mpic_unmask_err()`, and chip `fsl_mpic_err_chip`.

Control flow: setup maps MPIC error registers, copies the chip, marks the MPIC as having EIMR, and assigns a contiguous set of hardware vectors for error sources. Domain mapping recognizes those vectors, installs the error chip and level handler, and stores MPIC chip data. Init maps the parent error IRQ, masks all error sources, and requests a no-thread cascade handler. The handler reads EISR/EIMR, ignores fully masked status, and dispatches each unmasked set bit through the MPIC irqdomain; dispatch failures cause that error bit to be masked.

State and persistence: error register MMIO, `mpic->err_int_vecs`, `mpic->hc_err`, and EIMR mask state persist in the MPIC structure/hardware.

Dependencies and integration points: depends on core MPIC structures and irqdomain, Freescale MPIC register layout, and platform MPIC init calling these helpers.

Risks: bit order uses `31 - src` and `__builtin_clz`, so vector-to-bit mapping must remain consistent. Secondary MPICs are warned against for error interrupts. Dispatch errors are handled by masking to avoid storms.

Test signals: MPIC error interrupt registration, per-error masking/unmasking, injected error bits causing child IRQ handlers, and no IRQ storms on unmapped errors validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_mpic_err.c -->
