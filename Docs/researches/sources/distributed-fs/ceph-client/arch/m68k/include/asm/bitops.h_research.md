<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h

## Purpose
This header implements m68k architecture bit operations for the Linux bitops API. It selects instruction forms for ColdFire, 68000-class CPUs, and 68020+ bitfield-capable CPUs.

## Important APIs, Types, And Functions
- Low-level helpers implement set/clear/change/test-and-set/test-and-clear/test-and-change using `bset`, `bclr`, `bchg`, or bitfield instructions.
- Public arch hooks include `arch___set_bit()`, `arch___clear_bit()`, `arch___change_bit()`, and test-and-operation variants.
- `arch_test_bit` and `arch_test_bit_acquire` defer to generic implementations.
- Bit address calculations use `(nr ^ 31) / 8` and `(nr & 7)` to match m68k big-endian bit numbering.

## Control Flow
Compile-time `CONFIG_COLDFIRE` and `CONFIG_CPU_HAS_NO_BITFIELDS` select register, memory, or bitfield instruction implementations. For constant bit numbers on bitfield-capable CPUs, the code still uses shorter memory bit instructions; dynamic indexes use bitfield operations.

## State And Persistence Behavior
Operations mutate caller-supplied bitmaps in memory. The header stores no global state. Memory clobbers are used where assembly updates through address registers rather than explicit memory outputs.

## Dependencies And Integration Points
It must be included through `<linux/bitops.h>` and depends on compiler attributes and barriers. It is used by core kernel bitmap, flags, scheduler, filesystem, networking, and driver code.

## Risks And Edge Cases
Endian-specific bit numbering is central; changing address math would break on-disk and in-memory bitmaps. Atomicity depends on instruction and CPU behavior. Variant selection must match CPU instruction availability or illegal instructions can occur.

## Test Signals
Kernel bitops selftests, bitmap tests, ext/filesystem bitmap operations, lock bit operations, and cross-builds for ColdFire, 68000/no-bitfield, and 68020+ configs validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bitops.h -->
