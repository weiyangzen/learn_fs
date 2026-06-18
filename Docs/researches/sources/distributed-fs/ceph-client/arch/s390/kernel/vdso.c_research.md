## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso.c

Purpose: Maps the s390 vDSO and vvar pages into new user address spaces, records the vDSO base for stack walking, initializes the TOD programmable field used by vDSO getcpu, and applies vDSO alternatives at boot.

Important APIs and functions: `vdso_getcpu_init()`, `arch_setup_additional_pages()`, `vdso_text_size()`, `vdso_size()`, `vdso_init()`, `map_vdso()`, `vdso_addr()`, `vdso_setup_pages()`, and `vdso_apply_alternatives()`.

Control flow: Early init writes the current CPU number into the TOD programmable field before SMP init. During exec, `arch_setup_additional_pages()` picks a randomized address below `VDSO_BASE` when ASLR is enabled, maps vvar pages first with `vdso_install_vvar_mapping()`, then maps the sealed executable vDSO special mapping. `mremap` updates `mm->context.vdso_base`. Boot-time vDSO init scans the embedded ELF for `.altinstructions`, applies alternatives, and creates the page list for the special mapping.

State and persistence: Stores `mm->context.vdso_base` per process and a global `vdso_mapping.pages` list. The embedded vDSO image is patched once during boot.

Dependencies and integration: Depends on linked symbols `vdso_start`/`vdso_end`, vDSO datastore/vvar helpers, ELF section scanning, alternatives, random address selection, mmap locking, and stacktrace user unwinder knowledge of vDSO layout.

Risks and test signals: Risks include failed vvar/vDSO partial mapping cleanup, wrong ASLR bounds, stale `vdso_base` after mremap, and alternatives corrupting the DSO image. Test signals include process exec vDSO mappings, `getauxval(AT_SYSINFO_EHDR)`, vDSO time/getcpu calls, gdb breakpoints using `VM_MAYWRITE`, mremap behavior, and boot alternative patch logs.
