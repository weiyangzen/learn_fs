# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/perf_regs.h

## Purpose
Defines x86 register IDs used by perf sample register masks and user-space perf tooling.

## APIs, Types, and Functions
Exports `enum perf_event_x86_regs`, covering GPRs, segment registers, flags, instruction pointer, and XMM registers. Defines limits `PERF_REG_X86_32_MAX`, `PERF_REG_X86_64_MAX`, `PERF_REG_X86_XMM_MAX`, and `PERF_REG_EXTENDED_MASK`.

## Control Flow, State, and Persistence
No runtime flow. Enum values are ABI indices; XMM registers intentionally consume two bits each because they are 128-bit values.

## Dependencies and Integration
Included by perf event UAPI users. The IDs must match kernel perf register capture and user-space decoding.

## Risks and Test Signals
Risks include changing enum order, mishandling XMM two-bit mask allocation, and mixing 32-bit and 64-bit max values. Test signals are perf register sampling tests, mask validation for extended registers, and cross-ABI builds.
