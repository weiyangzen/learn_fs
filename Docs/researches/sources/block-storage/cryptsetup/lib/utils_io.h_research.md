# File Research: sources/block-storage/cryptsetup/lib/utils_io.h

## Purpose
Declares cryptsetup’s low-level buffered and blockwise I/O helpers.

## Key Responsibilities
- Declares exact-length read/write helpers.
- Declares interruptible read/write helpers.
- Declares blockwise read/write helpers and lseek-plus-blockwise variants.

## Important Details
- The API passes block size and memory alignment explicitly, letting device code supply topology-derived values.
