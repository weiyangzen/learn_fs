## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-nala.h

### Purpose
`pwc-nala.h` is an included data table for older Nala cameras, covering type 645/646 mode commands.

### Important APIs, Types, And Functions
The file is not a normal standalone header with guards. It contributes initializer rows for `Nala_table[PSZ_MAX][PWC_FPS_MAX_NALA]` in `pwc-ctrl.c`. Each row contains USB alternate setting, compressed flag, and a three-byte mode command.

### Control Flow
There is no executable flow. `set_video_mode_Nala()` indexes the included table after mapping requested frame rates to supported Nala rates.

### State, Persistence, And Dependencies
All data becomes static table state inside `pwc-ctrl.c`. It depends on the exact `struct Nala_table_entry` layout visible at inclusion time.

### Integration Points
The table feeds codec1/Nala video mode selection and determines which resolutions are unavailable by zero entries.

### Risks
Because this is an include-fragment rather than a guarded header, it should only be included in the intended initializer context. Table shape must remain exactly aligned with `PSZ_MAX` and `PWC_FPS_MAX_NALA`.

### Test Signals
Build tests catch initializer-shape errors. Runtime tests on Nala devices should verify SQCIF/QCIF/CIF mode selection, unavailable modes, alternate settings, compression flags, and raw PWC1 output.
