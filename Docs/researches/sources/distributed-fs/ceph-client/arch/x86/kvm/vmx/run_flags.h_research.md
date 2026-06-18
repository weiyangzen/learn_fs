# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/run_flags.h

## Purpose
Defines bit flags passed to the low-level VMX run assembly path.

## Important APIs, Types, And Functions
`VMX_RUN_VMRESUME` selects VMRESUME instead of VMLAUNCH. `VMX_RUN_SAVE_SPEC_CTRL` documents/specifies a run flag for saving guest SPEC_CTRL state. `VMX_RUN_CLEAR_CPU_BUFFERS_FOR_MMIO` requests CPU buffer clearing when the vCPU can access host MMIO.

## Control Flow
`vmenter.S` tests `VMX_RUN_VMRESUME` before executing VMRESUME or VMLAUNCH and tests `VMX_RUN_CLEAR_CPU_BUFFERS_FOR_MMIO` in the VERW mitigation path when the CPU uses conditional MMIO buffer clearing. C code constructing run flags controls these mitigations and entry mode.

## State And Persistence
No persistent state. The flags are transient inputs to a single guest entry attempt and are consumed from the assembly stack frame.

## Dependencies And Integration Points
Depends on `BIT()` from included kernel context. Integrated directly with `__vmx_vcpu_run()` and VMX C code that decides launch/resume and mitigation requirements.

## Risks
Flag bit reuse or mismatch with assembly offsets can select the wrong VM-entry instruction or skip required CPU vulnerability mitigations. Since the assembly reads flags by stack offset, calling convention changes must keep this contract intact.

## Test Signals
VMX launch/resume tests, nested VMX tests, and CPU mitigation selftests or tracing around VERW behavior are the primary signals.
