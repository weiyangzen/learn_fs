# File Research: sources/block-storage/cryptsetup/lib/utils_loop.h

## Purpose
Declares loopback block-device helper APIs.

## Key Responsibilities
- Declares backing-file lookup, loop-device detection, attach, detach, and resize functions.

## Important Details
- `crypt_loop_attach()` returns an open loop fd on success and fills the selected loop path.
