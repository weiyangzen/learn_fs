# sources/distributed-fs/ceph-client/net/ceph/crush/hash.c

## Purpose
Implements deterministic CRUSH hash functions used by bucket selection and device-out checks.

## Important APIs, Types, and Functions
Public functions are `crush_hash32()`, `crush_hash32_2()`, `crush_hash32_3()`, `crush_hash32_4()`, `crush_hash32_5()`, and `crush_hash_name()`. Internal functions implement the `CRUSH_HASH_RJENKINS1` variant for one through five 32-bit inputs. `crush_hashmix` is the Jenkins mixing macro and `crush_hash_seed` is the fixed seed.

## Control Flow
Each dispatcher switches on hash type and calls the matching Jenkins function or returns 0 for unknown types. The Jenkins variants combine the fixed seed and arguments, then apply several mixing rounds with constants to produce a 32-bit deterministic result.

## State and Persistence
No mutable state. Hash stability is required for placement consistency.

## Dependencies and Integration Points
Used by `mapper.c` bucket selection, permutation generation, straw/straw2 draws, and `is_out()` probability checks. Must match userspace CRUSH exactly.

## Risks
Unknown hash types silently return 0, which can bias placement if invalid maps pass validation. Any arithmetic or seed change causes cluster-wide remapping. The code relies on unsigned 32-bit wraparound semantics.

## Test Signals
Known-answer vectors for all arities, unknown type behavior, cross-implementation comparison with userspace Ceph, and placement regression tests using real CRUSH maps.
