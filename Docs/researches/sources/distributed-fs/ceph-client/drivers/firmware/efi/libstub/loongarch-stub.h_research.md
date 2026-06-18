
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.h

Purpose: declares the LoongArch stub helper for deriving the relocated kernel entry address.

Important APIs/types/functions: declares `kernel_entry_address(unsigned long kernel_addr, efi_loaded_image_t *image)`.

Control flow: no executable flow. The declaration lets LoongArch common boot code call either the strong implementation from `loongarch-stub.c` or the weak fallback in `loongarch.c`.

State and persistence behavior: no state.

Dependencies and integration points: depends on `efi_loaded_image_t` from `efistub.h` being visible before inclusion. It connects LoongArch relocation and final boot handoff code.

Risks and test signals: prototype mismatch would break LoongArch EFI builds. Test signal is successful linked builds with both normal and zboot LoongArch paths.
