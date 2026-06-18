<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h` supplies machine-specific early-entry assembly hooks for `mach-ip27`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_IP27_KERNEL_ENTRY_H`, `PAGE_GLOBAL`, `PAGE_VALID`, `PAGE_DIRTY`, `CACHE_CACHABLE_COW`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is assembly macro expansion during kernel entry. The common MIPS entry path invokes these macros before normal C setup, then returns to generic initialization after CP0, cache, TLB, or SMP wait-loop state has been prepared.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are `asm/sn/addrs.h`, `asm/sn/agent.h`, `asm/sn/klkernvars.h`. Major macro families are `CACHE_CACHABLE (1)`, `PAGE_DIRTY (1)`, `PAGE_GLOBAL (1)`, `PAGE_VALID (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS reset/vector entry code, CP0 setup, TLB/cache mode selection, SMP secondary entry, and kexec handoff.

## Risks
assembly macros run before normal C runtime services, so register clobbers or CPU-revision checks can break boot very early; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; boot cold, kexec, and SMP secondary CPUs where supported, because failures can occur before console output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip27/kernel-entry-init.h -->
