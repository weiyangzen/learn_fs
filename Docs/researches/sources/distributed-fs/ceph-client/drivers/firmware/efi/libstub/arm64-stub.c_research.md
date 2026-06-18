# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/arm64-stub.c

Purpose: handles arm64 kernel image validation, KASLR relocation, entry offset calculation for in-kernel stubs, and instruction-cache synchronization.

Important APIs/types/functions: defines `handle_kernel_image()`, `primary_entry_offset()`, and `efi_icache_sync()`.

Control flow: `handle_kernel_image()` corrects bogus firmware `image_base`, warns on segment misalignment, calculates kernel file/code/memory sizes from linker symbols, seeds KASLR from the EFI handle, and delegates relocation to `efi_kaslr_relocate_kernel()`. `primary_entry_offset()` returns the true `primary_entry` offset because the PE/COFF header may not be present in the in-memory kernel image. `efi_icache_sync()` cleans/invalidates caches to point of unification.

State and persistence behavior: no persistent state; relocation outputs reserve/image addresses for common stub handling.

Dependencies and integration points: depends on arm64 linker symbols, KASLR stub helpers, cache maintenance, EFI loaded image protocol, and common stub entry flow.

Risks and test signals: incorrect image-base handling, segment alignment, or code/memory size calculation can break relocation or execution permissions. Test signals include KASLR-enabled EFI boot, warning on bad firmware image base without boot failure, and correct branch into `primary_entry`.
