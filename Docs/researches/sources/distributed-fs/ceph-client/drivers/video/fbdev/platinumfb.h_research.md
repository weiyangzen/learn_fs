## sources/distributed-fs/ceph-client/drivers/video/fbdev/platinumfb.h

Purpose: this header provides the hardware register layout and static mode programming tables consumed by `platinumfb.c`. It is effectively the data sheet encoding for Apple Platinum timing, pitch, DACula, and clock setup.

Important APIs/types/functions: `struct cmap_regs` maps DACula indexed address/data/LUT registers with 16-byte spacing. `struct preg` and `struct platinum_regs` model padded 32-bit Platinum registers. `struct platinum_regvals` packages framebuffer offset, pitch per color mode, 26 timing/control register values, per-cmode offsets, modes, DACula controls, and two clock-parameter variants. `platinum_reg_init_1` through `_20` define Mac video mode tables. `platinum_reg_init[VMODE_MAX]` indexes those tables by Mac vmode. `struct vmode_attr` and `vmode_attrs[]` expose resolution, refresh, and interlace metadata.

Control flow: no executable control flow exists here, but `platinumfb.c` indexes `platinum_reg_init[pinfo->vmode - 1]` during hardware programming, mode validation, framebuffer offset computation, clock setup, and line-length calculation. The `clock_params[2][2]` entries are selected by detected DACula/clock type.

State and persistence behavior: all state is static kernel data. It is read-only in normal operation, though the definitions are not declared `const`. It encodes persistent hardware knowledge rather than runtime state.

Dependencies and integration points: depends on `VMODE_MAX` and color-mode indices from `macmodes.h`. Its tables must align with `mac_vmode_to_var()` and `mac_var_to_vmode()` expectations. The register offsets and pitches are interpreted by `platinum_set_hardware()` and `set_platinum_clock()`.

Risks: tables are hand-coded magic values; a wrong value can damage display timing or produce unusable video. `platinum_reg_init` assumes every vmode from 1 to `VMODE_MAX` has a corresponding table and matching `vmode_attrs` entry. Because tables are mutable static objects, accidental writes would affect all devices. Some comments mark duplicated/unsupported modes, e.g. 800x600 56 Hz copied from another mode.

Test signals: compile with PowerMac/macmodes constants, mode-by-mode validation via `fbset`, visual confirmation for each supported resolution/refresh/color depth, DACula old/new clock parameter selection, VRAM-limited modes using pitch/offset tables, and regression tests comparing `vmode_attrs` to `macmodes` conversions.
