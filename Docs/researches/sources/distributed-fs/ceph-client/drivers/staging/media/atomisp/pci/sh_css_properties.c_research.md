# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_properties.c

## Purpose
Implements a small public query that reports static CSS/ISP properties to callers.

## Important APIs, Types, and Functions
`ia_css_get_properties(struct ia_css_properties *properties)` fills `gdc_coord_one`, `l1_base_is_index`, and `vamem_type`. It derives GDC unity from `gdc_get_unity(GDC0_ID) / HRT_GDC_COORD_SCALE`.

## Control Flow
The routine asserts a non-null output pointer, computes the truncated GDC coordinate scale, then stores fixed properties for L1 addressing and VAMEM type.

## State and Persistence Behavior
No persistent state is modified. The returned values are a snapshot of hardware/static platform properties and are stable for the lifetime of the driver instance.

## Dependencies and Integration Points
Depends on `ia_css_properties.h`, `ia_css_types.h`, `assert_support.h`, and `gdc_device.h`. The values are consumed by upper CSS users that need coordinate scaling or memory-model details.

## Risks
Assumes `GDC0_ID` is the relevant GDC instance and that truncating the full GDC coordinate scale is acceptable. Any platform with different VAMEM or L1 behavior would need this function updated.

## Test Signals
Callers should observe nonzero `gdc_coord_one`, `l1_base_is_index == true`, and `vamem_type == IA_CSS_VAMEM_TYPE_2` during CSS property queries.
