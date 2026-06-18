<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S

## Purpose
`host.S` contains the nVHE host exception vector and low-level host/hyp transition assembly. It saves host CPU context on traps into EL2, calls the C trap handler, restores host state for `eret`, handles hyp panic return to the host, supports legacy stub HVC calls before protected mode, and forwards unhandled SMCs to firmware.

## Important APIs, Types, and Functions
`__host_exit` saves host registers, optionally switches pointer-authentication keys to hyp keys, calls `handle_trap()`, then restores host registers and returns. `__host_enter` restores a supplied host context and never returns in C terms. `__hyp_do_panic` prepares host panic-handler entry with ESR/ELR/PAR/FAR/HPFAR arguments. `__host_hvc` chooses between protected-mode trap handling, legacy stub HVC dispatch, and full host-exit handling. `__kvm_hyp_host_vector` defines EL2 and lower-EL vector slots. `__kvm_hyp_host_forward_smc` loads x0-x17 from `struct kvm_cpu_context`, executes `smc #0`, and stores the result.

## Control Flow, State, and Persistence
The file persists CPU state only by writing the per-CPU host context selected by `get_host_ctxt`. Synchronous lower-EL vectors push x0/x1, inspect ESR, dispatch HVC64 specially, and otherwise enter `__host_exit`. Invalid EL2 vectors detect stack overflow using the `NVHE_STACK_SHIFT` guard bit and route to panic, optionally on the overflow stack. Pointer-authentication state is saved/restored only under configured alternatives and protected mode.

## Dependencies and Integration Points
It depends on assembler macros for KVM context offsets, ptrauth save/restore, hyp/kimage address conversion, host vector constants, and panic symbols. It is entered from `hyp-init.S` via VBAR_EL2 and calls C handlers in `hyp-main.c` and panic support in `switch.c` / `stacktrace.c`.

## Risks and Test Signals
Risks include register-save omissions, mismatch with `struct kvm_cpu_context` offsets, incorrect ptrauth key switching, stack-overflow detection depending on stack alignment, and forwarding SMC register sets wider than the firmware ABI guarantees. Test signals are booting nVHE with and without protected mode, HVC/SMC trap smoke tests, panic stacktrace capture, ptrauth-enabled kernels, and objtool/assembler checks for vector slot size constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/host.S -->
