
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate_loadstore.c

## Purpose
Emulates load/store instructions that trap on MMIO or cache-inhibited mappings. It decodes instructions through the PowerPC single-step analyzer and routes scalar, floating-point, VMX, VSX, and cache operation cases to common MMIO handlers in `powerpc.c`.

## Important APIs, Types, And Functions
Exports `kvmppc_emulate_loadstore(struct kvm_vcpu *)`. Internal feature checks are `kvmppc_check_fp_disabled()`, `kvmppc_check_vsx_disabled()`, and `kvmppc_check_altivec_disabled()`. It uses `struct instruction_op`, instruction type bits such as `LOAD`, `STORE`, `LOAD_FP`, `LOAD_VMX`, `LOAD_VSX`, `STORE_FP`, `STORE_VMX`, `STORE_VSX`, `CACHEOP`, flags like `SIGNEXT`, `BYTEREV`, `UPDATE`, `FPCONV`, and VSX flags.

## Control Flow
The function fetches the last instruction, clears all MMIO copy/extension bookkeeping, mirrors current MSR into `vcpu->arch.regs`, and calls `analyse_instr()`. Scalar loads/stores call `kvmppc_handle_load()`, `kvmppc_handle_loads()`, or `kvmppc_handle_store()`. FPU/VMX/VSX paths first inject unavailable exceptions if the relevant MSR enable bit is off, configure copy type, offsets, sign/precision conversion, and then call vector-aware handlers. Update-form instructions write the effective address back to the update register after successful decode.

## State And Persistence
Uses transient vCPU fields including `mmio_vsx_copy_nums`, `mmio_vsx_offset`, `mmio_vmx_copy_nums`, `mmio_vmx_offset`, `mmio_copy_type`, `mmio_sp64_extend`, `mmio_sign_extend`, `mmio_host_swabbed`, `vaddr_accessed`, `paddr_accessed`, and `mmio_is_write`. It may flush guest FP/VMX/VSX extension state via backend `giveup_ext()` before stores.

## Dependencies And Integration Points
Depends on `asm/sstep.h`, KVM MMIO handlers in `powerpc.c`, exception queue helpers, MSR feature definitions, and tracepoint `kvm_ppc_instr`. It is called by `kvmppc_emulate_mmio()` in the common PowerPC KVM layer.

## Risks
Unsupported or incorrectly decoded load/store forms return `EMULATE_FAIL`, which the caller converts into data-storage or program exceptions. Vector and VSX accesses are alignment-sensitive and split into repeated MMIO operations; partial completion state must be resumed correctly by `kvm_arch_vcpu_ioctl_run()`. Endianness and floating-point conversion flags are subtle and architecture-dependent.

## Test Signals
Good coverage would include scalar byte-reversed and sign-extending MMIO, update-form loads/stores, FPU unavailable injection, VMX/VSX split loads/stores, and cache operations returning done without MMIO. Tracepoint output should identify emulated instruction and result.
