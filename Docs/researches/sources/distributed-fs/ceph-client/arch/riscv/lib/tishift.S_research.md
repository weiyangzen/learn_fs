<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S

## Purpose
`tishift.S` provides 128-bit integer shift helper routines needed by the compiler on 64-bit RISC-V.

## Important APIs, Types, And Functions
It exports `__lshrti3`, `__ashrti3`, and `__ashlti3` for logical right, arithmetic right, and arithmetic left shifts of TImode values carried in `a1:a0` with shift amount in `a2`.

## Control Flow
Each helper returns unchanged for shift zero, handles shifts below 64 by combining shifted low/high halves, and handles shifts of 64 or more by moving or sign-extending the high/low half into the result.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It is selected for CONFIG_64BIT and satisfies compiler-generated libcalls in kernel code.

## Risks
Wrong sign extension in arithmetic right shift or boundary handling at exactly 64 bits would corrupt compiler-generated 128-bit math.

## Test Signals
Builds that generate `__int128` shifts and arithmetic tests across shift counts 0, 1, 63, 64, 65, and 127 are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S -->
