# File Research: sources/block-storage/lvm2/lib/device/dev-swap.c

## Purpose
Detects swap and suspend signatures on Linux block devices.

## Core Behavior
`dev_is_swap()` gets the device size, then checks the last 10 bytes of possible page-size regions from 4KiB through 64KiB, skipping 32KiB. It recognizes `SWAP-SPACE`, `SWAPSPACE2`, suspend signatures `S1SUSPEND`, `S2SUSPEND`, `ULSUSPEND`, and a binary suspend signature.

On match it sets `offset_found` to the signature offset and returns 1. It returns 0 for no match and -1 on read/size failure.

## Integration
Used by signature probing to avoid overwriting devices that contain swap or hibernation state.

## Risk Notes
The implementation is Linux-only in this file. The `full` parameter is unused, and detection depends on the expected swap-signature placement for supported page sizes.
