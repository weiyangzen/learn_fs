## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.lds.S

Purpose: Linker script for the 64-bit s390 vDSO shared object.

Important sections and controls: Defines ELF64 s390 output, `VDSO_VVAR_SYMS`, dynamic/hash/symbol/version sections, PT_NOTE, executable text, rodata, alternatives, dynamic table, eh-frame metadata, GOT, debug sections, discard rules, explicit PHDRs, and exported versioned symbols.

Control flow: The linker lays out a single read-execute PT_LOAD segment plus read-only dynamic/note/eh-frame headers. The script discards data/bss and unwanted notes, keeps unwind metadata, and exports only `__kernel_gettimeofday`, `__kernel_clock_gettime`, `__kernel_clock_getres`, `__kernel_getcpu`, restart/sigreturn trampolines, and `__kernel_getrandom`.

State and persistence: Produces the persistent vDSO ELF image that is incbined into the kernel and mapped into every process that receives vDSO pages.

Dependencies and integration: Depends on vDSO ABI macros, generic vmlinux linker macros, vvar symbol definitions, and the Makefile's shared-object link.

Risks and test signals: Risks are accidentally exporting extra symbols, adding writable data, breaking program headers, or losing unwind info needed by stack walkers. Test signals include vDSO checker, `readelf -l/-S/-s`, exported symbol version tests, and user unwinding across vDSO frames.
