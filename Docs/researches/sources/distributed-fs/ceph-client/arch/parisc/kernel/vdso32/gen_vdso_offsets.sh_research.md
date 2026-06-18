<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh

### Purpose
This script converts `nm` output for the 32-bit vDSO into C preprocessor defines for vDSO symbol offsets.

### Important APIs, Types, And Functions
It uses a single `sed` expression to emit `#define vdso32_offset_<name> 0x<addr>` for symbols matching `__kernel_*`.

### Control Flow
The Makefile pipes `$(NM) vdso32.so` into the script, then sorts the output. The script sets `LC_ALL=C` and filters matching symbol lines.

### State, Persistence, And Dependencies
The generated header persists under `include/generated`. Dependencies are POSIX shell, sed, stable nm output, and vDSO symbol naming.

### Integration Points
Offsets are consumed by `VDSO32_SYMBOL()` users such as signal delivery.

### Risks
Only lowercase hexadecimal addresses and symbol type `.` lines match. Renaming trampoline symbols or changing nm output format silently drops defines.

### Test Signals
Run the Makefile rule and verify defines for sigtramp and restart syscall offsets are present and sorted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh -->
