
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/loongarch-stub.c

Purpose: implements LoongArch EFI stub kernel relocation from firmware-loaded image memory to an architecture-acceptable aligned physical location.

Important APIs/types/functions: exports `handle_kernel_image()` and `kernel_entry_address()`. Internal `efi_relocate_kernel()` allocates at `EFI_KIMG_PREFERRED_ADDRESS` or lowest suitable memory and copies the kernel file image.

Control flow: `handle_kernel_image()` derives the firmware image base, relocates `kernel_fsize` bytes into an allocation of `kernel_asize`, updates `image_addr` and `image_size`, and returns status. `kernel_entry_address()` converts the linked `kernel_entry` symbol offset from the original image base to the relocated base.

State and persistence behavior: uses linker-provided `kernel_asize`, `kernel_fsize`, and `kernel_entry` symbols. The relocated allocation persists into kernel entry; no global persistent state is added.

Dependencies and integration points: depends on LoongArch address/cache helpers, `efi_low_alloc_above()`, EFI page allocation, and the common stub `handle_kernel_image()` contract.

Risks and test signals: preferred-address allocation may fail, fallback must respect alignment, and image sizes must match linker/header data. Test signals include preferred-address success/failure, low allocation fallback, copied image checksum/entry offset, and cache sync before execution.
