# sources/distributed-fs/ceph-client/arch/x86/boot/startup/Makefile

Purpose: builds the position-independent x86-64 startup support objects used before normal kernel relocation and instrumentation are available.

Important APIs and state: configures special CFLAGS/AFLAGS, disables tracing/LTO/sanitizers/coverage, selects objects (`gdt_idt.o`, `map_kernel.o`, `sme.o`, `sev-startup.o`, `la57toggle.o`, `efi-mixed.o`), and transforms startup object symbols with `objcopy --prefix-symbols=__pi_`. It invokes objtool with `--noabs` on PI objects.

Control flow: make rules compile regular objects, prefix them into `.pi.o`, then replace `obj-y` with PI outputs. Library objects are marked non-standard for objtool.

Dependencies and integration: works with linker-provided aliases in `exports.h` so runtime code can call selected PI implementations. It is critical for early identity-mapped execution.

Risks and test signals: missing flags can introduce instrumentation, stack protector, jump tables, absolute relocations, or LTO output that is unsafe in early boot. Test with objtool no-absolute-relocation checks, sanitizer-enabled configs, EFI mixed-mode configs, and AMD memory encryption configs.
