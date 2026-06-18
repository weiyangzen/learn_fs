# sources/distributed-fs/ceph-client/arch/s390/kernel/relocate_kernel.S

Purpose: implements the s390 kexec relocation stub that copies a new kernel image to final physical destinations and transfers control via restart/diagnose.

Important APIs/symbols: defines `relocate_kernel`, local `load_psw`, and exported data `relocate_kernel_len`. It consumes the generic kexec indirection-page entry format via bit flags for destination, indirection, done, and source pages.

Control flow: `%r2` points at kimage entries, `%r3` holds the start address to jump to, and `%r4` holds the diagnose subcode. The loop reads entries, tracks destination pages, follows indirection pages, stops at the done marker, and copies source pages to destination pages using `mvcle` until a page is complete. At done, it places the subcode in `%r0`; if a start address is supplied, it patches a PSW template and copies it to absolute address zero. Finally it issues `diag 0x308`.

State and persistence: modifies physical memory by copying image pages and optionally writes a load PSW at absolute zero. No filesystem state is used.

Dependencies and integration points: depends on the generic kexec image entry encoding, s390 diagnose 0x308 restart semantics, page size constants, and the caller arranging execution from safe memory not overwritten by relocation.

Risks: the code runs without normal kernel services and must not clobber input state prematurely. Entry flag parsing and `0xf000` page masking must match kexec encoding. Wrong PSW patching or absolute-zero writes can hang the machine during kexec.

Test signals: `kexec -e` should boot the target kernel, crash-kernel paths should relocate reliably, image entries with indirection pages should copy correctly, zero start-address diagnose paths should behave as expected, and `relocate_kernel_len` should cover the exact stub range.
