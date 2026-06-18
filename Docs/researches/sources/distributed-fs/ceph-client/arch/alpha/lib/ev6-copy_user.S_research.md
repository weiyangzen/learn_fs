# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-copy_user.S

## Purpose
EV6-optimized `__copy_user` with fault recovery and residual count semantics. The source was read as part of `subset-b-000628` and contains 227 lines.

## Important APIs, Types, and Functions
Exports `__copy_user` for EV6 builds.

## Control Flow
Chooses alignment-specific copy loops, uses EV6 scheduling/cache hints for aligned blocks, handles byte heads/tails, and exception-table branches preserve the number of bytes not copied on source or destination faults.

## State and Persistence Behavior
Reads source, writes destination, returns residual byte count, and emits exception-table entries.

## Dependencies
Depends on Alpha uaccess ABI, EV6 instruction scheduling, Makefile EV6 selection, and callers in `copy_to_user`/`copy_from_user` wrappers.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Residual count, source fault, and destination fault paths are ABI-visible. Optimized unaligned paths can corrupt neighboring bytes if masks are wrong.

## Test Signals
Run usercopy fault-injection and alignment tests on EV6 config, validate return counts, and stress filesystem/network syscalls that copy user buffers.
