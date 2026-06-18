<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S

## Purpose
Contains Xen x86 early entry and hypercall-page assembly. It provides the PV startup symbol, secondary CPU bringup trampolines, and HVM/PV hypercall stubs including vendor-specific AMD/Intel VMCALL/VMMCALL entry points.

## Important APIs, Types, And Functions
Important symbols are `startup_xen`, `asm_cpu_bringup_and_idle`, `xen_cpu_bringup_again`, `xen_hypercall_hvm`, `xen_hypercall_amd`, `xen_hypercall_intel`, and Xen ELF notes/hypercall page definitions in the remainder of the file.

## Control Flow
`startup_xen` is the Xen-loaded entry point and transfers control into the C Xen startup path with the Xen start-info pointer. CPU bringup symbols switch stacks or jump into `cpu_bringup_and_idle` after a CPU is started or reawakened. HVM hypercall stubs provide aligned call slots used by the hypercall machinery and dispatch through the selected instruction sequence.

## State And Persistence
State is architectural register/stack setup at entry plus the compiled hypercall page. Xen ELF notes persist in the kernel image and inform the hypervisor loader.

## Dependencies And Integration Points
Depends on Xen loader ABI, Linux compressed/uncompressed x86 entry conventions, C functions declared in `xen-ops.h`, and runtime hypercall patch/selection code.

## Risks And Edge Cases
Wrong ELF notes or entry register assumptions prevent Xen from booting the image. Hypercall stubs must match Xen ABI register clobbers and alignment. Secondary bringup stack handling must align with `smp_pv.c`.

## Test Signals
Boot PV and HVM Xen kernels, bring secondary CPUs online/offline, verify hypercall execution on Intel and AMD hosts, and inspect built image notes with ELF tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-head.S -->
