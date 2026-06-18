<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h

Purpose: Header for legacy VIA mode/register tables and mode lookup helpers.

Important APIs/types/functions: Defines `struct VPITTable` and `struct patch_table`, externs for table lengths and mode register arrays, extern `VPIT`, and prototypes for `viafb_get_best_mode()` and `viafb_get_best_rb_mode()`.

Control flow and state: No runtime flow. It exposes static register/mode table state stored in `viamode.c`.

Dependencies and integration points: Includes `global.h`, which supplies `StdSR`, `StdGR`, `StdAR`, and `struct io_reg` through the include chain. Risks are extern/table drift, especially `VX800_ModeXregs` being declared here while this source group only defines `VX855_ModeXregs`, and global mutable `int` table lengths rather than constants. Test signals are link-time coverage and mode table consumers compiling against all externs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/viamode.h -->
