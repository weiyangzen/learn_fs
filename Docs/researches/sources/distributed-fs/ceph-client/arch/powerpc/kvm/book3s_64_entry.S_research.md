# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_64_entry.S

## Purpose
Implements 64-bit Book3S KVM exception entry dispatch and POWER9 HV guest entry/exit assembly. It normalizes hcalls and interrupts from exception handlers, routes PR versus HV exits, supports skip-mode fault recovery, and saves/restores guest/host register state around P9 HV guest execution.

## Important APIs, Types, And Functions
Global entry points are `kvmppc_hcall`, `kvmppc_interrupt`, and `kvmppc_p9_enter_guest` (exported). Local paths include `.Lgot_save_area`, `.Lmaybe_skip`, `.Lret_to_ultra`, `kvmppc_p9_exit_hcall`, `kvmppc_p9_exit_interrupt`, and `kvmppc_p9_bad_interrupt`. It uses PACA `HSTATE_*`, `EX_*` save areas, `VCPU_*` offsets, `KVM_GUEST_MODE_*`, `HRFI_TO_GUEST`, `RFI_TO_KERNEL`, and ultravisor `UV_RETURN`.

## Control Flow
`kvmppc_hcall` detects P9 HV guest mode and branches to the P9 hcall exit path, otherwise normalizes state to look like a generic interrupt. `kvmppc_interrupt` chooses the correct PACA save area, saves CFAR/PPR/CTR and scratch registers, and dispatches to PR or HV handlers based on `HSTATE_IN_GUEST`. Skip-mode faults from guest-context instruction loads are handled by advancing SRR0/HSRR0 and returning to kernel code without going through full KVM exit. `kvmppc_p9_enter_guest` saves host nonvolatile state, loads guest LR/CTR/XER/CR/CFAR/PPR/GPRs, and enters with `HRFI_TO_GUEST` or returns to the ultravisor for secure guests. P9 exit saves guest state to the vCPU, restores host stack/nonvolatile registers, optionally flushes the link stack, and returns to C.

## State And Persistence
The code persists guest GPRs, CR, LR, XER, PC, MSR, CFAR/PPR, and selected scratch values in `struct kvm_vcpu` and PACA HSTATE fields. It temporarily mutates host stack, PACA guest mode flags, SRR/HSRR state, and special registers. Secure guest paths coordinate with Ultravisor state.

## Dependencies And Integration Points
Depends on 64S exception handlers, PACA layout, generated asm offsets, PR and HV interrupt handlers, P9 entry C code, ultravisor ABI, CPU feature patching, and link-stack flush patch sites. It is the assembly bridge between Linux exception entry and KVM Book3S execution.

## Risks And Edge Cases
Register save/restore omissions cause silent guest or host corruption. Skip-mode recovery intentionally advances faulting host loads and must only apply to expected MCE/DSI/segment faults. P9 bad-interrupt recovery is best-effort and loops for hash hosts. Secure guest ultracall return uses a special register contract. Feature-patched CFAR/PPR/link-stack code must match CPU capabilities.

## Test Signals
Guest boot and migration on POWER9/POWER10 HV, PR syscall reflection, hcall exits, external/decrementer/data-storage interrupts, prefixed instruction faults, secure guest ultravisor exits, injected machine checks/system resets, and host stability after repeated entry/exit cycles.
