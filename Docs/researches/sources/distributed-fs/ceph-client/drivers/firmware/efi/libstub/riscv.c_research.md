
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv.c

Purpose: handles RISC-V EFI platform feature checks and final kernel entry ABI, especially discovery of the boot hart ID.

Important APIs/types/functions: exports `check_platform_features()`, weak `stext_offset()`, and `efi_enter_kernel()`. Internals are `get_boot_hartid_from_efi()` and `get_boot_hartid_from_fdt()`.

Control flow: platform check first tries the RISC-V EFI Boot Protocol `get_boot_hartid()`, then falls back to `/chosen/boot-hartid` in the EFI device tree. Final entry disables the MMU by clearing SATP, computes `entrypoint + stext_offset()`, and jumps with a0 = hartid and a1 = FDT address.

State and persistence behavior: static `hartid` stores boot hart discovery until final jump. No other state persists.

Dependencies and integration points: depends on EFI config-table FDT, libfdt, unaligned FDT property reads, RISC-V CSR access, and the RISC-V kernel boot ABI.

Risks and test signals: missing boot hart ID makes boot unsupported. FDT property width must be 32 or 64 bits. Test signals include EFI boot protocol presence, FDT fallback, malformed/missing `/chosen`, zboot weak offset behavior, and successful MMU-off jump.
