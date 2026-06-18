<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow.h

Purpose: declares the UML COW disk-image format helpers used by the UBD block driver. The helpers create, read, and size copy-on-write image headers and bitmap/data regions.

Important APIs/types/functions: exported functions are `init_cow_file()`, `file_reader()`, `read_cow_header()`, `write_cow_header()`, and `cow_sizes()`. The API returns backing-file path, mtime, virtual size, sector size, alignment, bitmap offset/length, and data offset.

Control flow: UBD calls `read_cow_header()` to detect COW images and validate backing files, `write_cow_header()` when switching or creating COW files, and `cow_sizes()` to compute bitmap/data placement.

State and persistence: this header describes persistent COW-image metadata stored in host files, but owns no state itself.

Dependencies and integration points: depends on `asm/types.h` and COW implementation in `cow_user.c`; UBD uses it for COW-backed block devices.

Risks: function signatures are part of the storage driver's internal ABI. Type sizes and endian assumptions must match the on-disk COW format implementation.

Test signals: compile UBD with COW enabled, create/read COW images, validate bitmap/data offsets, and exercise old COW header versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow.h -->
