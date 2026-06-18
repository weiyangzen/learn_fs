# File Research: sources/block-storage/cryptsetup/lib/utils_wipe.c

## Purpose
Implements device wiping, including zero/random/special patterns and OPAL hardware erase integration.

## Key Responsibilities
- Uses `BLKZEROOUT` for block-device zero wipes when available.
- Implements the Gutmann special wipe pattern for rotational media.
- Writes wipe blocks with aligned blockwise I/O.
- Provides `crypt_wipe_device()` for internal device objects.
- Provides public `crypt_wipe()` for paths or the crypt device data device.
- Supports progress callbacks and interruption.
- Syncs devices after wiping.
- Implements OPAL PSID/factory reset or segment reset plus LUKS2 header-area wipe.

## Important Details
- All offsets, lengths, and wipe block sizes must be 512-byte aligned.
- Non-rotational devices downgrade special wipe to random wipe.
- Random wipe refreshes block contents each iteration.
- Zeroout ioctl availability is cached and disabled after first failure.
- OPAL segment wipe validates segment range and uses an exclusive OPAL lock.

## Dependencies
Uses device helpers, random generation, blockwise I/O, LUKS2 internals, and OPAL helper APIs.
