# File Research: sources/block-storage/cryptsetup/lib/utils_device_locking.c

## Purpose
Implements on-disk/flock-based metadata locking for device and named resource serialization.

## Key Responsibilities
- Creates lock resource names by block-device major/minor or explicit resource name.
- Opens and creates the default LUKS2 lock directory safely.
- Acquires file, block-device, or name-based lock handles.
- Supports shared read locks and exclusive write locks with reference counts.
- Verifies lock resource identity after acquiring locks to handle races with deleted lock files.
- Removes name/block lock resource files when safe.
- Verifies that a locked device fd still matches the locked file or block-device resource.

## Important Details
- Regular file locks use the target file itself where possible, with an NFSv4 workaround.
- Block-device locks use separate files under `DEFAULT_LUKS2_LOCK_PATH`, keyed by `major:minor`.
- Named resource locks use `LN_<name>` files and can be blocking or nonblocking.
- Release logic takes an exclusive nonblocking lock and checks inode identity before unlinking resource files.
- Nested locks are refcounted for devices, but named `crypt_unlock_internal()` asserts no nested locks remain.

## Dependencies
Uses `flock`, openat/mkdirat, stat inode comparison, `utils_device_locking.h`, and device path/handle helpers.
