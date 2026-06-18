## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/kvm_perf.h` is a s390 KVM perf trace
ABI in the s390 ceph-client Linux source snapshot. It has 22 lines and 474 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
decode string length and trace-field index constants for KVM entry/exit perf events
Important macros/constants: `__LINUX_KVM_PERF_S390_H`, `DECODE_STR_LEN`, `VCPU_ID`, `KVM_ENTRY_TRACE`, `KVM_EXIT_TRACE`, `KVM_EXIT_REASON`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf trace decoding, KVM tracepoints, and SIE intercept definitions. Direct include dependencies
detected here: `asm/sie.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf trace decoding, KVM tracepoints,
and SIE intercept definitions. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
index drift makes perf decode the wrong vCPU or exit reason fields

### Test Signals
perf kvm trace tests and tracepoint format inspection
