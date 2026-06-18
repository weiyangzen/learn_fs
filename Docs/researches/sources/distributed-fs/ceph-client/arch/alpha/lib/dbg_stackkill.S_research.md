# sources/distributed-fs/ceph-client/arch/alpha/lib/dbg_stackkill.S

## Purpose
Debug `_mcount` hook that poisons unused Alpha kernel stack space with `0xdeadbeefdeadbeef` to expose uninitialized stack-variable use. The source was read as part of `subset-b-000628` and contains 36 lines.

## Important APIs, Types, and Functions
Defines global `_mcount`; uses `STACK_SIZE` and `TASK_SIZE` from `asm/asm-offsets.h`.

## Control Flow
The hook builds the 64-bit poison value, aligns from the current stack region toward the active stack pointer, writes the poison pattern in 8-byte steps up to `$30`, and returns through `$28`.

## State and Persistence Behavior
Mutates currently unused stack memory below the active frame. It creates diagnostic stack contents but no persistent global state.

## Dependencies
Depends on Alpha `_mcount` instrumentation, task stack layout constants, and callers tolerating stack poisoning during debug builds.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Wrong stack bounds can corrupt live frames or miss unused stack space. Because it runs from `_mcount`, overhead is high and it must stay confined to debug configurations.

## Test Signals
Build the stack-kill debug configuration, verify stack gaps contain the poison pattern after instrumented calls, run workloads that previously used uninitialized locals, and confirm production configs do not select this object.
