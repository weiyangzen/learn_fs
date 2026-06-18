# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h` is the input selector GP-register and IRQ definition header in the Intel AtomISP CSS driver. It defines bit widths and register indexes for sync generator, PRBS, TPG, channel id, format type, data/sideband/sync selection, soft reset, counters, and input-selector IRQs.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_selector_defs_h`, `HIVE_ISP_ISEL_SEL_BITS`, `HIVE_ISP_CH_ID_BITS`, `HIVE_ISP_FMT_TYPE_BITS`, `HIVE_ISEL_GP_REGS_SYNCGEN_ENABLE_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_FREE_RUNNING_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_PAUSE_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_FRAMES_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_PIX_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_LINES_IDX`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input setup code programs these registers when selecting FIFO, TPG, PRBS, or sensor-like generated input.

## State and Persistence Behavior

State is hardware register content.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include width truncation for channel/format fields and stale counter/IRQ assumptions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 80 lines, 3786 bytes.
