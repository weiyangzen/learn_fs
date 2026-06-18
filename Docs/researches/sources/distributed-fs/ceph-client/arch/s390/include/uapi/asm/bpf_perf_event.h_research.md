## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bpf_perf_event.h` is a BPF perf
register binding in the s390 ceph-client Linux source snapshot. It has 9 lines and 250 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
ptrace-register inclusion used by BPF perf-event programs on s390
Important macros/constants: `_UAPI__ASM_BPF_PERF_EVENT_H__`.
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
perf, eBPF helpers, ptrace register layout, and userspace BPF tooling. Direct include dependencies
detected here: `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf, eBPF helpers, ptrace register
layout, and userspace BPF tooling. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
register layout mismatch yields wrong BPF context reads

### Test Signals
BPF perf_event selftests on s390
