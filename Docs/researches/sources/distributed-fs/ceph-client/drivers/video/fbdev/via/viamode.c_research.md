<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c

Purpose: Static mode/register table repository for VIA fbdev plus helpers to select the closest refresh-rate mode for a requested resolution.

Important APIs/types/functions: Defines common register initialization arrays such as `CN400_ModeXregs`, `CN700_ModeXregs`, `KM400_ModeXregs`, `CX700_ModeXregs`, `VX855_ModeXregs`, and `CLE266_ModeXregs`, a small patch table for 1024x768, `VPIT`, standard `viafb_modes[]`, reduced-blanking `viafb_rb_modes[]`, exported table length variables, `viafb_get_best_mode()`, and `viafb_get_best_rb_mode()`.

Control flow and state: The data tables are persistent read-only/static initialization sources used during chipset/mode setup. `get_best_mode()` linearly scans a mode array for matching xres/yres and returns the entry whose refresh is closest to the requested refresh. No allocation or hardware writes happen in this file.

Dependencies and integration points: Includes `linux/via-core.h` and `global.h`; exported arrays are consumed by hardware setup code. `viafbdev.c` calls `viafb_get_best_mode()` during mode validation/defaulting, while LCD code uses it for native panel modes. Risks include duplicate/near-duplicate modes, static register magic values, external declaration of `VX800_ModeXregs` in the header without a definition in this file, and no pixel-clock/chip capability filtering in best-mode selection. Test signals are requested resolution/refresh lookup coverage, register table application on each chipset family, and fbdev mode validation for all listed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.c -->
