<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h

## Purpose
This trace header covers arm64 KVM exit handling events that are close to trap dispatch: WFx instructions, HVC calls, sysreg handling, individual sysreg accesses, and guest debug flag updates.

## Important APIs, Types, And Functions
- `kvm_wfx_arm64` records WFI/WFE traps and the guest PC.
- `kvm_hvc_arm64` records HVC PC, x0/r0 value, and immediate.
- `kvm_arm_set_dreg32` records debug register name/value writes; the name is historical and values are 64-bit.
- `kvm_handle_sys_reg` records raw HSR/ESR for sysreg traps.
- `kvm_sys_access` records PC, access direction, descriptor name, and decoded sysreg fields.
- `kvm_set_guest_debug` records vCPU pointer and guest debug flags.

## Control Flow
Exit handling and sysreg emulation code call generated `trace_kvm_*` helpers. `kvm_sys_access` receives `struct sys_reg_params` and `struct sys_reg_desc`, which ties this header directly to `sys_regs.h`.

## State And Persistence Behavior
The tracepoints only emit samples to tracing buffers. The `kvm_sys_access` event stores the descriptor name pointer and decoded fields; it does not keep ownership of any dynamic state.

## Dependencies And Integration Points
It includes Linux tracepoint support and `sys_regs.h`. `sys_regs.c` calls `trace_kvm_handle_sys_reg()` and `trace_kvm_sys_access()` to provide sysreg trap diagnostics.

## Risks And Edge Cases
- Trace output depends on descriptor names being stable and valid.
- The `TP_fast_assign` block assigns `Op0` twice; this is harmless duplication but worth noting if editing.
- Tracepoints run on hot paths, so additional fields or expensive formatting would affect enabled tracing overhead.

## Test Signals
Run a guest that executes trapped sysregs, WFI/WFE, HVC, and debug operations with corresponding tracefs events enabled. Build coverage validates macro expansion and include path configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h -->
