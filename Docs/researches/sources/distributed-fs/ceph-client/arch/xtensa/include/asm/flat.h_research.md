<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h

## Purpose
Provides FLAT binary relocation access helpers for noMMU Xtensa.

## Important APIs, Types, And Functions
Defines `flat_get_addr_from_rp` and `flat_put_addr_at_rp`.

## Control Flow
The helpers use unaligned loads/stores to read or write 32-bit relocation addresses at the relocation pointer and return success.

## State And Persistence
State is the relocated binary image in memory. No durable persistence.

## Dependencies And Integration Points
Depends on `linux/unaligned.h` and the generic binfmt_flat loader.

## Risks And Edge Cases
The helpers ignore `relval` and flags, which is correct only for this FLAT relocation format. User pointer casts are forced and rely on loader-controlled memory.

## Test Signals
Run noMMU FLAT binary load/relocation tests, including unaligned relocation pointer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/flat.h -->
