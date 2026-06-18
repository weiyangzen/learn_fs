# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h

### Purpose
`kvm_types.h` supplies ARM64 KVM architecture-specific type aliases needed by generic KVM headers.

### Important APIs, Types, And Functions
The file is intentionally tiny and defines KVM scalar types such as the architecture pfn type used in page-table code.

### Control Flow
There is no runtime flow; the header exists to satisfy include-time type contracts.

### State, Persistence, And Dependencies
It has no state or persistence. It depends on generic integer type definitions already available through the include stack.

### Integration Points
Included indirectly by generic KVM and ARM64 page-table/MMU code.

### Risks
Type width drift would break address translation or pfn math. The small size makes ABI drift the main concern.

### Test Signals
Compile KVM and page-table code across ARM64 configs; run sparse/build checks for type mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_types.h -->
