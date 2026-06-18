
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot.c

Purpose: implements the EFI zboot entry point that decompresses a compressed kernel payload into EFI memory and then runs the shared EFI stub common path on the decompressed image.

Important APIs/types/functions: exports weak `efi_cache_sync_image()`, `alloc_primary_display()`, and `efi_zboot_entry()`. Internal `alloc_preferred_address()` tries an architecture preferred kernel image address.

Control flow: entry records the EFI system table, obtains Loaded Image Protocol, handles command line/options, initializes decompressor to get allocation size, tries preferred address, otherwise obtains RNG seed when KASLR is enabled and uses `efi_random_alloc()`, decompresses into the allocation, calls `efi_stub_common()`, and frees the allocation on return/failure.

State and persistence behavior: writes global `efi_system_table`; image allocation persists only until common stub returns, but successful boot does not return. Primary display allocation is routed through the config-table approach.

Dependencies and integration points: depends on zboot decompressor backends, EFI Loaded Image Protocol, common command-line and stub code, random allocation, arch image alignment/cache hooks, and optional preferred address.

Risks and test signals: allocation must match decompressed payload size and alignment, RNG failures disable KASLR, and returned failure must free the decompressed image. Test signals include gzip/zstd zboot, preferred address success/failure, KASLR disabled/enabled, EFI_RNG unavailable, and handoff through common stub with initrd/FDT/GOP.
