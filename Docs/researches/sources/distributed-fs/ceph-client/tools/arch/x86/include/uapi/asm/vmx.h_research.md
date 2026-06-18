# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/vmx.h

## Purpose
Defines Intel VMX VM-exit reason constants, exit-reason flag bits, printable reason lists, and VMX abort codes for UAPI/tool consumers.

## APIs, Types, and Functions
Exports `EXIT_REASON_*` constants for exception/NMI, interrupts, task switch, CPUID, HLT, VMX instructions, CR/DR/IO/MSR accesses, EPT, APIC, SGX/TDX/SEAMCALL, bus lock, immediate MSR exits, and more. `VMX_EXIT_REASONS` and `VMX_EXIT_REASON_FLAGS` provide initializer lists mapping codes/flags to names. Abort constants include `VMX_ABORT_SAVE_GUEST_MSR_FAIL`, `VMX_ABORT_LOAD_HOST_PDPTE_FAIL`, and `VMX_ABORT_LOAD_HOST_MSR_FAIL`.

## Control Flow, State, and Persistence
No runtime state. Consumers expand the lists into tables used to decode VM-exit reason fields and flag bits.

## Dependencies and Integration
Used by KVM VMX tracing, diagnostics, and user-space tools that display nested or hardware VM-exit reasons. Numeric values must match Intel architecture and kernel KVM definitions.

## Risks and Test Signals
Risks include missing new exit reasons, inconsistent handling of flag bits such as failed VM-entry, and stale names for TDX/SEAMCALL-related exits. Test signals are VMX KVM selftests, trace decoding tests, and compile-time table expansion.
