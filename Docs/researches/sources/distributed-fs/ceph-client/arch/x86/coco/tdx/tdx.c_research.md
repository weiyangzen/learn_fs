# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx.c

## Purpose
Main Intel TDX guest implementation. It detects TDX, configures CoCo masks and TD controls, emulates #VE exits, provides TDX attestation/quote helpers, handles shared/private page conversion callbacks, and prepares safe halt/kexec behavior.

## Important APIs, Types, And Functions
Exports `tdx_kvm_hypercall()` when KVM guest support is enabled, `tdx_mcall_get_report0()`, `tdx_mcall_extend_rtmr()`, `tdx_hcall_get_quote()`, `tdx_get_ve_info()`, `tdx_handle_virt_exception()`, `tdx_halt()`, `tdx_early_handle_ve()`, and `tdx_early_init()`. Important internals include `tdcall()`, `tdg_vm_rd()`, `tdg_vm_wr()`, `tdx_setup()`, `disable_sept_ve()`, `reduce_unnecessary_ve()`, `handle_mmio()`, `handle_io()`, `read_msr()`, `write_msr()`, `handle_cpuid()`, `tdx_map_gpa()`, and kexec callbacks.

## Control Flow And State
Early init checks the TDX CPUID signature, forces TDX/TSC capabilities, reads TD info to derive the shared-bit mask, disables unwanted notifications and SEPT #VE where possible, reduces unnecessary #VEs, updates `physical_mask`, installs encryption conversion callbacks, replaces halt pv_ops, disables parallel CPU bringup, and logs TD metadata. #VE handling retrieves VEINFO immediately, dispatches user CPUID-only handling or kernel HLT/MSR/CPUID/MMIO/IO handling, and advances RIP by decoded or module-provided length. Page conversion maps GPA ranges through TDVMCALL MapGPA, accepts memory on shared-to-private, and accounts shared pages in `nr_shared`. Kexec finish walks the direct map, clears shared PTEs, converts pages private, flushes TLBs, and reports accounting mismatch.

## Dependencies And Integration
Integrates TDX module calls, GHCI TDVMCALL ABI, x86 CoCo vendor/mask APIs, paravirt halt hooks, set-memory encryption callbacks, instruction decoder/MMIO helpers, kexec, KVM hypercall export, and TDX guest driver attestation APIs.

## Risks And Test Signals
Risks include leaving SEPT #VE enabled, private GPA EPT violations, unsafe HLT with interrupts enabled, user-mode #VE beyond CPUID, MMIO instruction split-page handling, MapGPA retry validation, shared-page accounting drift, and kexec with leftover shared mappings. Signals include TDX guest boot, TD quote/report/RTMR tests, MMIO/PIO drivers, CPUID hypervisor leaves, suspend/idle halt behavior, kexec/kdump, and set_memory decrypted/encrypted stress tests.
