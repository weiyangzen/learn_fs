# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/regsnv04.h

## Purpose
Defines NV04 PTIMER MMIO register offsets shared by legacy timer implementations.

## Important APIs, Types, And Functions
Macros cover interrupt status, interrupt enable, numerator, denominator, time low/high, and alarm registers.

## Control Flow
C files include these constants to read/write PTIMER state through nvkm MMIO helpers.

## State, Persistence, And Dependencies
No runtime state exists in the header.

## Integration Points
Integrated by NV04, NV40, and NV41 timer files.

## Risks
Incorrect offsets would break all legacy timer operations. The header intentionally contains only constants.

## Test Signals
Build coverage and correct timer behavior on legacy chips validate these definitions.
