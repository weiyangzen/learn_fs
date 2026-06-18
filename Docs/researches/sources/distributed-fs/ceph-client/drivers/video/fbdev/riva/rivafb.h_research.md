# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb.h

## Purpose
`rivafb.h` is the shared private header for the RIVA fbdev driver. It defines VGA register-count constants, DDC bit masks, saved mode structures, I2C channel state, the main per-device `struct riva_par`, and cross-file prototypes.

## Important APIs, types, and functions
- `struct riva_regs` stores VGA attribute, CRTC, graphics, sequencer, misc output, and `RIVA_HW_STATE` extended registers.
- `struct riva_i2c_chan` stores the bit-banged DDC adapter, algorithm data, DDC base, and back-pointer.
- `struct riva_par` stores the embedded `RIVA_HW_INST`, pseudo/direct palettes, MMIO base, dclk limit, initial/current states, optional X86 VGA state, open lock/refcount, EDID pointer, chipset/flat-panel/CRTC flags, PCI device, cursor reset, write-combining cookie, and three I2C channels.
- Prototypes connect `nv_driver.c`, `rivafb-i2c.c`, and `riva_hw.c` to `fbdev.c`.

## Control flow
The header defines data contracts rather than executable flow. `fbdev.c` allocates `struct riva_par` inside `fb_info`, `nv_driver.c` fills hardware pointers/configuration, `riva_hw.c` mutates `RIVA_HW_INST` and extended states, and `rivafb-i2c.c` manages `chan[]`.

## State and persistence behavior
`struct riva_par` is the driver's primary persistent in-memory state for a bound PCI device. It survives from successful probe until remove, with mode state additionally saved/restored across open/release transitions. No state is written outside memory/hardware.

## Dependencies and integration points
It includes fbdev, VGA, I2C, I2C bit-bang, and `riva_hw.h`. Integration points are broad: every source in the RIVA subset shares this header, and its struct layout must remain consistent with allocation in `framebuffer_alloc()` and use in fbdev callbacks.

## Risks and test signals
Risks include lifetime ownership ambiguity for `EDID`, conditional `vgastate` fields, shared channel array state, and stale DDC mask macros not used by the bit-bang implementation. Test signals include clean builds under combinations of `CONFIG_X86` and `CONFIG_FB_RIVA_I2C`, successful probe/remove without leaks, and correct state restore after last framebuffer close.
