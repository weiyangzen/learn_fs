# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/volt/gpio.c

## Purpose
Implements GPIO VID bit get/set and validation for voltage controllers using discrete VID pins.

## Important APIs, Types, And Functions
`nvkm_voltgpio_get()`, `nvkm_voltgpio_set()`, and `nvkm_voltgpio_init()` are the public helpers. The static `tags[]` table maps VID bit positions to DCB GPIO functions.

## Control Flow
Init verifies each VID bit has a GPIO function, masking missing bits when the VBIOS advertises more VID bits than the board wires. Get samples each valid bit and assembles a VID value; set writes each valid bit from the requested VID.

## State, Persistence, And Dependencies
State is the mutable `volt->vid_mask` and GPIO hardware levels.

## Integration Points
Depends on VBIOS GPIO metadata and the Nouveau GPIO subdev.

## Risks
Missing GPIOs are tolerated only for `-ENOENT`; other GPIO errors abort. Masking bits can reduce available voltage states.

## Test Signals
Signals include debug logs for missing VID bits, valid VID readback, and voltage changes through GPIO pins.
