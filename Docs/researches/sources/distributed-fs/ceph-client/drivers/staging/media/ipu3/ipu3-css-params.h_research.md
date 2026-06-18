# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-params.h

## Purpose
`ipu3-css-params.h` declares the CSS parameter conversion API used by the streaming core.

## Important APIs, Types, and Functions
- `imgu_css_cfg_acc()` fills accelerator parameters from user flags, old state, current CSS geometry, and defaults.
- `imgu_css_cfg_vmem0()` and `imgu_css_cfg_dmem0()` fill firmware late-binding parameter memories.
- `imgu_css_cfg_gdc_table()` generates a no-warp GDC/DVS table.

## Control Flow
`ipu3-css.c` allocates DMA-backed buffers from pools, passes old/current virtual addresses plus user flags, and receives populated ABI memory blocks or an error code.

## State and Persistence Behavior
The header stores no state. Its function signatures define how previous parameter generations are handed to the conversion layer for state preservation.

## Dependencies and Integration Points
It requires visibility of CSS, UAPI parameter, and ABI parameter types from surrounding includes. It is the contract between parameter queueing and the conversion implementation.

## Risks
The API uses raw pointers for firmware memory blocks, so callers must pass buffers matching the selected firmware binary's declared sizes and offsets.

## Test Signals
Compile checks should catch signature drift. Runtime tests should confirm omitted user sections preserve old values and invalid layouts/geometries are rejected.
