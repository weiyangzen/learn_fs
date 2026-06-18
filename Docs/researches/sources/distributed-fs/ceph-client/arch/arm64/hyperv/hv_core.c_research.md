## sources/distributed-fs/ceph-client/arch/arm64/hyperv/hv_core.c

### Purpose
Provides low-level ARM64 Hyper-V hypercall and virtual processor register helpers plus legacy panic reporting.

### Important APIs, Types, And Functions
Exports `hv_do_hypercall`, `hv_do_fast_hypercall8`, `hv_do_fast_hypercall16`, `hv_set_vpreg`, `hv_get_vpreg_128`, `hv_get_vpreg`, and `hyperv_report_panic`. It uses `struct arm_smccc_res`, `struct arm_smccc_1_2_regs`, `struct hv_get_vp_registers_output`, and Hyper-V register constants.

### Control Flow
Normal hypercalls convert input/output virtual pointers to physical addresses and invoke `arm_smccc_1_1_hvc()`. Fast hypercalls pass one or two register arguments with the fast bit set. VP register access uses fast Hyper-V register calls; 128-bit reads require SMCCC 1.2 registers beyond x0-x3. Panic reporting writes crash parameters once, then notifies Hyper-V through `HV_REGISTER_GUEST_CRASH_CTL`.

### State, Persistence, And Dependencies
The only file-local state is static `panic_reported`, preventing duplicate crash notifications. Hypervisor-visible state is VP registers and crash data. Dependencies include SMCCC, `virt_to_phys`, Hyper-V HVDK definitions, `asm/mshyperv.h`, and panic/oops globals.

### Integration Points
Used by ARM64 Hyper-V initialization and common Hyper-V drivers. Exported GPL symbols are consumed by the broader Hyper-V guest stack.

### Risks
Hypercall argument register ordering must match Hyper-V ABI exactly. `BUG_ON()` on VP register failure is intentionally fatal. Panic reporting must avoid double reporting and must not run for non-panic oops when `panic_on_oops` is false.

### Test Signals
Boot ARM64 guests on Hyper-V, validate feature/register reads, run synthetic device drivers using fast and normal hypercalls, inject panic/oops paths, and test `CONFIG_HYPERV` builds with SMCCC 1.1/1.2 support.
