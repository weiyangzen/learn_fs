# sources/distributed-fs/ceph-client/arch/x86/kernel/perf_regs.c

## Purpose
Maps x86 `pt_regs` and optional XMM register state into perf sample register values, validates user-requested perf register masks, and supplies user register snapshots for perf, including NMI-safe 64-bit handling.

## APIs, Types, And Functions
Core data is `pt_regs_offset[PERF_REG_X86_MAX]`. Public functions are `perf_reg_value()`, `perf_reg_validate()`, `perf_reg_abi()`, and `perf_get_regs_user()`. On 64-bit, per-CPU `nmi_user_regs` stores a partial NMI-safe copy.

## Control Flow
`perf_reg_value()` returns XMM values from `struct x86_perf_regs` when requested or otherwise reads from `pt_regs` using the offset table. `perf_reg_validate()` rejects empty masks, unsupported architecture-specific register bits, and reserved bits. `perf_reg_abi()` reports 32-bit or 64-bit ABI based on task mode. `perf_get_regs_user()` normally points perf at `task_pt_regs(current)`; in NMI context on 64-bit it first checks whether the NMI interrupted `task_pt_regs` setup and otherwise copies only reliably saved user registers into per-CPU storage.

## State And Persistence
The offset table is static. The per-CPU NMI copy is transient sample state and overwritten on each NMI sampling path. No persistent storage is created.

## Dependencies And Integration
Depends on perf event sampling, `asm/perf_regs.h`, ptrace register layout, task stack layout, user mode detection, and x86 FPU/XMM perf extensions.

## Risks And Test Signals
Register layout drift can corrupt perf samples. NMI sampling is especially fragile because it may interrupt syscall or interrupt entry while user regs are being constructed. Test signals include perf record/report register samples on 32-bit, 64-bit, and compat tasks, validation of rejected masks, and NMI PMU sampling under syscall-heavy workloads.
