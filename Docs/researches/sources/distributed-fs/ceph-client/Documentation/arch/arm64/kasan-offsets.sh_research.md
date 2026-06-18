<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh -->
## sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh

### Purpose
Prints arm64 KASAN shadow offsets for selected virtual address sizes and shadow scale shifts.

### Important APIs, Types, And Functions
Defines print_kasan_offset(scale argument via $2 and VABITS via $1) and prints tables for KASAN_SHADOW_SCALE_SHIFT 3 and 4 across VABITS 48, 47, 42, 39, and 36.

### Control Flow
Control flow is deterministic shell arithmetic and printf output.

### State, Persistence, And Dependencies
No persistent state; output is documentation/reference text. Depends on POSIX shell arithmetic supporting 64-bit-like expressions in the running shell and printf formatting.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include arithmetic portability across shells and hard-coded VABITS set getting stale as arm64 VA modes evolve.

### Test Signals
Test signals include expected offset table values and execution under dash/bash used by kernel scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh -->
