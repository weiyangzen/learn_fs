# File Research: sources/block-storage/cryptsetup/lib/utils_device_locking.h

## Purpose
Declares internal metadata locking primitives for devices and named resources.

## Key Responsibilities
- Exposes lock state queries.
- Declares internal read/write device lock and unlock functions.
- Declares locked-fd verification.
- Declares named write lock/unlock functions.
- Declares device lock-handle setters/getters used by `utils_device.c`.

## Important Details
- The API is internal and intentionally works with opaque `crypt_lock_handle` and `device` types.
