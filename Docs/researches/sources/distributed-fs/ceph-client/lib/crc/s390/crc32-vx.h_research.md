# sources/distributed-fs/ceph-client/lib/crc/s390/crc32-vx.h

## Purpose
This small header declares the s390 z/Architecture Vector Extension Facility CRC32 assembly/C entry points.

## Important APIs, Types, and Functions
It declares `crc32_be_vgfm_16()`, `crc32_le_vgfm_16()`, and `crc32c_le_vgfm_16()`, all accepting an initial CRC, byte buffer, and size.

## Control Flow
No executable flow exists. The arch selector in `crc32.h` calls these functions after alignment and vector-state setup.

## State and Persistence
The header carries no state.

## Dependencies and Integration Points
It depends on `linux/types.h` and is shared by s390 CRC32 selector and vector implementation files.

## Risks and Test Signals
Risks are declaration/definition mismatches and wrong variant wiring. Compile/link tests plus CRC32 KUnit on s390 VX systems are sufficient signals.
