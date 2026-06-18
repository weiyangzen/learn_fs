# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_current.S

## Purpose
Profiling/debug `_mcount` hook that traps if the Alpha `current` pointer and stack pointer relationship is inconsistent. The source was read as part of `subset-b-000628` and contains 30 lines.

## Important APIs, Types, and Functions
Defines global `_mcount`; it uses `PAL_bugchk` from `asm/pal.h` as the failure path.

## Control Flow
The hook computes `sp - 0x4000`, checks whether the stack pointer lies within the expected current task stack window relative to register `$8`, and returns through `$28` when valid. If the check fails, it invokes the PAL bugcheck call.

## State and Persistence Behavior
Reads the stack pointer and `$8` current/task register state only; failure enters firmware/kernel bugcheck handling. It does not store persistent data.

## Dependencies
Depends on Alpha profiling instrumentation naming `_mcount`, the convention that `$8` tracks current task state, stack-size assumptions, and PAL `PAL_bugchk`.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The hard-coded `0x4000` stack window must match the configured Alpha stack layout. If profiling invokes `_mcount` before registers are established, this can false-trigger a PAL bugcheck.

## Test Signals
Build a debug/profiling Alpha configuration that selects this object, boot with function profiling active, confirm normal calls return without PAL bugcheck, and deliberately inspect stack/current invariants under a debugger.
