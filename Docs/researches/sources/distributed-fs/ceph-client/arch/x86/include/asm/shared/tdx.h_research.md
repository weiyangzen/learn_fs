<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h

Purpose: defines Intel TDX guest-module and hypercall constants shared by the kernel, decompressor, and early boot paths. Important definitions include TDX CPUID identity, TDG leaf numbers, TD attributes, shared bit handling, TDVMCALL register masks, hypercall status codes, MMIO/port I/O hypercall subfunctions, and `tdx_module_args`.

Control flow: TDX guests use these constants to issue `TDCALL`/`TDVMCALL` operations for CPUID, VE info, memory acceptance, reports, MMIO, port I/O, and hypervisor services. State is carried in register arguments and TDX module metadata, not owned by this header.

Dependencies include TDX module ABI, confidential-computing detection, #VE handling, boot decompressor code, and shared register calling conventions. Risks include wrong register masks, hypercall leaf values, or shared-bit calculations causing boot failure or data exposure. Test signals include TDX guest boot, #VE MMIO/PIO handling, memory acceptance, TDREPORT, CPUID identity detection, and compressed-kernel TDX paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/tdx.h -->
