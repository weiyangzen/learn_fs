<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c` applies arm64 alternative instruction patches for CPU capabilities, modules, and the vDSO. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `pr_fmt`, `__ALT_PTR`, `ALT_ORIG_PTR`, `ALT_REPL_PTR`, `ALT_CAP`, `ALT_HAS_CB`, `align_down`; types: `alt_region`, `alt_instr`, `elf64_hdr`, `elf64_shdr`; functions/prototypes/exports: `alternative_is_applied`, `branch_insn_requires_update`, `get_alt_insn`, `patch_alternative`, `clean_dcache_range_nopatch`, `__apply_alternatives`, `apply_alternatives_vdso`, `__apply_alternatives_multi_stop`, `apply_alternatives_all`, `apply_boot_alternatives`, `apply_alternatives_module`, `alt_cb_patch_nops`. The file is 305 lines / 7850 bytes. Direct includes are `linux/init.h`, `linux/cpu.h`, `linux/elf.h`, `asm/cacheflush.h`, `asm/alternative.h`, `asm/cpufeature.h`, `asm/insn.h`, `asm/module.h`, `asm/sections.h`, `asm/vdso.h`, `linux/stop_machine.h`.

### Control Flow
Boot and module paths iterate `struct alt_instr` regions, check capability bits, rewrite branch-relative instructions when needed, patch replacement instructions or callback-generated sequences, flush caches, and use `stop_machine` for system-wide safe application.

### State, Persistence, And Dependencies
Notable global/static state symbols are `all_alternatives_applied`, `alternative_is_applied`, `insn`, `i`, `cur`, `__apply_alternatives`, `is_module`, `nr_inst`, `cap`, `region`, `kernel_alternatives`, `__init`, `apply_alternatives_module`. `applied_alternatives` and `all_alternatives_applied` record patch state. Patched kernel text, module text, and vDSO images persist for the lifetime of the boot/module. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Length mismatches, branch offset errors, missing cache maintenance, or patching without CPU synchronization can corrupt executable text.

### Test Signals
Boot on CPUs with differing capabilities, run module load/unload tests, verify vDSO alternatives, disassemble patched sites, and enable text-patching/debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/alternative.c -->
