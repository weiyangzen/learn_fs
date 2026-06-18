
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_regs.h

Purpose: central register-offset definition file for Intel 810/815 graphics controller, VGA, overlay, BLT, clock, cursor, memory, and interrupt registers used by the i810 framebuffer driver.

Important content: defines MMIO offsets such as `IRING`, `PGTBL_ER`, `INSTDONE`, `FW_BLC`, `DRAMCH`, GPIOs, `DCLK_*`, GTT, overlay registers, BLT status registers, display/cursor registers (`PIXCONF`, `BLTCNTL`, `DPLYBASE`, `CUR*`), plus VGA I/O register indexes for sequencer, graphics, CRT controller, attribute controller, DAC/CLUT, and miscellaneous output.

Control flow and integration: this file has no executable code. It is consumed by `i810_main.c`, `i810_accel.c`, `i810_dvt.c`, and `i810_gtf.c` through read/write helper macros in `i810.h`. Register names are used directly in mode load/save, acceleration diagnostics, ring-buffer setup, blanking, palette programming, and cursor control.

State and persistence: none directly. These constants define the persistent hardware state locations that the driver saves, modifies, and restores.

Dependencies: guarded by `__I810_REGS_H__` and derived from the Intel 810 PRM. It assumes callers know whether an offset is MMIO or VGA I/O space.

Risks: wrong offsets or bit grouping affect hardware globally. The header mixes legacy VGA I/O ports with graphics-controller MMIO offsets, so accidental use with the wrong accessor family can corrupt programming. Some names reflect old documentation and are terse, increasing maintenance risk.

Test signals: build coverage through all i810 source files; runtime validation via register dump comparison during mode set, blank/unblank, cursor enable, and ring-buffer initialization. Static review should verify any new register use matches the accessor width and MMIO/I/O namespace.
