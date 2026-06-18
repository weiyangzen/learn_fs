# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.c

## Purpose
Implements KVM virtualization of Intel SGX ENCLS exits for VMX. It emulates or forwards key ENCLS leaves, validates guest SGX capabilities and BIOS enablement, safely translates guest operands for ECREATE/EINIT, virtualizes SGX launch-enclave public-key hash MSRs, and programs the VMCS ENCLS exiting bitmap.

## Important APIs, Types, And Functions
External functions are `handle_encls()`, `setup_default_sgx_lepubkeyhash()`, `vcpu_setup_sgx_lepubkeyhash()`, and `vmx_write_encls_bitmap()`. Core helpers include `sgx_get_encls_gva()`, `sgx_gva_to_gpa()`, `sgx_gpa_to_hva()`, `sgx_inject_fault()`, `handle_encls_ecreate()`, `__handle_encls_ecreate()`, `handle_encls_einit()`, `encls_leaf_enabled_in_guest()`, `sgx_enabled_in_guest_bios()`, and `sgx_intercept_encls_ecreate()`. The module parameter `enable_sgx` gates support.

## Control Flow
An ENCLS VM-exit reaches `handle_encls()`. It injects #UD if SGX/SGX1 is unavailable, #GP if the leaf is not guest-enabled, BIOS enablement is missing, or paging is off, then dispatches ECREATE and EINIT. ECREATE translates PAGEINFO, SECINFO, source, and SECS operands through GVA, GPA, and HVA stages, deep-copies SECS contents to avoid TOCTOU, enforces CPUID masks, provisioning-key policy, XFRM constraints, and max enclave size, then calls `sgx_virt_ecreate()`. EINIT translates SIGSTRUCT, SECS, and TOKEN operands, calls `sgx_virt_einit()` with vCPU launch-control hashes, updates flags and RAX, and skips the instruction. Bitmap programming starts from intercept-all, clears allowed SGX1/SGX2 ranges, forces ECREATE/EINIT exits when KVM must enforce policy, and ORs nested VMX ENCLS exits when needed.

## State And Persistence
Global `sgx_pubkey_hash[4]` stores default launch-control hash values after setup. Each VMX vCPU stores virtual `msr_ia32_sgxlepubkeyhash` values copied from that global. SGX provisioning policy is stored in `kvm->arch.sgx_provisioning_allowed`. The ENCLS bitmap is VMCS state and may incorporate nested `vmcs12->encls_exiting_bitmap`.

## Dependencies And Integration Points
Depends on SGX kernel helpers `sgx_virt_ecreate()` and `sgx_virt_einit()`, KVM MMU translation, VMX segment helpers, CPUID leaf 0x12, feature-control MSR state, nested VMX, VMCS writes, and guest capability state. It integrates with `vmx.c` exit handling and vCPU setup paths.

## Risks
SGX operand translation is sensitive to segmentation, canonicality, alignment, and page faults. Bad HVA handling exits to userspace as emulation failure. Provisioning-key and CPUID enforcement must happen on copied data to prevent guest TOCTOU. The code comments identify a limitation: non-EPCM #PF detection lacks PFEC.SGX plumbing. ENCLS bitmap errors can expose unsupported leaves or incorrectly trap leaves that should run natively.

## Test Signals
SGX KVM tests should cover disabled SGX, SGX1/SGX2 leaf gating, ECREATE CPUID mask enforcement, provisioning-key denial, EINIT launch-control hash behavior, nested ENCLS bitmap merging, invalid operands, bad userspace HVA exits, and SGX2 EPCM fault injection.
