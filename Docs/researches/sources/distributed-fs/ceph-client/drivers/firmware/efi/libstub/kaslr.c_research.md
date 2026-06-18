
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/kaslr.c

Purpose: obtains EFI RNG seed material for physical KASLR and relocates kernel images to either randomized or safe aligned physical memory.

Important APIs/types/functions: exports `efi_kaslr_get_phys_seed()` and `efi_kaslr_relocate_kernel()`. Internal `check_image_region()` detects loader-provided images whose BSS crosses EFI memory descriptors.

Control flow: seed acquisition checks `CONFIG_RANDOMIZE_BASE`, `efi_nokaslr`, and the fixed-placement protocol, then uses `efi_get_random_bytes()` or disables KASLR on failure. Relocation first attempts `efi_random_alloc()` when seeded. On failure it may execute in place if placement/alignment/BSS coverage are acceptable, otherwise allocates aligned pages, copies image bytes, updates `image_addr`, syncs instruction cache, and remaps code/data permissions.

State and persistence behavior: modifies caller-owned image/reserve addresses and global `efi_nokaslr` on RNG failure. Relocated pages persist into kernel entry; original allocations are handled by architecture code.

Dependencies and integration points: depends on EFI RNG, memory map helpers, `efi_random_alloc()`, `efi_allocate_pages_aligned()`, arch image alignment, cache sync, and `efi_remap_image()`. Used by RISC-V and similar non-x86 stubs.

Risks and test signals: risk includes weak/no RNG, fixed loader placement, GRUB BSS allocation bugs, incorrect minimum alignment, and copy/remap failures. Test signals include KASLR enabled/disabled command lines, fixed placement protocol, RNG unavailable, image already aligned in place, BSS overlap diagnostics, and successful randomized relocations.
