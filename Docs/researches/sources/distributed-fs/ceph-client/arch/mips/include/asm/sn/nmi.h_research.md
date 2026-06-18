<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h

Purpose: Defines SGI SN NMI handoff records and saved-register frame layout used for non-maskable interrupt handling and diagnostics.

Important APIs/types/functions: `NMI_MAGIC`, size/offset constants, `nmi_t`, `struct reg_struct`, and register offset macros `R0_OFF` through `NMISR_OFF`.

Control flow: NMI setup fills per-CPU NMI records with magic, flags, callback, call parameter, and global-master state. NMI handlers save CPU registers into the fixed `reg_struct` layout for diagnostics and recovery.

State and persistence: State is per-NASID/per-slice NMI memory and saved register frames. It persists long enough for crash/debug handlers or PROM tools to inspect.

Dependencies and integration points: Depends on SN address macros and fixed KLDIR NMI locations. Integrated by SN NMI, panic, debug, and crash paths.

Risks: Offsets are assembly ABI; changing `reg_struct` layout or offset constants breaks NMI save/restore code. NMI callbacks must be safe in catastrophic contexts.

Test signals: NMI injection, panic/crash dump register validation, and assembly offset checks are useful.

Source read size: 125 lines, 3390 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h -->
