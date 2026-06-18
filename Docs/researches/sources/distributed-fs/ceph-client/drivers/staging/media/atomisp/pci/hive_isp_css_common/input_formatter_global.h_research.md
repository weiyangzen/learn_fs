# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/input_formatter_global.h

## Purpose

`input_formatter_global.h` defines the shared `input formatter` contract for the AtomISP CSS common layer, covering input formatter register offsets, input-switch LUT helpers, stream2mem register addresses, and the shared input formatter configuration struct.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `system_local.h`, `if_defs.h`, `str2mem_defs.h`, `input_switch_2400_defs.h`. Important macros/constants include `__INPUT_FORMATTER_GLOBAL_H_INCLUDED__`, `IS_INPUT_FORMATTER_VERSION2`, `IS_INPUT_SWITCH_VERSION2`, `_HIVE_INPUT_SWITCH_GET_FSYNC_REG_LSB`, `HIVE_SWITCH_N_CHANNELS`, `HIVE_SWITCH_N_FORMATTYPES`, `HIVE_SWITCH_N_SWITCH_CODE`, `HIVE_SWITCH_M_CHANNELS`, `HIVE_SWITCH_M_FORMATTYPES`, `HIVE_SWITCH_M_SWITCH_CODE`. Important types include `input_formatter_cfg_s`.

## Control Flow

Control flow is indirect: public and private host wrappers include this header, then issue register or memory operations using these IDs, bit positions, and shared structs. Firmware-facing data structures must remain layout-compatible because SP/ISP code and host code share the same contract.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
