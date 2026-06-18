# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h` is the generic HRT IRQ-controller register index header in the Intel AtomISP CSS driver. It defines register indexes for edge, mask, status, clear, enable, edge-not-pulse, stream-output-enable, and register alignment.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_irq_controller_defs_h`, `_HRT_IRQ_CONTROLLER_EDGE_REG_IDX`, `_HRT_IRQ_CONTROLLER_MASK_REG_IDX`, `_HRT_IRQ_CONTROLLER_STATUS_REG_IDX`, `_HRT_IRQ_CONTROLLER_CLEAR_REG_IDX`, `_HRT_IRQ_CONTROLLER_ENABLE_REG_IDX`, `_HRT_IRQ_CONTROLLER_EDGE_NOT_PULSE_REG_IDX`, `_HRT_IRQ_CONTROLLER_STR_OUT_ENABLE_REG_IDX`, `_HRT_IRQ_CONTROLLER_REG_ALIGN`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Low-level IRQ controller helpers use these indexes to read status, mask/unmask, clear, and configure edge behavior.

## State and Persistence Behavior

State lives in IRQ-controller MMIO registers.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include writing the wrong register index and failing to preserve mask/edge state across reset.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 20 lines, 652 bytes.
