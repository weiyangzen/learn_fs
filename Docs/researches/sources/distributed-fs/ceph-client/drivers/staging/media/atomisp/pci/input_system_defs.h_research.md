# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h` is the top-level input-system GP-register, reset, interrupt, stream-monitor, and DMA constants in the Intel AtomISP CSS driver. It maps multicast/mux registers, streaming monitor registers, soft-reset bit ids for capture/acquisition/DMA/CIO blocks, IRQ bit ids, and fixed DMA shape constants.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_system_defs_h`, `HIVE_CSI_CONFIG_MAIN`, `HIVE_CSI_CONFIG_STEREO1`, `HIVE_CSI_CONFIG_STEREO2`, `HIVE_ISYS_GPREG_MULTICAST_A_IDX`, `HIVE_ISYS_GPREG_MULTICAST_B_IDX`, `HIVE_ISYS_GPREG_MULTICAST_C_IDX`, `HIVE_ISYS_GPREG_MUX_IDX`, `HIVE_ISYS_GPREG_STRMON_STAT_IDX`, `HIVE_ISYS_GPREG_STRMON_COND_IDX`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input-system initialization and error handling use these values to reset subblocks, choose routes, monitor streams, and interpret interrupts.

## State and Persistence Behavior

State is hardware register and IRQ controller state.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are generation mismatch and reset ordering mistakes that leave capture or DMA subblocks wedged.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 118 lines, 5273 bytes.
