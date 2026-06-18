
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Interface.h

Purpose: internal interface header connecting Kyro fbdev front-end code with STG4000 RAMDAC, timing generator, core PLL, and overlay helper implementation files.

Important APIs: declares `InitialiseRamdac()`, `DisableRamdacOutput()`, `EnableRamdacOutput()`, `DisableVGA()`, `StopVTG()`, `StartVTG()`, `SetupVTG()`, `ProgramClock()`, `SetCoreClockPLL()`, `ResetOverlayRegisters()`, `CreateOverlaySurface()`, `SetOverlayBlendMode()`, `SetOverlayViewPort()`, and `EnableOverlayPlane()`.

Control flow and integration: `fbdev.c` calls these helpers during mode set, overlay ioctl handling, probe, and remove. The helpers take `volatile STG4000REG __iomem *` and, for timing, `struct kyrofb_info` from `<video/kyro.h>`.

State and persistence: no state is declared here, but the interfaces expose hardware programming that mutates RAMDAC, VTG, PLL, overlay, and stream-control registers.

Dependencies: includes Linux PCI definitions and `<video/kyro.h>`, and expects `STG4000REG` plus overlay enums from `STG4000Reg.h` to be visible in including translation units before function use.

Risks: all functions are global within the linked object, with no namespace prefix beyond descriptive names. Unit contracts are implicit: pixel clocks, widths, offsets, and polarities must use the units expected by each helper. Overlay APIs rely on prior `CreateOverlaySurface()` state maintained inside `STG4000OverlayDevice.c`.

Test signals: compile-link coverage for `CONFIG_FB_KYRO`; mode set should call RAMDAC/VTG helpers in order; overlay ioctls should fail before surface creation and succeed after valid creation.
