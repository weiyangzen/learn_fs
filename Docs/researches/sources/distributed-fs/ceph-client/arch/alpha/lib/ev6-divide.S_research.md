# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-divide.S

## Purpose
EV6-optimized software divide/remainder source used to build Alpha arithmetic helper variants. The source was read as part of `subset-b-000628` and contains 263 lines.

## Important APIs, Types, and Functions
Defines/export symbols via `ufunction` and `sfunction` for `__divqu`, `__remqu`, `__divlu`, and `__remlu` objects selected by the Makefile.

## Control Flow
Like generic `divide.S`, assembler defines choose divide versus remainder and long versus quad size. The EV6 version uses scheduling better suited to 21264 pipelines while preserving signed/unsigned semantics.

## State and Persistence Behavior
No persistent state; input registers produce quotient or remainder outputs.

## Dependencies
Depends on Makefile flags, EV6 build selection, compiler-emitted arithmetic helper references, and Alpha calling convention.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
All generated variants share one source and must remain ABI-compatible with generic helpers. Signed edge cases and divide-by-zero expectations are high risk.

## Test Signals
Run arithmetic differential tests across the four generated objects on EV6 config, include signed min/-1 and zero divisor cases expected by kernel callers, and verify no generic divide symbols are missing.
