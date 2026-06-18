## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/guarded_storage.h` is a guarded-
storage userspace ABI in the s390 ceph-client Linux source snapshot. It has 78 lines and 1208 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
guarded-storage control block, event parameter list, control flags, and inline
load/store/save/restore helpers
Important macros/constants: `_GUARDED_STORAGE_H`, `GS_ENABLE`, `GS_DISABLE`, `GS_SET_BC_CB`, `GS_CLEAR_BC_CB`, `GS_BROADCAST`.
Important types/layouts: `gs_cb`, `gs_epl`.
Important declarations or inline helpers: `volatile`, `load_gs_cb`, `store_gs_cb`, `save_gs_cb`, `restore_gs_cb`.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
signal frames, thread context switching, and userspace guarded-storage enablement. Direct include
dependencies detected here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal frames, thread context
switching, and userspace guarded-storage enablement. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
context layout mistakes lose guarded-storage state across signal or context switches

### Test Signals
guarded-storage selftests and signal/context-switch coverage
