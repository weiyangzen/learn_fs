## sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/entry-fpsimd.S` provides low-level ARM64
assembly routines for saving, loading, sizing, and flushing FPSIMD, SVE, and SME architectural
state. It is the register-movement backend for the higher-level FPSIMD/SVE/SME context-management
code.

### Important APIs, Types, And Functions
Always-present functions are `fpsimd_save_state()` and `fpsimd_load_state()`. Under
`CONFIG_ARM64_SVE`, the file exports `sve_save_state()`, `sve_load_state()`, `sve_get_vl()`,
`sve_set_vq()`, and `sve_flush_live()`. Under `CONFIG_ARM64_SME`, it exports `sme_get_vl()`,
`sme_set_vq()`, `sme_save_state()`, and `sme_load_state()`. Implementation uses macros from
`asm/fpsimdmacros.h` such as `fpsimd_save`, `sve_save`, `sve_load`, `sve_flush_z`,
`sve_flush_p`, `sve_flush_ffr`, `sme_save_za`, and `sme_load_za`.

### Control Flow
The FPSIMD routines simply save or restore the fixed FP/SIMD register file to the supplied
`struct fpsimd_state`. SVE routines save/load vector and predicate state, read or configure vector
length, and flush non-FPSIMD portions of live SVE state during syscall ABI cleanup. SME routines read
or configure streaming vector length and save/load ZA plus optional ZT state.

### State, Persistence, And Dependencies
State is CPU register state and caller-provided memory buffers; no file-local storage exists.
Dependencies include the ARM64 vector architecture, compile-time SVE/SME configuration, CPACR access
having been enabled by C callers, and exact buffer layouts shared with `fpsimd.c`, signal handling,
ptrace, and task context switching.

### Integration Points
`entry-common.c` calls `sve_flush_live()` on syscall entry. FPSIMD/SVE/SME management code uses the
save/load helpers for context switch, signal frame, ptrace, exec, and lazy state management. These
helpers are enabled only after `cpufeature.c` has detected and enabled the corresponding CPU caps.

### Risks
Any mismatch between macro layout and C structure layout corrupts task vector state. Calling SVE/SME
helpers without enabling access traps. Incorrect vector-length setup can overrun buffers or preserve
invalid state. Syscall flushing must clear the right architectural state to maintain the user ABI
while preserving shared FPSIMD lanes.

### Test Signals
FPSIMD context-switch tests, signal-frame save/restore tests, ptrace register tests, SVE vector
length switching, SME ZA/ZT save/load tests, syscall ABI tests that verify SVE state discard, and
preemption stress with vector workloads are useful validation.
