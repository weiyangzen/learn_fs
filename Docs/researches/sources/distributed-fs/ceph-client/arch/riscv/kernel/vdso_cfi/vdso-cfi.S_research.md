<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S

Purpose: Embeds the CFI vDSO shared object into the kernel under distinct linker symbols.

Important APIs/types/functions: Renames `vdso_start`/`vdso_end` to `vdso_cfi_start`/`vdso_cfi_end` and includes the normal `vdso.S` with path `arch/riscv/kernel/vdso_cfi/vdso-cfi.so`.

Control flow: Build-time include emits an `.incbin` for the CFI image.

State and persistence: CFI vDSO blob is stored in the kernel image.

Dependencies and integration points: Consumed by vDSO setup when mapping CFI-capable tasks.

Risks: Symbol/path mismatch prevents CFI vDSO discovery.

Test signals: CFI vDSO build/link, symbol presence, and process mapping under CFI configuration.

Source read size: 11 lines, 234 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/vdso_cfi/vdso-cfi.S -->
