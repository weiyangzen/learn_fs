## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/perf_regs.h` is a perf register
enumeration in the s390 ceph-client Linux source snapshot. It has 44 lines and 887 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
s390 perf_event register ids for general, mask, and address registers
Important macros/constants: `_ASM_S390_PERF_REGS_H`.
Important types/layouts: `perf_event_s390_regs`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
perf sampling, BPF stack/register capture, and userspace unwinding tools. Direct include
dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for perf sampling, BPF stack/register
capture, and userspace unwinding tools. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
renumbering breaks perf sample decoding and BPF register access

### Test Signals
perf regs selftests and sample register dumps
