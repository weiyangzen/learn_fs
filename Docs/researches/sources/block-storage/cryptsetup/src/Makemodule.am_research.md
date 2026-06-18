# File Research: sources/block-storage/cryptsetup/src/Makemodule.am

## Purpose
Defines automake build targets for the `cryptsetup`, `veritysetup`, and `integritysetup` command-line programs.

## Key Responsibilities
- Lists source files for each tool when its build conditional is enabled.
- Adds each enabled tool to `sbin_PROGRAMS`.
- Links each tool with `libcryptsetup.la` and relevant external libraries.
- Defines static variants when `STATIC_TOOLS` is enabled.
- Adds static crypto, pwquality, and devmapper libraries to static link lines where needed.

## Important Details
- All three tools share common utility sources: `lib/utils_crypt.c`, `lib/utils_loop.c`, `lib/utils_io.c`, `lib/utils_blkid.c`, and several `src/utils_*` files.
- `cryptsetup` links password quality libraries; `veritysetup` has a smaller dependency set; `integritysetup` links UUID and blkid.
- Static target source lists mirror their dynamic counterparts.
