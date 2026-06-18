# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init301.h

## Purpose

`init301.h` is the bridge-initialization interface for SiS 30x-series external display hardware. It is consumed by `init301.c` and `sis_main.c` to expose CRT2, LCD, TV encoder, DDC, and bridge power-control routines while sharing the global mode and hardware definitions from `initdef.h`, `vstruct.h`, and `sis.h`.

## Important APIs, Types, And Functions

- Declares CRT2/bridge control APIs: `SiS_UnLockCRT2`, `SiS_EnableCRT2`, `SiS_DisableBridge`, `SiS_SetCRT2Group`, `SiS_SiS30xBLOn`, and `SiS_SiS30xBLOff`.
- Declares mode-selection helpers: `SiS_GetRatePtr`, `SiS_GetVBInfo`, `SiS_SetTVMode`, `SiS_SetYPbPr`, `SiS_GetLCDResInfo`, `SiS_GetVCLK2Ptr`, and `SiS_GetResInfo`.
- Declares output-specific helpers for Chrontel encoders: `SiS_SetCH700x`, `SiS_GetCH700x`, `SiS_SetCH701x`, `SiS_GetCH701x`, and `SiS_SetCH70xxANDOR`, with extra 315-series backlight helpers under `CONFIG_FB_SIS_315`.
- Declares DDC helpers: `SiS_DDC2Delay`, `SiS_ReadDDC1Bit`, and `SiS_HandleDDC`.
- Re-declares cross-file init routines implemented in `init.c`, including mode table search, CRT register conversion, DAC loading, FIFO-threshold helpers, and PCI bridge reads.

## Control Flow

This header has no executable control flow. It creates compile-time linkage between `init301.c` and the generic init/fbdev layers. Runtime flow generally starts in `sis_main.c`, which calls mode selection and bridge setup functions; those functions use the prototypes here to coordinate generic mode table lookup, bridge-specific programming, TV/LCD register setup, and DDC reads.

## State And Persistence

The APIs operate on `struct SiS_Private *SiS_Pr`, which carries mode tables, hardware port addresses, chip type, bridge flags, ROM data, and per-mode state. Persistent state is hardware state written to VGA sequencer/CRTC ports, bridge part registers, Chrontel encoder registers, panel/TV flags, and backlight state. The header itself stores no data.

## Dependencies And Integration Points

- Includes `initdef.h`, `vgatypes.h`, `vstruct.h`, `sis.h`, and `<video/sisfb.h>`.
- Depends on Linux fbdev and I/O headers for types and port/MMIO access.
- Feature sections are gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`.
- Integrates with `init301.c` for implementation, `init.c` for shared mode logic, and `sis_main.c` for fbdev-facing mode setting and DDC operations.

## Risks

- Prototype duplication with `sis.h` and `init.h` can drift if function signatures change.
- Most functions mutate low-level display hardware through `SiS_Pr`; incorrect flags or mode indexes can blank displays, select the wrong encoder, or misprogram TV/LCD timings.
- Conditional declarations mean build coverage must include both 300 and 315 configurations to catch missing prototypes.

## Test Signals

- Build with `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, and combined configurations to validate conditional prototypes.
- Exercise CRT2 enable/disable, TV/LCD switching, and DDC through fbdev mode setting paths.
- Check for warnings about missing prototypes or incompatible pointer types when compiling `init301.c`, `init.c`, and `sis_main.c`.
