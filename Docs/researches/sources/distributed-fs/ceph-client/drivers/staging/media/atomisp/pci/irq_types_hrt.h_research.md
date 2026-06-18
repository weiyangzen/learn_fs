# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h` is the HRT CSS interrupt id and status type header in the Intel AtomISP CSS driver. It maps CSS interrupt enum values to system-defined GPIO, SP, ISP, ISYS, ISEL, IFMT, stream monitor, memory error, timer, software pin, and DMA bit ids, and defines IRQ handling status values.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_HIVE_ISP_CSS_IRQ_TYPES_HRT_H_`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

HRT IRQ helpers and dispatchers use `hrt_isp_css_irq_t` ids to address interrupt-controller bits and return `hrt_isp_css_irq_status_t` while draining pending sources.

## State and Persistence Behavior

State is external interrupt-controller status.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are dependency on `HIVE_GP_DEV_IRQ_*` macros and enum drift when hardware interrupt sources change.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 60 lines, 3201 bytes.
