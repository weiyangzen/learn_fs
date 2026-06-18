# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.h

## Purpose
Defines MB862xx GDC 2D/3D geometry engine register offsets, command codes, type codes, color register selectors, and raster operation constants used by acceleration code.

## Important APIs, Types, and Functions
- FIFO and engine registers such as `GDC_GEO_REG_INPUT_FIFO`, `GDC_REG_FIFO_COUNT`, `GDC_REG_MODE_BITMAP`, `GDC_REG_DRAW_BASE`, and `GDC_REG_X_RESOLUTION`.
- Drawing command codes such as `GDC_CMD_BLT_FILL`, `GDC_CMD_BLT_DRAW`, `GDC_CMD_BITMAP`, and directional BLT copy codes.
- Packet type codes such as `GDC_TYPE_SETREGISTER`, `GDC_TYPE_SETCOLORREGISTER`, `GDC_TYPE_DRAWRECTP`, `GDC_TYPE_DRAWBITMAPP`, and `GDC_TYPE_BLTCOPYP`.
- Raster operations `GDC_ROP_COPY`, `GDC_ROP_XOR`, and related ROP constants.

## Control Flow
No executable flow. `mb862xxfb_accel.c` composes command words by shifting these type and command constants into FIFO packet positions.

## State and Persistence
No software state. Constants refer to hardware engine state changed by emitted commands.

## Dependencies and Integration Points
Included by the acceleration implementation and indirectly tied to the GDC hardware command FIFO.

## Risks
The header is a large set of magic numeric constants with limited type safety. A typo in command composition can issue an unintended engine command. Several constants mention reserved or MB86293-later behavior, so callers must avoid using unsupported commands on older chips.

## Test Signals
Compile acceleration code and validate emitted command sequences on hardware or emulator traces. Visual tests for fill, copy, and imageblit are the practical regression signal.
