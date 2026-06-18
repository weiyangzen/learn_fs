# sources/distributed-fs/ceph-client/include/video/maxinefb.h

## Purpose
`maxinefb.h` provides fixed physical/KSEG1 addresses and register numbers for the DECstation 5000/xx onboard framebuffer and IMS332 video controller.

## Important APIs, Types, and Functions
The file defines `MAXINEFB_IMS332_ADDRESS`, `DS5000_xx_ONBOARD_FBMEM_START`, and IMS332 register indices for cursor RAM, color palette, and cursor color palette. There are no functions or structs.

## Control Flow
Framebuffer code maps or directly accesses the uncached KSEG1 framebuffer base and IMS332 registers, then programs palette and hardware cursor memory using the register numbers multiplied by the controller's 32-bit register spacing.

## State and Persistence Behavior
Framebuffer pixels and IMS332 palette/cursor state are hardware memory/register state. They persist while the machine remains powered and are reset by firmware or driver initialization.

## Dependencies and Integration Points
The header depends on MIPS `asm/addrspace.h` for `KSEG1ADDR`. It integrates DECstation platform framebuffer code with fixed legacy memory maps.

## Risks and Test Signals
Risks include using cached instead of uncached addresses, wrong register scaling by four, palette byte-order mistakes (`0x00BBGGRR`), and assuming the onboard framebuffer exists on other DECstation models. Test signals include console display on DECstation 5000/xx, palette writes, cursor rendering, and platform gating around the fixed address map.
