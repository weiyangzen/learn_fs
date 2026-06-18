<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh

### Purpose
This script converts 64-bit vDSO `nm` output into offset defines.

### Important APIs, Types, And Functions
Its sed rule emits `#define vdso64_offset_<name> 0x<addr>` for matching `__kernel_*` symbols.

### Control Flow
The Makefile pipes `NM` output into the script and sorts the result under `LC_ALL=C`.

### State, Persistence, And Dependencies
The output header persists in `include/generated`. Dependencies are shell, sed, nm symbol format, and `__kernel_` symbol names.

### Integration Points
Used by native VDSO symbol lookup macros in signal and restart paths.

### Risks
The matching pattern is narrow; symbol type or address formatting changes can drop needed defines.

### Test Signals
Generated header should include sigtramp and restart syscall offsets after a 64-bit vDSO build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh -->
