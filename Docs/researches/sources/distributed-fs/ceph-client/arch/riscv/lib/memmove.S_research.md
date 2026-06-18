<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S

## Purpose
`memmove.S` implements overlap-safe RISC-V memory copying with forward and reverse paths.

## Important APIs, Types, And Functions
`__memmove` is the main symbol, with weak `memmove` and `__pi_memmove` aliases. Internal labels implement byte copy, co-aligned word copy, and misaligned fixup copy in both directions.

## Control Flow
The function returns immediately for identical pointers or zero length. It decides forward vs reverse based on source/destination order, byte-copies small ranges, aligns destination, then uses co-aligned word loops or shift-combine loops for misaligned source. Reverse paths copy from the end to preserve overlapping source bytes.

## State And Persistence
It writes destination memory and stores no state.

## Dependencies And Integration Points
It depends on little-endian shift direction, RISC-V calling convention, `SZREG`, and early boot aliases.

## Risks
The file explicitly notes big-endian would require reversed shifts. Overlap correctness depends on exact direction selection and tail byte loops. Misaligned fixup loops are complex and sensitive to off-by-one endpoints.

## Test Signals
Randomized overlap tests across all alignments and lengths, early boot use, and lib/string selftests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S -->
