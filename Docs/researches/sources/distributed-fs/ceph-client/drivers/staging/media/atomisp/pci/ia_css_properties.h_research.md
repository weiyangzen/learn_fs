# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h` is the CSS hardware property query interface in the Intel AtomISP CSS driver. It defines `struct ia_css_properties` containing GDC coordinate scale, whether the L1 MMU base is an index, and the VAMEM type, plus `ia_css_get_properties()`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_properties`. Visible enums: `enum ia_css_vamem_type vamem_type;`. Important macros/constants: `__IA_CSS_PROPERTIES_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers query once during setup or capability reporting and branch on returned hardware constants.

## State and Persistence Behavior

The state is a snapshot of compiled/platform hardware properties.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are stale property values when supporting multiple ISP generations and misuse of MMU base semantics.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 33 lines, 857 bytes.
