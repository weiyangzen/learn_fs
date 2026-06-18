# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/init.c

## Purpose
`init.c` is the SiS/XGI framebuffer driver's CRT1 mode-initialization engine. It selects BIOS-style mode IDs for CRT, LCD, TV, and secondary VGA outputs; binds the generic `struct SiS_Private` state to the correct 300-series or 315/XGI-series timing tables; unlocks and programs VGA sequencer, CRTC, graphics-controller, attribute-controller, DAC, clock, FIFO, bridge, and chipset-specific registers; optionally clears framebuffer memory; and exposes helper routines for custom CRTC timing conversion.

This file is not Ceph-specific despite living under the `ceph-client` source snapshot. It is Linux fbdev hardware initialization code for `drivers/video/fbdev/sis`.

## Important APIs, types, and functions
The central type is `struct SiS_Private`, defined by the sibling SiS headers. This file mutates its table pointers, register port addresses, chipset flags, detected bridge flags, mode flags, panel geometry, custom-mode timing fields, VRAM pointer/size, and ROM-layout fields.

Public or externally used entry points include:

- `SiSInitPtr()`: selects and installs table pointers for either the SiS 300 family or the SiS 315/XGI family.
- `SiS_GetModeID_LCD()`, `SiS_GetModeID_TV()`, and `SiS_GetModeID_VGA2()`: convert requested geometry/depth/output flags into SiS BIOS mode numbers.
- `SiS_SetReg*()` and `SiS_GetReg*()`: low-level indexed and raw I/O-port access wrappers around `outb/outw/outl` and `inb/inw/inl`.
- `SiS_DisplayOn()` and `SiS_DisplayOff()`: toggle sequencer display blanking.
- `SiSRegInit()`: derives all VGA, bridge, DDC, video-capture, and video-playback I/O port addresses from the device base address.
- `SiSDetermineROMLayout661()`: detects old versus new SiS 661/650 BIOS ROM layouts.
- `SiS_SearchModeID()`, `SiS_GetModeFlag()`, `SiS_GetModePtr()`, `SiS_GetRefCRTVCLK()`, `SiS_GetRefCRT1CRTC()`, `SiS_GetColorDepth()`, and `SiS_GetOffset()`: table lookup helpers used by mode programming and by other init modules.
- `SiS_LoadDAC()`: loads MDA/CGA/EGA/VGA palette data either into CRT1 DAC ports or bridge DAC ports depending on active programming target.
- `SiSSetMode()`: the main mode-set routine called by `sis_main.c`.
- `SiS_CalcCRRegisters()`, `SiS_CalcLCDACRT1Timing()`, and `SiS_Generic_ConvertCRData()`: helpers for custom CRTC timing synthesis and conversion to `fb_var_screeninfo`.

Key internal routines include pointer initializers (`InitCommonPointer()`, `InitTo300Pointer()`, `InitTo310Pointer()`), chipset discovery (`SiS_GetSysFlags()`, `SiSSetLVDSetc()`, `SiS_GetVBType()`), ROM usage selection (`SiSDetermineROMUsage()`), register group writers (`SiS_SetSeqRegs()`, `SiS_SetMiscRegs()`, `SiS_SetCRTCRegs()`, `SiS_SetATTRegs()`, `SiS_SetGRCRegs()`, `SiS_SetCRT1CRTC()`, `SiS_SetCRT1Offset()`, `SiS_SetCRT1VCLK()`, `SiS_SetCRT1ModeRegs()`), FIFO tuning (`SiS_SetCRT1FIFO_300()`, `SiS_SetCRT1FIFO_630()`, `SiS_SetCRT1FIFO_310()`), and final orchestration (`SiS_SetCRT1Group()`).

## Control flow
Mode selection starts with callers supplying either a BIOS mode number or geometry/output flags that are translated by the `SiS_GetModeID*()` helpers. `SiSSetMode()` clears custom-mode state, decides whether framebuffer clearing is required from the high bit of `ModeNo`, normalizes FSTN CRT1 modes, initializes pointers and port addresses, reads system/chipset flags, unlocks sequencer register access, enables PCI/MMIO/2D/3D engine bits, detects LVDS/Chrontel/Trumpion/Conexant possibilities, decides whether ROM data is usable, and unlocks CRT2 registers.

For normal modes, `SiSSetMode()` resolves `ModeNo` into a standard or extended table index with `SiS_SearchModeID()`. It then detects video bridge type, initializes bridge programming clock state, gathers connector/output information through sibling bridge helpers, derives TV and LCD information, runs low-mode tests, and rejects the mode if required memory exceeds `VideoMemorySize`.

The CRT1 path runs when the mode is for CRT1, simultaneous scan, or LCDA. `SiS_SetCRT1Group()` selects the standard VGA register template, disables the bridge if low-mode safety requires it, resets segment registers, writes the sequencer, miscellaneous output, CRTC, attribute, and graphics-controller groups, clears extended sequencer registers, resets VCLK when bridge/LVDS hardware needs it, finds the refresh-rate table row, and then applies sync polarity, extended CRTC timing, pitch/offset, pixel clock, FIFO thresholds, and mode-specific control bits. It loads the DAC, clears VRAM when requested, waits for retrace where appropriate, and turns display output on.

