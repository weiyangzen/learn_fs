# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h` is the input formatter subsystem register and IRQ bit definitions in the Intel AtomISP CSS driver. It maps input-switch LUT, fsync, soft-reset, channel/format, and IRQ bit ids for the IFMT GP-register block.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_if_subsystem_defs_h__`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_0`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_1`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_2`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_3`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_4`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_5`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_6`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_7`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_FSYNC_LUT_REG`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Low-level input formatter code writes these register indexes to route CSI channels/formats and reset IFMT subblocks.

## State and Persistence Behavior

State lives in MMIO registers addressed by these constants.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are off-by-one register indexes and mismatched reset bits across ISP generations.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 45 lines, 2080 bytes.
