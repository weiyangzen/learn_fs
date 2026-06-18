<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S

Purpose: Linker script for the RISC-V vDSO shared object.

Important APIs/types/functions: Defines ELF sections, dynamic symbol layout, version script inclusion, note/eh_frame/dynamic sections, and discards unsupported sections.

Control flow: Build-time only; controls how vDSO objects are laid out and which symbols are exported.

State and persistence: Produces the runtime vDSO ELF layout mapped into processes.

Dependencies and integration points: Used by vDSO Makefile, symbol versioning, loader expectations, and kernel vDSO validation.

Risks: Section ordering, alignment, and exported symbol mistakes can break dynamic linking, unwinding, or security hardening.

Test signals: `readelf`/`objdump` on vDSO, runtime libc vDSO calls, and build checks for unwanted relocations/sections.

Source read size: 88 lines, 1830 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso/vdso.lds.S -->
