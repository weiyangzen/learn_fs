## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-kiara.c

### Purpose
`pwc-kiara.c` provides static mode-selection and ROM lookup data for Kiara-generation PWC cameras, mainly types 730, 740, and 750.

### Important APIs, Types, And Functions
The file defines `Kiara_fps_vector`, `Kiara_table[PSZ_MAX][PWC_FPS_MAX_KIARA][4]`, and `KiaraRomTable[8][2][16][8]`. Entries describe USB alternate interface, packet size, compressed band length, and twelve-byte camera mode commands for each resolution/fps/compression slot.

### Control Flow
There is no executable control flow beyond static initialization. `set_video_mode_Kiara()` indexes `Kiara_table` by size, fps, and compression preference, while `pwc_dec23_init()` indexes `KiaraRomTable` by command-derived ROM version and pass.

### State, Persistence, And Dependencies
All data is constant and shared by all devices. No runtime state is stored here. The file depends on `pwc-kiara.h` for type declarations and on PWC size constants.

### Integration Points
Mode negotiation in `pwc-ctrl.c` consumes the mode table to select alternate settings and commands. The codec23 decompressor consumes ROM tables to build decode tables for compressed YUV output.

### Risks
Data correctness is critical and hard to infer from code review. An incorrect alternate, band length, or command byte can cause USB bandwidth failures, malformed frame sizing, or bad decompression. Unsupported modes are represented by zero alternates and must remain aligned with `PSZ_MAX` and fps vectors.

### Test Signals
Exercise Kiara devices at each supported resolution and frame rate, compare selected `valternate`/`vbandlength` against expected table entries, capture raw and YUV420 formats, and verify decode output after mode changes that alter ROM versions.
