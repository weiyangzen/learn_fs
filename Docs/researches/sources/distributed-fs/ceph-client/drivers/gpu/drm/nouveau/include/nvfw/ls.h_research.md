
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/ls.h

## Purpose
Defines light-secure firmware descriptors and high-secure bootloader wrapper headers.

## Important APIs, types, and functions
- `struct nvfw_ls_desc_head` captures common descriptor metadata, date, bootloader offsets, app offsets, and resident code/data regions.
- `struct nvfw_ls_desc`, `nvfw_ls_desc_v1`, and `nvfw_ls_desc_v2` add overlay counts, overlay start/size arrays, compression, and secure bootloader flag variants.
- Parser prototypes return typed descriptors from a firmware blob.
- `struct nvfw_ls_hsbl_bin_hdr` and `nvfw_ls_hsbl_hdr` describe HS bootloader binary/header metadata and signatures.

## Control flow
The header is declarative. Firmware parsing code selects a descriptor version, reads overlay and app layout, and uses HSBL headers when a light-secure image is wrapped by a high-secure bootloader.

## State and persistence
No live state exists. Descriptors mirror persistent firmware metadata and are used transiently during firmware load.

## Dependencies and integration points
Includes `core/os.h` and forward declares `struct nvkm_subdev`. It integrates with `fw.h`, `flcn.h`, and ACR/LS falcon loaders.

## Risks
The `load_ovl[64]` arrays and overlay counts must be bounds-checked by parsers. Descriptor versions differ subtly, especially around secure bootloader and IMEM/DMEM overlay counts. Incorrect resident region offsets can break falcon boot.

## Test signals
Firmware parsing for LS descriptor versions 0/1/2, compressed and overlay-heavy images, and HSBL-wrapped images should be validated.
