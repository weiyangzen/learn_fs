# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h` is the shading table allocation API in the Intel AtomISP CSS driver. It declares `ia_css_shading_table_alloc()` and `ia_css_shading_table_free()` for lens shading correction tables described by `ia_css_shading_info` in `ia_css_types.h`.

## Important APIs, Types, and Functions

Visible functions: `ia_css_shading_table_alloc`. Visible structs: `struct ia_css_shading_table *`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_SHADING_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers allocate a table sized to CSS-reported shading grid info, fill per-color gains, attach it through ISP config, and retain it while the pipe can use it.

## State and Persistence Behavior

The memory is host-owned and referenced by pointer from config/pipe code rather than always deep-copied.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover grid dimensions from pipe info, null frees, allocation failure, and stream teardown with active shading tables.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 32 lines, 776 bytes.
