<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h

**Purpose:** Defines DECstation/DECsystem ECC error register bit layouts and ECC handler declarations.

**Important APIs/types/functions:** `KN0X_EAR_*` defines error address register bits; `KN0X_ESR_*` defines syndrome register bits. Declares `dec_ecc_be_init`, `dec_ecc_be_handler`, and `dec_ecc_be_interrupt`.

**Control flow:** Header constants guide bus-error and interrupt handlers that decode/clear ECC status.

**State, dependencies, integration:** Used by DEC memory/bus error handling on KN02/KN03/KN05 class systems.

**Risks and test signals:** Register bits are write-clear; wrong handling loses diagnostic data. Test single/double-bit ECC reports, timeout/overrun, IRQ path, and bus-error fixup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h -->
