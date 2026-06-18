# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h` is the public generation-specific input-system include aggregator in the Intel AtomISP CSS driver. It currently includes the ISP2400 public input-system API header.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Public users include this file to avoid directly selecting the generation-specific path.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are asymmetric generation coverage and accidental dependency on ISP2400-only public definitions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 7 lines, 198 bytes.
