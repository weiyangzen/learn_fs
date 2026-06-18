# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.h

## Purpose
Declares the VMX SGX hooks and provides no-op or intercept-all fallbacks when `CONFIG_X86_SGX_KVM` is disabled.

## Important APIs, Types, And Functions
When SGX KVM support is enabled, it declares `enable_sgx`, `handle_encls()`, `setup_default_sgx_lepubkeyhash()`, `vcpu_setup_sgx_lepubkeyhash()`, and `vmx_write_encls_bitmap()`. Without SGX KVM, `enable_sgx` is a constant zero, setup functions are no-ops, and `vmx_write_encls_bitmap()` writes `-1ull` to `ENCLS_EXITING_BITMAP` when hardware supports ENCLS exits.

## Control Flow
VMX initialization/setup uses the setup helpers for launch-control MSR defaults. VM-exit handling calls `handle_encls()` only in SGX-enabled builds. VMCS setup calls `vmx_write_encls_bitmap()` regardless of build, allowing the disabled build to force all ENCLS leaves to exit.

## State And Persistence
The header owns no state. It exposes global SGX enablement and vCPU launch-control setup when enabled. In disabled builds, state is intentionally absent and ENCLS remains intercepted.

## Dependencies And Integration Points
Includes KVM host definitions, VMX capabilities, and VMCS operation helpers. It links SGX support to VMX exit handling, VMCS setup, and vCPU initialization.

## Risks
The fallback must preserve correct guest behavior when host hardware supports ENCLS exits but the kernel lacks SGX KVM support. If the bitmap is not set to intercept all leaves, unsupported ENCLS execution could reach hardware unexpectedly.

## Test Signals
Builds with and without `CONFIG_X86_SGX_KVM`, VMCS bitmap inspection, and guest SGX-disabled ENCLS #UD/#GP behavior validate this header.
