
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/zboot-decompress-zstd.c

Purpose: provides Zstandard payload decompression for EFI zboot images.

Important APIs/types/functions: exports `efi_zboot_decompress_init()` and `efi_zboot_decompress()`. Uses Zstd decompressor workspace tracked in static `wksp_size` and `wksp`.

Control flow: init computes workspace bound, allocates EFI pages, and returns `payload_size`. Decompress initializes a Zstd context in that workspace, decompresses from `_gzdata_start` to `_gzdata_end - 4`, frees the workspace, checks the Zstd error code, syncs the instruction cache, and reports EFI load errors on failure.

State and persistence behavior: workspace state is transient between init and decompress. Output buffer persists to zboot common boot.

Dependencies and integration points: depends on Linux Zstd decompressor sources, EFI page allocation/free, compressed payload linker symbols, and arch cache sync.

Risks and test signals: the `- 4` input-size adjustment must match zboot payload layout, and workspace must not be reused after free. Test signals include valid/corrupt Zstd images, allocation failure, payload size checks, and instruction-cache coherency.
