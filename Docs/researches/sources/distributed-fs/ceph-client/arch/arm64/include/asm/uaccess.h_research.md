<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h` defines arm64 user-access primitives: `get_user`/`put_user`, raw copy helpers, unsafe user access regions, privileged-access enable/disable hooks, TTBR0/PAN/MTE handling, and nofault kernel probes. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_UACCESS_H`, `access_ok`, `uaccess_mask_ptr`, `__get_mem_asm`, `__raw_get_mem`, `__raw_get_user`, `__get_user_error`, `__get_user`, `get_user`, `__get_kernel_nofault`, `__put_mem_asm`, `__raw_put_mem`, `__raw_put_user`, `__put_user_error`, `__put_user`, `put_user`, `__put_kernel_nofault`, `raw_copy_from_user`, `raw_copy_to_user`, `user_access_begin`, `user_access_end`, `arch_unsafe_put_user`, `arch_unsafe_get_user`, `unsafe_copy_loop`, `unsafe_copy_to_user`, `INLINE_COPY_TO_USER`, `INLINE_COPY_FROM_USER`, `clear_user`; functions/prototypes/exports: `access_ok`, `__uaccess_ttbr0_disable`, `__uaccess_ttbr0_enable`, `uaccess_ttbr0_disable`, `uaccess_ttbr0_enable`, `__uaccess_disable_hw_pan`, `__uaccess_enable_hw_pan`, `uaccess_disable_privileged`, `uaccess_enable_privileged`, `volatile`, `goto`, `user_access_begin`, `user_access_save`, `user_access_restore`, `__clear_user`, `copy_from_user_flushcache`, `probe_subpage_writeable`. The file is 503 lines / 14012 bytes. Direct includes are `asm/alternative.h`, `asm/kernel-pgtable.h`, `asm/sysreg.h`, `linux/bitops.h`, `linux/kasan-checks.h`, `linux/string.h`, `asm/asm-extable.h`, `asm/cpufeature.h`, `asm/mmu.h`, `asm/mte.h`, `asm/ptrace.h`, `asm/memory.h`, `asm/extable.h`, `asm-generic/access_ok.h`.

### Control Flow
Callers first pass through `access_ok` and size-specialized inline assembly. Faulting loads/stores are paired with exception-table fixups so a bad user pointer returns `-EFAULT` rather than taking the kernel down. Copy paths branch to arch copy/clear routines, while `user_access_begin/end` and `uaccess_ttbr0_enable/disable` toggle addressability around short critical sections.

### State, Persistence, And Dependencies
Notable global/static state symbols are `__gma_err`, `__gu_err`, `__pu_err`. The header does not persist data, but it temporarily changes CPU state such as PAN, UAO, TTBR0, and MTE tag-check override state. Correctness depends on exception tables and per-task address-limit assumptions owned by the memory-management and fault subsystems. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
The main risks are missing barriers around privileged user access, stale exception-table entries after inline assembly changes, wrong behavior on PAN/UAO/MTE combinations, and accidental user pointer dereference outside an enabled access window.

### Test Signals
Cross-build arm64 configs with PAN, UAO, KASAN, and MTE variants; run usercopy, nofault probe, hardened-usercopy, and fault-injection tests; inspect generated exception-table entries and copy helper disassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/uaccess.h -->
