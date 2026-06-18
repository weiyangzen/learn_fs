# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_sdiv.c

## Purpose
`verifier_sdiv.c` validates signed BPF division and modulo instructions for 32-bit and 64-bit operands. It covers immediate and register divisors, positive and negative signs, zero divisors, `INT_MIN`/`LLONG_MIN` overflow with `-1`, and x86 translation rewrites for safe overflow handling.

## Important APIs, Types, and Functions
The file is conditionally compiled for architectures and compiler versions that support CPU v4 signed division/modulo syntax in inline assembly. It uses `<limits.h>` for `INT_MIN` and `LLONG_MIN`, `SEC("socket")` BPF program sections, `__naked` exact assembly, and `__retval` contracts. x86-specific tests include `__arch_x86_64` and multiple `__xlated` expectations to validate verifier/JIT lowering. If the architecture, JIT, or Clang version is unsupported, a dummy successful socket test is emitted instead.

## Control Flow
Most programs are tiny straight-line arithmetic fixtures: load constants into `w0` or `r0`, perform `s/=` or `s%=` with either an immediate or another register, then exit. Zero-divisor tests initialize a divisor register to zero and verify the defined BPF result semantics. Overflow tests preserve the original dividend, execute signed division or modulo by `-1`, and compare or return the result to assert the verifier's rewrite behavior.

## State and Persistence
The file has no persistent maps or external state. State exists only in BPF registers and in compile-time test metadata. The signed arithmetic semantics are deterministic for each program, so return values and translated instruction sequences are the persistence-like contract for regression detection.

## Dependencies and Integration Points
Dependencies include the BPF assembler accepted by Clang, target architecture feature macros, libbpf helper macros, and verifier support for signed ALU operations. It integrates directly with the selftest runner through pass/fail metadata, return-value execution, unprivileged success markers for many simple cases, and translated instruction matching.

## Risks and Test Signals
Risks are high for arithmetic edge cases because C-like signed division overflow is undefined on many platforms while BPF must define verifier and JIT behavior. Incorrect rewrites could return wrong values, trap, or diverge between interpreter and JIT. Test signals include exact `__retval` values for sign rounding toward zero, zero-divisor behavior, modulo sign rules, overflow preservation for min-int divided by `-1`, and `__xlated` sequences that show inserted checks around divisor `-1` and zero.
