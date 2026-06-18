## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/runtime_instr.h` is a runtime-
instrumentation userspace ABI in the s390 ceph-client Linux source snapshot. It has 74 lines and
1424 bytes; exported UAPI contract: yes.

### Important APIs, Types, And Functions
runtime-instrumentation start/stop commands, control block layout, and inline load/store control-
block helpers
Important macros/constants: `_S390_UAPI_RUNTIME_INSTR_H`, `S390_RUNTIME_INSTR_START`, `S390_RUNTIME_INSTR_STOP`.
Important types/layouts: `runtime_instr_cb`.
Important declarations or inline helpers: `volatile`, `load_runtime_instr_cb`, `store_runtime_instr_cb`.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
runtime_instr syscall/device paths, task context management, and performance/debug tooling. Direct
include dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for runtime_instr syscall/device paths,
task context management, and performance/debug tooling. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
control-block layout mistakes misprogram hardware runtime instrumentation

### Test Signals
runtime-instrumentation start/stop and context-switch tests
