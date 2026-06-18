# sources/distributed-fs/ceph-client/arch/arm64/kernel/image-vars.h

Purpose: Defines linker-script symbols and aliases needed after section layout resolution for the arm64 kernel image, EFI stub, PI startup code, and nVHE KVM code.

Important macros and symbols: `PI_EXPORT_SYM()` publishes selected kernel symbols as `__pi_*` aliases and asserts they are not BSS. The file provides EFI aliases such as `__efistub_primary_entry`, `__efistub__text`, and `__efistub_caches_clean_inval_pou`, PI libc aliases, feature override aliases, page table aliases, and many `KVM_NVHE_ALIAS*` entries under `CONFIG_KVM`. It also defines `kimage_limit` to avoid LLD convergence issues.

Control flow and persistence: this is linker-time metadata, not runtime code. Its effects persist in the final vmlinux symbol table and govern what early PI/EFI/nVHE code can legally reference.

Dependencies and integration: included only by `vmlinux.lds.S` with `LINKER_SCRIPT` defined. It depends on linker symbols from the arm64 memory layout, EFI stub namespace rules, KVM nVHE namespace isolation, and LLD version behavior.

Risks and test signals: risks are exporting unsafe BSS symbols to PI code, missing aliases after symbol renames, broken nVHE linking, and LLD script regressions. Test with full arm64 links under GNU ld and LLD, EFI boot builds, KVM nVHE builds, relocation/KASLR builds, and link-time assertion coverage.
