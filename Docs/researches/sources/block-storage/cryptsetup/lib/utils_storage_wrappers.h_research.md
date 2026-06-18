# File Research: sources/block-storage/cryptsetup/lib/utils_storage_wrappers.h

## Purpose
Declares the generic storage wrapper interface.

## Key Responsibilities
- Defines flags controlling kernel crypto, dm-crypt fallback, read-only opens, large IVs, locked opens, and dm-crypt-only mode.
- Defines wrapper types: `NONE`, `USPACE`, and `DMCRYPT`.
- Declares initialization, destruction, raw/read-decrypt/decrypt/write/encrypt-write, datasync, and type accessor functions.

## Important Details
- Documents that all read/write offsets passed to wrapper functions are relative to `data_offset`.
