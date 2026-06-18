
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sorc37d.c

## Purpose
Implements SOR output control for GV100/Turing-era C37D display core classes and reads SOR capabilities through the NVIF caps object.

## Important APIs, types, and functions
- `sorc37d_ctrl()` emits `NVC37D_SOR_SET_CONTROL(or)`.
- `sorc37d_get_caps()` reads `disp->caps` at `0x000144 + (or * 8)` and maps bit `0x04000000` to `dp_interlace`.
- `const struct nv50_outp_func sorc37d` exports the backend.

## Control flow
The display output code calls `.ctrl` with an already-formed control word; this file only serializes it into the core push channel. Capability probing uses `nvif_rd32()` instead of the older notifier BO path.

## State and persistence
No local state is retained. The output control method changes hardware core state; `get_caps` stores a boolean in the encoder capability cache.

## Dependencies and integration points
Depends on `core.h`, `nvif/pushc37b.h`, and `clc37d.h`. It integrates with the newer display caps object used by GV100+ display initialization.

## Risks
The raw caps offset and bit mask are hardware-contract details. Incorrect offsets silently misreport interlace support. Control words must be prepared by callers because this backend does not add polarity or depth fields.

## Test signals
DP interlace support should match hardware caps across SOR instances. Modeset tests should exercise SOR owner/protocol changes on C37D-class devices.
