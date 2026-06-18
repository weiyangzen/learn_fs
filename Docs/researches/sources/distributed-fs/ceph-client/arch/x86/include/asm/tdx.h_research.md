<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h

Purpose: declares Intel TDX guest and host kernel interfaces beyond the shared ABI constants. Important APIs include TDX detection/init helpers, #VE handling, TDCALL/TDVMCALL wrappers, memory accept/private/shared helpers, KVM/host TDX module calls, and stubs for non-TDX builds.

Control flow: early boot detects TDX, accepts memory, configures #VE handling, and routes MMIO/PIO or hypervisor services through TDVMCALL. Host/KVM code initializes and invokes the TDX module for TD lifecycle operations when configured.

State and persistence: TDX guest state lives in TDX module/SEAM state, accepted-memory bitmap/state, and per-CPU exception handling context; host state includes module metadata and TD resources. Dependencies include `shared/tdx.h`, confidential-computing framework, set-memory, exception entry, KVM TDX code, and firmware/module ABI.

Risks: unaccepted memory use, wrong shared/private transitions, #VE recursion, hypercall ABI mismatch, and host module call failure handling. Test signals include TDX guest boot, memory acceptance, MMIO #VE tests, TDREPORT/hypercalls, KVM TDX initialization, and non-TDX stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx.h -->
