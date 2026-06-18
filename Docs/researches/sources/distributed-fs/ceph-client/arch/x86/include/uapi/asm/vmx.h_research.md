<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h

Purpose: Defines Intel VMX VM-exit reason codes, exit reason flags, abort codes, and decode lists for KVM/perf tooling.

Important APIs/types/functions: `VMX_EXIT_REASONS_FAILED_VMENTRY`, `VMX_EXIT_REASONS_SGX_ENCLAVE_MODE`, `EXIT_REASON_*`, `VMX_EXIT_REASONS`, `VMX_EXIT_REASON_FLAGS`, and `VMX_ABORT_*`.

Control flow: KVM VMX reports exits and aborts using these constants; perf tooling decodes exit reasons from KVM tracepoints.

State and persistence behavior: No state. Exit codes are hardware/trace ABI values.

Dependencies and integration points: Integrates with KVM VMX, nested VMX, SGX enclave VM-exit reporting, TDX-related exits, perf KVM decode, and userspace VMM diagnostics.

Risks and test signals: Risks include missing new hardware exit codes, decode name drift, and failed-vmentry flag handling. Test Intel KVM selftests, nested VMX, perf exit decoding, SGX/TDX exit paths where available, and invalid VM-entry reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h -->
