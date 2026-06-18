
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/riscv-stub.c

Purpose: implements RISC-V EFI stub image sizing, optional KASLR relocation, and instruction cache synchronization for the kernel-linked EFI stub.

Important APIs/types/functions: exports `stext_offset()`, `handle_kernel_image()`, and `efi_icache_sync()`.

Control flow: `stext_offset()` returns the actual kernel text entry offset because the PE/COFF header is not part of the in-memory kernel presentation. `handle_kernel_image()` derives text/data/BSS sizes from linker symbols, sets image/reserve sizes, and calls `efi_kaslr_relocate_kernel()` with an EFI RNG physical seed. `efi_icache_sync()` emits `fence.i`.

State and persistence behavior: only updates caller-provided image and reserve addresses/sizes. Relocated memory persists to kernel entry.

Dependencies and integration points: depends on RISC-V linker symbols, common KASLR relocation, EFI RNG, and the RISC-V instruction cache fence. Used by the normal RISC-V EFI boot path.

Risks and test signals: linker symbol ranges must match actual image layout, and `fence.i` must run after copying executable code. Test signals include RISC-V EFI boot with KASLR enabled/disabled, relocation failure path, correct entry offset, and decompressed image execution.
