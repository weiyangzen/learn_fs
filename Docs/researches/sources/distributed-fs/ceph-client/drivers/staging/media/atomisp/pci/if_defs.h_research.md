# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h` is the input formatter request token constants in the Intel AtomISP CSS driver. It defines request token base values for frame, line, and vector requests.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_IF_DEFS_H`, `HIVE_IF_FRAME_REQUEST`, `HIVE_IF_LINES_REQUEST`, `HIVE_IF_VECTORS_REQUEST`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input formatter and firmware code use these constants when interpreting or issuing HIVE input formatter requests.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are magic-number drift against firmware definitions and insufficient type safety around token construction.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 14 lines, 336 bytes.
