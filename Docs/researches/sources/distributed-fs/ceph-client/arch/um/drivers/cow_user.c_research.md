<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c

Purpose: implements UML COW disk-image header creation and parsing for UBD. It supports historical COW header versions, endian conversion, backing-file validation data, bitmap/data layout computation, and initialization of sparse COW image files.

Important APIs/types/functions: persistent structures are `cow_header_v1`, `cow_header_v2`, `cow_header_v3`, broken 64-bit `cow_header_v3_broken`, and `union cow_header`. Public functions are `cow_sizes()`, `write_cow_header()`, `file_reader()`, `read_cow_header()`, and `init_cow_file()`. `absolutize()` canonicalizes backing-file paths.

Control flow: `write_cow_header()` seeks to offset 0, allocates a v3 header, stores magic/version/backing path/mtime/size/sectorsize/alignment/cow_format in big-endian form, and writes it. `read_cow_header()` reads a full union, detects native or big-endian magic, dispatches version 1/2/3/broken-v3 layouts, computes offsets, and duplicates the backing path. `init_cow_file()` writes the header, calculates bitmap/data offsets, seeks to the final byte of the virtual data area, and writes one zero byte to size the sparse image.

State and persistence: state is host-file persistent COW metadata plus zeroed bitmap/data extents. No global runtime state exists.

Dependencies and integration points: depends on libc `pread`, endian helpers, UML COW system wrappers, `os_file_modtime()`, and UBD's COW open/read/write path.

Risks: this is an on-disk format compatibility surface. Incorrect packing, endian conversion, broken-v3 detection, or path canonicalization can make old images unreadable or point at the wrong backing file. `absolutize()` temporarily changes cwd and must restore it.

Test signals: create v3 COW files, read v1/v2/v3 and broken-v3 fixtures, verify backing-file path/mtime/size mismatch detection in UBD, test long path rejection, sparse EOF sizing, sector/alignment variations, and host endian portability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/cow_user.c -->
