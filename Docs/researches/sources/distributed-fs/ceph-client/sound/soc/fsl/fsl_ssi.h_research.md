# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.h

## Purpose
`fsl_ssi.h` defines the SSI register map, control/status bit fields, FIFO helpers, AC97 fields, and optional debugfs statistics interface used by `fsl_ssi.c` and `fsl_ssi_dbg.c`.

## Important APIs, Types, And Functions
The main content is register constants `REG_SSI_*`, selector macros `REG_SSI_SxCR`, `REG_SSI_SxCCR`, and `REG_SSI_SxMSK`, SCR/SISR/SIER/STCR/SRCR/SxCCR/SFCSR/STR/SOR/SACNT masks, and helper encoders such as `SSI_SxCCR_WL`, `SSI_SxCCR_DC`, `SSI_SxCCR_PM`, and FIFO counter/watermark macros.

When `CONFIG_DEBUG_FS` is enabled, `struct fsl_ssi_dbg` contains a debugfs dentry and per-status-bit counters, with prototypes for `fsl_ssi_dbg_isr`, `fsl_ssi_debugfs_create`, and `fsl_ssi_debugfs_remove`. When debugfs is disabled, the struct is empty and inline no-op replacements keep the main driver code unconditional.

## Control Flow
The header has no direct execution, but it defines how the SSI driver sets or clears transmitter/receiver enable, clock/frame direction, DMA/IRQ enable, FIFO clear, AC97 read/write mode, TDM masks, and suspend/resume cache fields. The debugfs conditional flow compiles statistics support in or out without changing call sites.

## State And Persistence
No live state is allocated by the header except through `struct fsl_ssi_dbg` embedded in `struct fsl_ssi`. The counters persist for the device lifetime and are incremented from the IRQ path. Register masks define which hardware values are cached by the C file for suspend/resume.

## Dependencies And Integration Points
It depends on Linux device declarations and debugfs availability. It is consumed by the SSI driver for regmap access and by `fsl_ssi_dbg.c` for human-readable interrupt statistics.

## Risks And Edge Cases
Several registers are marked as undocumented or internal in comments (`STR`, `SOR`) but are still used to clear FIFOs and observe state. i.MX21-class hardware lacks AC97 channel status/enable/disable registers, so users of these constants must gate access. Debugfs no-op stubs must remain signature-compatible with the enabled implementation.

## Test Signals
Build with and without `CONFIG_DEBUG_FS`, run SSI playback/capture to confirm SIER and SISR bit meanings, check AC97 paths on non-i.MX21 hardware, and validate debugfs counter increments for FIFO, frame, underrun, overrun, and command status interrupts.
