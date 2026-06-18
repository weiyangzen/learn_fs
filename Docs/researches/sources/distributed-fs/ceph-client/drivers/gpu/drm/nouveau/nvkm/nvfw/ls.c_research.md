# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/ls.c

## Purpose
Parses and logs low-secure firmware descriptors and secure bootloader signature headers used in ACR WPR images.

## Important APIs, types, and functions
`nvfw_ls_desc()`, `_v1()`, and `_v2()` expose bootloader/app offsets, sizes, resident code/data layout, overlay counts, secure bootloader metadata, and app IMEM/DMEM offsets. `nvfw_ls_hsbl_bin_hdr()` and `nvfw_ls_hsbl_hdr()` parse HS bootloader signature containers.

## Control flow, state, and persistence
The helpers log descriptor fields and return typed pointers. They allocate only temporary strings for dates and free them immediately. No firmware state is persisted here.

## Dependencies and integration points
Used by `subdev/acr/lsfw.c` to convert firmware descriptors into `nvkm_acr_lsfw` layout. Depends on `nvfw/ls.h` and subdev logging.

## Risks and test signals
Descriptor interpretation feeds WPR layout and secure signature patching. Test signals include debug dumps, WPR comparison output, and successful low-secure falcon bootstrap.
