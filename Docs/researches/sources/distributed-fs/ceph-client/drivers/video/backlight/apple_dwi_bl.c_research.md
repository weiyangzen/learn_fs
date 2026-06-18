# sources/distributed-fs/ceph-client/drivers/video/backlight/apple_dwi_bl.c

## Purpose
This platform driver controls Apple DWI two-wire-interface backlight controllers through memory-mapped command and control registers, primarily for Apple SoC systems.

## Important APIs, types, and functions
`struct apple_dwi_bl` stores the MMIO base. Important routines are `dwi_bl_update_status`, `dwi_bl_get_brightness`, and `dwi_bl_probe`. Register definitions cover command type/data fields and control send bits, including `SEND4` for Apple A9 and later. The OF compatible is `apple,dwi-bl`.

## Control flow
Probe allocates state, ioremaps the first platform resource, registers a platform-type linear backlight with max 2047, and seeds brightness from the current command register. Brightness updates build a set-brightness command with `FIELD_PREP`, write it to `DWI_BL_CMD`, and trigger transmission by writing the combined send bits to `DWI_BL_CTL`.

## State and persistence
The driver keeps only the MMIO base pointer. Brightness state is read back from the command register and mirrored by the backlight core. Hardware state persists in controller registers.

## Dependencies and integration points
It depends on platform resources, OF matching, MMIO accessors, bitfield helpers, and the backlight core.

## Risks and test signals
Risks include applying `SEND4` on older variants if incompatible, no explicit range clamp beyond backlight core properties, lack of runtime PM/disable path, and command-register readback not necessarily reflecting panel output. Test signals include OF probe, MMIO resource failure, brightness 0/max/intermediate writes, suspend/resume via core option, and hardware validation on pre-A9 and A9+ controllers.
