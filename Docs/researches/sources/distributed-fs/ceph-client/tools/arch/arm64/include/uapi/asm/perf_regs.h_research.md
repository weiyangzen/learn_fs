# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/perf_regs.h

## Purpose
Defines arm64 perf sample register indexes for user and tools code.

## Important APIs, Types, and Functions
Exports `enum perf_event_arm_regs` for X0-X30/LR/SP/PC and pseudo register `PERF_REG_ARM64_VG` for SVE vector granule. `PERF_REG_EXTENDED_MASK` marks the extended pseudo register.

## Control Flow, State, and Persistence
No state or control flow; perf records and consumers use enum indexes to request and decode register samples.

## Dependencies and Integration Points
Integrated with perf event `sample_regs_user`/`sample_regs_intr` masks and arm64 register dump code.

## Risks and Test Signals
Risk is enum numbering drift, especially the sparse `VG = 46` extended slot. Test signals are perf register mask tests, SVE VG sample decode, and user/kernel header consistency checks.
