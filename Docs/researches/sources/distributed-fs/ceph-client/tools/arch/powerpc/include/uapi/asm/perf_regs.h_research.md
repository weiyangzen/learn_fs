# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/perf_regs.h

## Purpose
Defines PowerPC perf sampled-register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_powerpc_regs` for GPRs, NIP/MSR/ORIG_R3/CTR/LINK/XER/CCR/SOFTE/TRAP/DAR/DSISR/SIER/MMCRA/MMCR0/MMCR2/MMCR3/SIER2/SIER3 plus PVR, and PMU mask helpers `PERF_REG_PMU_MASK*`.

## Control Flow, State, and Persistence
No state; perf uses the enum and masks to request/decode register samples, including PMU-dependent subsets.

## Dependencies and Integration Points
Integrated with PowerPC perf event sampling and register dump code.

## Risks and Test Signals
Risks include changing enum order or PMU mask coverage, which breaks perf ABI. Test signals are perf sample register tests on PMU versions 3.00 and 3.1.
