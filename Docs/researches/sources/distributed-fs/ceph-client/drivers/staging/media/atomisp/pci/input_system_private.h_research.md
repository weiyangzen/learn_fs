# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h` is the private generation-specific input-system include aggregator in the Intel AtomISP CSS driver. It includes ISP2401 and ISP2400 private input-system headers, exposing implementation-only internals to selected C files.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow is compile-time inclusion, not runtime dispatch.

## State and Persistence Behavior

No state is declared directly here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are namespace collisions and accidental exposure of private generation-specific definitions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 8 lines, 241 bytes.
