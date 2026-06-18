# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h` is the ISP2400 input-switch LUT helper and selection constants in the Intel AtomISP CSS driver. It provides macros to compute LUT register id and bit shift from channel id and MIPI format type, plus scalar/vector route selectors.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_switch_2400_defs_h`, `_HIVE_INPUT_SWITCH_GET_LUT_REG_ID`, `_HIVE_INPUT_SWITCH_GET_LUT_REG_LSB`, `HIVE_INPUT_SWITCH_SELECT_NO_OUTPUT`, `HIVE_INPUT_SWITCH_SELECT_IF_PRIM`, `HIVE_INPUT_SWITCH_SELECT_IF_SEC`, `HIVE_INPUT_SWITCH_SELECT_STR_TO_MEM`, `HIVE_INPUT_SWITCH_VSELECT_NO_OUTPUT`, `HIVE_INPUT_SWITCH_VSELECT_IF_PRIM`, `HIVE_INPUT_SWITCH_VSELECT_IF_SEC`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input routing code uses these macros to steer streams to primary IF, secondary IF, stream-to-memory, or no output.

## State and Persistence Behavior

State is the programmed input-switch LUT.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are invalid channel/format values and confusion between scalar and vector route encodings.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 22 lines, 806 bytes.
