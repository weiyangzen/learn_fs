# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h

### Purpose
`mmu.h` defines ARM64 MM context state and ASID/TCR-related helpers used by process address spaces and kernel page-table management.

### Important APIs, Types, And Functions
It declares `mm_context_t`, ASID/id fields, flags for 52-bit VA or CnP-style behavior, and architecture MMU helper prototypes/macros used by context switching and page-table setup.

### Control Flow
Context-switch and MM initialization code read/write the context fields to select the active ASID and translation regime. Page-table setup uses flags to choose address-space sizing.

### State, Persistence, And Dependencies
State persists in each `mm_struct` context for the lifetime of a process address space. It depends on atomic counters, CPU feature flags, and ARM64 translation control definitions.

### Integration Points
Used by `mmu_context.h`, scheduler context switch, TLB flushing, exec/fork, KVM interactions with process memory, and filesystem page-fault paths.

### Risks
ASID reuse and context flag mistakes can create stale TLB access across processes. 52-bit VA support must stay synchronized with page-table layout.

### Test Signals
Run fork/exec stress, ASID rollover tests, TLB shootdown tests, 52-bit VA builds, and memory-management selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mmu.h -->
