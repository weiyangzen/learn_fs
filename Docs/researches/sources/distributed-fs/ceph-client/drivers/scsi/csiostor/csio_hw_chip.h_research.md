# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_chip.h

## Purpose
`csio_hw_chip.h` defines chip-generation identification, firmware/config filenames, PCI device-table helpers, firmware version macros, memory-window constants, interrupt descriptor records, and the chip-specific operations table used by the hardware layer. It lets generic CSIostor code call T5/T6-specific register and memory routines through `struct csio_hw_chip_ops`.

## Important APIs, Types, and Constants
- Chip/device constants: `CSIO_HW_T5`, `CSIO_T5_FCOE_ASIC`, `CSIO_HW_T6`, `CSIO_T6_FCOE_ASIC`, and `CSIO_HW_CHIP_MASK`.
- Firmware assets: `FW_FNAME_T5`, `FW_CFG_NAME_T5`, `FW_FNAME_T6`, and `FW_CFG_NAME_T6`.
- `CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, and `CHELSIO_CHIP_RELEASE` encode/decode chip revision values.
- `enum chip_type` names supported T5/T6 revisions.
- `csio_is_t5()` and `csio_is_t6()` classify PCI device IDs after masking.
- `CSIO_DEVICE()` builds PCI table entries for Chelsio devices.
- `FW_VERSION()` and `FW_INTFVER()` bridge generated firmware version headers into driver comparisons.
- `struct fw_info` packages chip ID, firmware filename/module name, and expected `fw_hdr`.
- Memory constants include `MEM_EDC0`, `MEM_EDC1`, `MEM_MC`, `MEM_MC0`, `MEM_MC1`, `MEMWIN_APERTURE`, and `MEMWIN_BASE`.
- `struct intr_info` describes slow-path interrupt cause bits with message, stat index, and fatality.
- `struct csio_hw_chip_ops` exposes chip-specific methods for memory-window setup, PCIe interrupt handling, flash config address lookup, MC/EDC reads, generic memory read/write, and debugfs external memory creation.

## Control Flow and State
This header holds no persistent runtime state beyond type definitions. Runtime selection happens in hardware initialization, which fills `hw->chip_ops` with the externally defined `t5_ops` for supported T5/T6 paths. Generic code then calls `hw->chip_ops` from debugfs, interrupt handling, firmware config loading, and memory access paths.

## Dependencies and Integration Points
It includes `csio_defs.h`, `t4fw_api.h`, and `t4fw_version.h`, and forward-declares `struct csio_hw`. `csio_hw_t5.c` implements the exported `t5_ops`; `csio_init.c` uses `FW_FNAME_T5/FW_FNAME_T6` in module firmware declarations; PCI probe uses `csio_is_t5()`/`csio_is_t6()`.

## Risks and Edge Cases
- `csio_is_t5()` and `csio_is_t6()` compare only the masked chip-generation value, so callers must mask the PCI device with `CSIO_HW_CHIP_MASK`.
- T6 constants are declared, but this subset only includes the T5 ops implementation; generic code must ensure the selected ops are valid for the actual chip.
- Firmware filenames and version macros depend on external firmware headers and installed firmware blobs.
- `struct intr_info.stat_idx` is a raw index; users must keep it synchronized with the stats structures they increment.

## Test Signals
Probe should accept only masked T5/T6 IDs. Firmware loading tests should confirm the declared `MODULE_FIRMWARE()` names exist. Chip-op tests should verify `hw->chip_ops` is non-null and methods match the generation being probed. Interrupt tests can validate that `intr_info` tables log fatal and nonfatal causes correctly.
