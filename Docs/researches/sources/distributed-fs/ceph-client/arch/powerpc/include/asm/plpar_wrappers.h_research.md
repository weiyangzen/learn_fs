<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h

## Purpose
This header provides pseries logical-partition hypervisor wrapper helpers around low-level `plpar_hcall*` interfaces for TCE/IOMMU, virtual processor management, dispatch accounting, memory, interrupt, and platform services.

## Important APIs, Types, And Functions
It defines many static inline wrappers for H_PUT_TCE, H_STUFF_TCE, H_PUT_TCE_INDIRECT, H_GET_TCE, H_REGISTER_VPA and related VPA/SLB/shadow buffer registration, H_CONFER, H_PROD, H_CEDE, H_JOIN, H_GET_TERM_CHAR/H_PUT_TERM_CHAR, H_RANDOM, H_HOME_NODE_ASSOCIATIVITY, H_BEST_ENERGY, H_TLB_INVALIDATE, and related pseries hypercalls, translating arguments and return registers into C helpers.

## Control Flow
Callers invoke wrappers, which marshal arguments to `plpar_hcall_norets()` or return-value variants. Some helpers loop or choose flags for bulk TCE operations and virtual CPU state registration.

## State And Persistence Behavior
Persistent state is hypervisor-owned: TCE tables, VPA registration, dispatch/yield state, CPU cede/prod state, terminal buffers, and platform attributes. Wrappers themselves store no state.

## Dependencies And Integration Points
It depends on pseries hypercall numbers and calling conventions from `hvcall.h`, endian/CPU utilities, and partition firmware. It integrates with IOMMU, virtual console, scheduler idle/yield, CPU hotplug, and pseries platform setup.

## Risks And Edge Cases
Hypercall return codes must be propagated exactly. TCE operations must match table index/page size semantics. VPA registration addresses must be real addresses and aligned. Some calls are only valid under specific firmware capabilities.

## Test Signals
Boot pseries LPARs, exercise IOMMU DMA, virtual console, CPU cede/prod/yield, VPA registration during CPU hotplug, random-number calls, and TLB block invalidate capability paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/plpar_wrappers.h -->
