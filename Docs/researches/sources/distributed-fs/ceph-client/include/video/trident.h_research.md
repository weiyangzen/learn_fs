<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/trident.h -->
# sources/distributed-fs/ceph-client/include/video/trident.h

## Purpose
This header defines Trident framebuffer debug/output macros, supported PCI IDs, LCD policy constants, VGA extension register indices, graphics-engine offsets, and common ROP values.

## Important APIs, Types, And Functions
- `TRIDENTFB_DEBUG` controls `debug()` logging; `output()` logs with the `tridentfb` prefix.
- PCI IDs cover Cyber, TGUI, ProVIDIA, Image, Blade3D, and CyberBlade families.
- `LCD_STRETCH`, `LCD_CENTER`, and `LCD_BIOS` select laptop panel scaling policy.
- Register constants cover sequencer (`3C4`), CRTC (`3x4`), graphics (`3CE`) extensions, LCD/TV registers, memory clock, I2C, cursor, and graphics engine registers.
- `ROP_S`, `ROP_P`, and `ROP_X` define source, pattern, and XOR raster operations.

## Control Flow
The driver uses PCI IDs to select chipset behavior, unlocks protected registers via key registers, programs clocks/memory/LCD scaling through extension indices, and uses graphics engine registers for acceleration. Debug macros add trace points when enabled at compile time.

## State And Persistence
No software state is declared. State is held in VGA extension registers, graphics-engine registers, LCD policy variables in the implementation, and PCI/chip detection results.

## Dependencies And Integration Points
It integrates with Trident fbdev implementation, PCI probing, VGA indexed register access, laptop LCD scaling, I2C/DDC register handling, and graphics acceleration.

## Risks And Edge Cases
Some comments note mismatched "real" PCI IDs; detection code must handle aliases. Many registers share indices across old/new chips, so generation gating is required. LCD stretch/center/BIOS policy can conflict with panel native timing.

## Test Signals
Probe should identify each supported chipset, unlock and program extension registers, read DDC where available, set LCD scaling modes, and complete graphics-engine copy/fill operations with expected ROP results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/trident.h -->
