<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h

**Purpose:** Declares and wraps MIPS branch/delay-slot exception PC computation helpers.

**Important APIs/types/functions:** Externs include `__compute_return_epc*`, microMIPS and MIPS16e variants, and branch instruction testers. Inline helpers include `delay_slot`, `set_delay_slot`, `clear_delay_slot`, `exception_epc`, `compute_return_epc`, and `MIPS16e_compute_return_epc`.

**Control flow:** Exception handling advances EPC directly for simple non-delay cases, dispatches to ISA-specific decoders for delay slots or compressed ISA modes, and handles branch-likely flags.

**State, dependencies, integration:** Operates on `struct pt_regs` CP0 EPC/cause fields and CPU ISA feature macros. Used by signal, exception, ptrace, and emulation code.

**Risks and test signals:** Incorrect EPC advancement causes repeated exceptions or skipped instructions. Test normal, delay-slot, branch-likely, microMIPS, and MIPS16e exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h -->
