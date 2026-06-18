# sources/distributed-fs/ceph-client/arch/mips/kernel/perf_regs.c

## Purpose
Provides perf sampled-register support for MIPS. It reports the task ABI for sampled user registers, validates register masks, extracts selected registers from `struct pt_regs`, and wires user register sampling to the current task's saved pt_regs.

## Important APIs, Types, and Functions
- `perf_reg_abi()` returns `PERF_SAMPLE_REGS_ABI_32` on 32-bit kernels or for 32-bit-reg tasks on 64-bit kernels, otherwise `PERF_SAMPLE_REGS_ABI_64`.
- `perf_reg_validate()` rejects empty masks and masks with bits outside `PERF_REG_MIPS_MAX`.
- `perf_reg_value()` maps perf register indexes to `cp0_epc`, general registers r1-r25 and r28-r31, warning on unsupported indexes.
- `perf_get_regs_user()` fills `struct perf_regs` with `task_pt_regs(current)` and the ABI.

## Control Flow
The perf core calls these helpers when processing `PERF_SAMPLE_REGS_USER`/register masks. Validation occurs before sampling. During sample formatting, each requested index is translated from perf's compact MIPS register namespace to `pt_regs` fields and sign-extended through an `s64` return.

## State and Persistence
No persistent state. It reads task flags and pt_regs only at sample time.

## Dependencies and Integration Points
Depends on MIPS ptrace register layout, `TIF_32BIT_REGS`, `PERF_REG_MIPS_*` constants, and perf's generic sampled register ABI. It complements `ptrace.c`/`process.c` register dump helpers but intentionally exposes a perf-specific subset.

## Risks
Register namespace drift between perf constants and `pt_regs` layout would produce incorrect samples. Unsupported registers warn once and return zero, so mask validation must remain strict. Sign extension is intentional for 32-bit tasks but can surprise consumers expecting zero-extended values.

## Test Signals
Perf record/report with sampled user registers should show PC and requested GPRs for both 32-bit and 64-bit tasks. Invalid masks should return `-EINVAL`. ABI values in perf samples should match the traced task's execution mode.
