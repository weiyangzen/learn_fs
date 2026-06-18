# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/drf.h

## Purpose
Provides generic NVIDIA DRF bitfield helpers for packing, extracting, testing, setting, and read-modify-writing register or method fields, including multi-word fields.

## Important APIs, Types, And Functions
Core helpers include `DRF_LO`, `DRF_HI`, `DRF_BITS`, `DRF_MASK`, `DRF_SMASK`, `NVVAL`, `NVDEF`, `NVVAL_GET`, `NVVAL_SET`, `NVDEF_SET`, `NVVAL_TEST`, `NVDEF_TEST`, multi-word `NVVAL_MW_GET/SET`, and object accessor families `DRF_RD`, `DRF_WR`, `DRF_MR`, `DRF_RV`, `DRF_WV`, `DRF_WD`, `DRF_MV`, `DRF_MD`, `DRF_TV`, and `DRF_TD`.

## Control Flow
All behavior is macro expansion. Selector macros choose indexed versus non-indexed fields and field-value versus named-definition variants. Read-modify helpers read an object through caller-supplied accessors, mask/merge values, write back, and return the previous field value.

## State And Persistence
The header stores no state. It mutates whichever register, mapped object, or in-memory descriptor the caller accessor targets.

## Dependencies And Integration Points
Used throughout NVIF/NVKM/NVHW code to manipulate generated bit ranges such as `31:16`. `nvif/object.h` and `nvkm/core/device.h` wrap it for MMIO/register access.

## Risks
The macros assume field definitions are valid C expressions using the `hi:lo` trick. Widths near 64 bits, signed shifts, multi-word fields, side-effecting arguments, and mismatched object element sizes are risk points.

## Test Signals
Compile failures catch malformed field names. Runtime validation comes from correct register programming, pushbuffer encoding, descriptor construction, and targeted unit-style checks for field pack/extract edge cases.
