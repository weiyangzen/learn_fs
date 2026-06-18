# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h` is the morph table allocation API for GDC/lens correction in the Intel AtomISP CSS driver. It declares allocation and free helpers for `struct ia_css_morph_table`, whose full layout in `ia_css_types.h` carries six planes of X/Y coordinate arrays.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_morph_table *`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MORPH_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers allocate by grid width/height, fill coordinate planes, pass the table through ISP config, and free it when no pipe references it.

## State and Persistence Behavior

The table memory is host-owned, and `ia_css_isp_config` comments say morph tables are pointer-copied rather than deep-copied, so caller lifetime matters.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover allocation failure, zero dimensions, all six planes, and freeing after stream/pipe teardown.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 31 lines, 741 bytes.
