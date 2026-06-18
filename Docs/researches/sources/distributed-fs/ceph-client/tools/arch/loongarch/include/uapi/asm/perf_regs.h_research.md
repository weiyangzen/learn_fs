# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/perf_regs.h

## Purpose
Defines LoongArch perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_loongarch_regs` for PC and general registers R1-R31, ending at `PERF_REG_LOONGARCH_MAX`.

## Control Flow, State, and Persistence
No state; perf sampling uses enum indexes in register masks and sample payloads.

## Dependencies and Integration Points
Integrated with perf register dumping and LoongArch perf events.

## Risks and Test Signals
Risk is register numbering mismatch with user pt_regs conventions. Test signals are perf sample decode and register-mask build tests.
