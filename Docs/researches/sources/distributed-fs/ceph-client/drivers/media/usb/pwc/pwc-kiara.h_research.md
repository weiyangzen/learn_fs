## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.h

### Purpose
`pwc-kiara.h` declares Kiara chipset mode-entry structures and constant tables.

### Important APIs, Types, And Functions
It defines `PWC_FPS_MAX_KIARA`, `struct Kiara_table_entry`, and extern declarations for `Kiara_table`, `KiaraRomTable`, and `Kiara_fps_vector`.

### Control Flow
The header has no runtime flow. It provides typed access to static table data.

### State, Persistence, And Dependencies
No mutable state exists. The header includes `pwc.h` for `PSZ_MAX` and shared constants.

### Integration Points
Included by control and decompressor code to negotiate Kiara modes and build codec23 decode tables.

### Risks
The struct layout must match table initializer order and control-code expectations. Changing `PWC_FPS_MAX_KIARA` or table dimensions requires updates in both data and enumeration logic.

### Test Signals
Build coverage catches declaration/definition mismatches. Runtime tests should enumerate frame intervals and set formats on Kiara cameras.
