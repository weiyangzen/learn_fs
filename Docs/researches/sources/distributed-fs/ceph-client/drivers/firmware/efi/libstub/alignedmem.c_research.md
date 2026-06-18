# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/alignedmem.c

Purpose: provides aligned EFI page allocation for the boot stub, returning an allocation base that satisfies architecture alignment while staying below a maximum address.

Important APIs/types/functions: defines `efi_allocate_pages_aligned(size, addr, max, align, memory_type)`.

Control flow: the allocator clamps `max` to `EFI_ALLOC_LIMIT`, raises `align` to at least `EFI_ALLOC_ALIGN`, rounds `size`, requests extra slack pages with `EFI_ALLOCATE_MAX_ADDRESS`, aligns the returned address upward, and frees unused leading/trailing slack pages around the aligned usable region.

State and persistence behavior: no file-local state; allocated EFI pages persist until the caller frees them or boot services exit.

Dependencies and integration points: used by EFI stub image allocation paths and depends on `efi_bs_call(allocate_pages/free_pages)`, EFI page sizing, and architecture alignment constants.

Risks and test signals: slack calculations must not free pages inside the aligned result or leak pages outside it. Test signals include aligned kernel/initrd allocations under varied firmware allocation bases and successful boot with large alignment requirements.
