# sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-handle.c

## Purpose
Runtime and early #VC exception handling for SEV-ES/SNP guests. It decodes intercepted instructions, performs GHCB hypervisor calls, emulates MMIO and port I/O, handles CPUID/MSR/TSC/debug-register cases, and dispatches kernel/user #VC entry behavior.

## Important APIs, Types, And Functions
External entry points include `__vc_handle_msr()`, `vc_forward_exception()`, `exc_vmm_communication` IDT handlers, and `handle_vc_boot_ghcb()`. Important helpers are `vc_decode_insn()`, `vc_read_mem()`, `vc_write_mem()`, `vc_handle_mmio()`, `vc_do_mmio()`, `vc_handle_dr7_read/write()`, `vc_handle_rdpmc()`, `vc_handle_vmmcall()`, `vc_handle_exitcode()`, `vc_raw_handle_exception()`, and Secure TSC/SVSM CAA MSR handlers. It also includes `vc-shared.c`, binding shared emulation helpers to runtime memory and logging primitives.

## Control Flow And State
The raw handler obtains a GHCB, invalidates it, initializes an emulation context, validates opcode bytes, dispatches by SVM exit code, releases the GHCB, then either advances RIP, forwards a real exception, retries, terminates, or signals user space. Kernel #VC runs in NMI-entry context and terminates/panics on unsupported hypervisor communication. User #VC runs in IRQ context and raises SIGBUS on unrecoverable emulation. MMIO handling translates guest virtual addresses through current CR3, rejects encrypted mappings, uses GHCB shared buffer, and handles string MOVS by splitting into ordinary memory accesses. MSR handling has special cases for SVSM CAA, Secure TSC, and Secure AVIC.

## Dependencies And Integration
Depends on x86 instruction decoding, exception forwarding, GHCB helpers, SNP CPUID table logic, EFI memory-mode detection, FPU/XCR helpers, IO bitmap checks, APIC/Secure AVIC integration, and architecture IDT macros.

## Risks And Test Signals
Risks include incorrect instruction-length advancement, unsafe user/EFI instruction decoding, encrypted MMIO rejection, nested string-instruction #VC recursion, Secure TSC intercept termination, DR7 debug-swap semantics, and kernel #VC from invalid stack context. Signals include SEV-ES boot, MMIO/PIO-heavy drivers, EFI runtime calls, userspace I/O permission tests, CPUID table tests, debug/NMI paths, and objtool coverage for entry/exit constraints.