The CRT2 path is delegated to `SiS_SetCRT2Group()` from companion bridge code when simultaneous scan, CRT2-only, or LCDA output is selected and a supported bridge/LVDS/TV encoder exists. After both paths, `SiSSetMode()` re-enables CRT1 gating, applies odd capture/video register workarounds, restores selected bridge/CRTC backup bits, adjusts SIS760 AGP/UMA/LFB timing, conditionally relocks sequencer access, and returns success.

The custom timing helpers operate after timing fields such as `CHTotal`, `CHDisplay`, `CVTotal`, and `CVDisplay` are already loaded into `struct SiS_Private`. `SiS_CalcCRRegisters()` encodes those values into the `CCRT1CRTC[]` register image; `SiS_CalcLCDACRT1Timing()` derives scaled LCD CRT1 timings from panel geometry and writes them to hardware; `SiS_Generic_ConvertCRData()` decodes CRTC bytes back into framebuffer margins and sync lengths.

## State and persistence behavior
There is no filesystem or durable software persistence. State persists in three places only:

- `struct SiS_Private`: table pointers, port addresses, mode flags, bridge flags, panel data, ROM-layout metadata, custom timing data, and cached backup register values for one driver instance.
- VGA/bridge/chipset registers: mode programming writes persist in hardware until another mode set, reset, suspend/resume sequence, or device removal.
- VRAM: `SiS_ClearBuffer()` clears all or part of framebuffer memory depending on mode class when `SiS_flag_clearbuffer` is set.

`SiSDetermineROMUsage()` reads `VirtualRomBase` and sets `SiS_UseROM`, `SiS_ROMNew`, `SiS_EMIOffset`, `SiS_PWDOffset`, and `SiS661LCD2TableSize`, but it does not modify ROM contents. Low-level register helpers are immediate side-effect APIs and assume the caller already serialized access at the driver level.

## Dependencies and integration points
The file depends on Linux I/O primitives from `<asm/io.h>`, framebuffer structures from `<linux/fb.h>`, local type and table definitions from `init.h`, `initdef.h`, `vgatypes.h`, `vstruct.h`, `sis.h`, and `sisfb.h`, and generated/large timing tables from `300vtbl.h` and `310vtbl.h` under `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`.

It integrates with `sis_main.c`, which calls `SiSSetMode()` for normal mode changes and fallback/default modes, and with `initextlfb.c`, which uses `SiSInitPtr()` while querying linear framebuffer and mode details. It calls sibling bridge and chipset helpers such as `SiS_GetVBInfo()`, `SiS_SetYPbPr()`, `SiS_SetTVMode()`, `SiS_GetLCDResInfo()`, `SiS_SetCRT2Group()`, `SiS_DisableBridge()`, `SiS_UnLockCRT2()`, `SiS_WaitRetrace1()`, `SiS_IsDualEdge()`, `SiS_IsVAMode()`, `SiS_GetVCLK2Ptr()`, `SiS_GetRatePtr()`, `SiS_GetCH700x()`, and PCI config helpers such as `sisfb_read_nbridge_pci_dword()`.

Compile-time integration is heavily gated by `CONFIG_FB_SIS_300` and `CONFIG_FB_SIS_315`. A build with only one family enabled will reject unsupported chip families through `SiSInitPtr()`.

## Risks and edge cases
The main risk is direct hardware programming. Incorrect table data, chip detection, bridge detection, or register ordering can blank the screen, corrupt timings, or leave CRT2/LCDA state inconsistent. Many branches encode empirical legacy hardware behavior for specific chip revisions, ROM layouts, TV standards, and panel types; changes need real hardware coverage or very careful table-level comparison.

Mode ID helpers index depth-specific arrays directly, so callers must supply the expected small depth index rather than raw bits per pixel. `SiSSetMode()` has early failure paths after unlocking sequencer registers or before restoring all state; callers must treat a false return as a partially touched hardware state. Register access wrappers have no locking, range checking, or I/O failure reporting.

ROM parsing assumes enough valid bytes behind `VirtualRomBase` once `UseROM` is true. New-layout detection reads fixed offsets and version characters and can misclassify malformed ROMs. FIFO and clock routines perform integer arithmetic with mode and memory clocks; invalid clocks or custom timings can produce unsafe thresholds. The code also contains disabled or TODO paths for XGI dual-chip setup, SiS340 details, and Conexant support, which means apparent detection does not always imply full programming support.

## Test signals
Useful build signals are successful compilation with `CONFIG_FB_SIS_300`, `CONFIG_FB_SIS_315`, both enabled, and each family disabled where supported by Kconfig. Static checks should flag missing prototypes, impossible enum values, and array-index assumptions for mode depth.

Runtime validation needs hardware or emulation capable of SiS/XGI VGA I/O. High-value tests include setting standard VGA modes and extended modes through `sis_main.c`, verifying `SiSSetMode()` return values and visual output, checking fallback 640x480 initialization, exercising CRT-only, CRT2-only, simultaneous scan, LCDA, LCD, TV, and VGA2 paths, and confirming memory-size rejection for modes that exceed configured VRAM. Custom-mode tests should compare `SiS_CalcCRRegisters()` and `SiS_Generic_ConvertCRData()` against known timing values. Regression signals include unchanged register traces for representative chip/mode pairs, expected framebuffer clearing behavior, stable palette output, and no blank display after suspend/resume or repeated mode switches.
