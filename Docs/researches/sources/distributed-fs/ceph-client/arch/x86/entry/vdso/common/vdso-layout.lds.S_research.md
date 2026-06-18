## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vdso-layout.lds.S

Purpose: common linker script that defines the ELF layout for x86 vDSO shared objects.

Important symbols/sections: `VDSO_VVAR_SYMS`, `vclock_pages`, `pvclock_page`, `hvclock_page`, dynamic/rodata/note/eh_frame/text sections, `.altinstructions`, `.altinstr_replacement`, `__ex_table`, discard rules, and PHDRs for `PT_LOAD`, `PT_DYNAMIC`, `PT_NOTE`, `PT_GNU_EH_FRAME`, `PT_GNU_STACK`, and `PT_GNU_PROPERTY`.

Control flow: at link time it places shared kernel/user data before vDSO text, emits one RX load segment plus read-only metadata program headers, keeps exception-table entries, and discards kernel-only sections that should not appear in the user mapping.

State/persistence: the resulting ELF layout is persisted in `vdso*.so.dbg` images and later mapped into processes by `vma.c`.

Integration points: `vdso32.lds.S`, `vdso64.lds.S`, `vdsox32.lds.S`, vDSO VVAR definitions, alternative instruction patching, exception fixups for SGX, and userspace ELF loaders/debuggers.

Risks: section ordering affects load permissions, VVAR offsets, and symbol addresses used by kernel mapping code. Test signals include vDSO link success with GNU ld/LLD, readelf segment checks, vvar fault tests, SGX extable fixup tests, and ABI symbol/version validation.
