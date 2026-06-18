# sources/distributed-fs/ceph-client/include/linux/kasan-tags.h

## Purpose
Defines common KASAN pointer/memory tag constants used by software and hardware tag-based modes.

## Important APIs, Types, And Functions
Constants include `KASAN_TAG_KERNEL` for native kernel pointers, `KASAN_TAG_INVALID` for inaccessible memory, `KASAN_TAG_MAX`, and `KASAN_TAG_MIN`. Hardware tag mode raises the random tag minimum to `0xF0`; other modes use `0x00`.

## Control Flow
There is no runtime flow. `CONFIG_KASAN_HW_TAGS` selects the minimum random tag value at compile time.

## State And Persistence
No state is stored. These constants parameterize tag generation and validation elsewhere.

## Dependencies And Integration Points
Used by KASAN allocation, poisoning, and tag reset code. It is included by `kasan.h`.

## Risks
Changing constants can break tag ABI assumptions and invalid memory detection. Hardware and software tag ranges differ, so shared code must not hard-code a single minimum.

## Test Signals
Tag generation tests should confirm invalid/kernel tags are avoided or used as intended, random tag ranges differ by mode, and poisoned memory reports identify invalid tags.
