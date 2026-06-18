<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c

## Purpose
`vcpu_sbi.c` is the central RISC-V KVM SBI dispatcher. It defines the ordered SBI extension table, records per-vCPU extension availability, routes guest ECALLs to extension handlers, forwards unsupported/vendor calls to userspace, and exposes SBI extension and extension-state registers through KVM ONE_REG.

## Important APIs, Types, And Functions
The key table is `sbi_ext[]`, whose entries bind `KVM_RISCV_SBI_EXT_*` ids to `struct kvm_vcpu_sbi_extension` implementations. `kvm_vcpu_sbi_find_ext()` finds an enabled handler by SBI extension id. `kvm_riscv_vcpu_sbi_ecall()` is the hot-path ECALL dispatcher. `kvm_riscv_vcpu_sbi_forward_handler()` formats `KVM_EXIT_RISCV_SBI` for userspace. `kvm_riscv_vcpu_sbi_system_reset()`, `kvm_riscv_vcpu_sbi_request_reset()`, and `kvm_riscv_vcpu_sbi_load_reset_state()` coordinate reset and boot state. ONE_REG support is split between extension enable registers and extension-specific state registers.

## Control Flow
Initialization probes every extension, marks it unavailable/disabled/enabled, and calls optional per-extension init. An ECALL reads `a7` as extid and `a6` as funcid, looks up a handler, executes it, then either advances `sepc`, redirects a virtual trap, exits to userspace, or returns SBI error/output values in `a0/a1`. State register enumeration skips disabled extensions and delegates register layout to each extension when available.

## State And Persistence
State is per-vCPU in `arch.sbi_context.ext_status`, `return_handled`, extension private state, and reset state protected by `reset_state.lock`. System reset writes all vCPUs to stopped MP state and requests sleep. There is no disk persistence; migration persistence is via ONE_REG state.

## Dependencies And Integration Points
This file integrates all RISC-V KVM SBI extension modules, KVM run exits, KVM ONE_REG, vCPU MP state, reset requests, and trap redirection. Userspace VMMs observe forwarded calls through `run->riscv_sbi` and system events through `KVM_EXIT_SYSTEM_EVENT`.

## Risks
Extension status and default-disabled behavior are ABI-sensitive. ECALL completion must advance `sepc` exactly once and must not clobber `a1` for SBI v0.1 semantics. ONE_REG setters reject changes after a vCPU has run, which is important for migration correctness. Forwarded calls rely on userspace returning through `kvm_riscv_vcpu_sbi_return()` exactly once.

## Test Signals
Useful tests boot guests using legacy and modern SBI, probe enable/disable through ONE_REG, migrate FWFT/STA state, exercise vendor/experimental forwarding, and verify reset/shutdown exits and unsupported extension return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c -->
