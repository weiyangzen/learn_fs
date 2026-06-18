# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h` is the input-system controller register, reset, width, token, and acknowledge ABI in the Intel AtomISP CSS driver. It defines 23 controller registers, reset values, field widths, command token ids, acknowledge token ids, bit positions, port ids, and no-ack sentinel values for capture/acquisition/DMA control.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_system_ctrl_defs_h`, `_INPUT_SYSTEM_CTRL_REG_ALIGN`, `ISYS_CTRL_NOF_REGS`, `ISYS_CTRL_CAPT_START_ADDR_A_REG_ID`, `ISYS_CTRL_CAPT_START_ADDR_B_REG_ID`, `ISYS_CTRL_CAPT_START_ADDR_C_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_A_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_B_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_C_REG_ID`, `ISYS_CTRL_CAPT_NUM_MEM_REGIONS_A_REG_ID`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input-system code writes command tokens through NEXT/LAST command registers and observes acknowledge registers/FSM state to coordinate capture frame acquisition, external capture, acquisition reads, and overrule commands.

## State and Persistence Behavior

State persists in input-system control MMIO and FSMs.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are token bitfield packing errors, assuming reset values after partial reset, and failing to handle no-ack/device-error tokens.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 235 lines, 9979 bytes.
