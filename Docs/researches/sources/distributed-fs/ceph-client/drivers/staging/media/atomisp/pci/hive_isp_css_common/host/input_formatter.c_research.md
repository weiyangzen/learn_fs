# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter.c

## Purpose

`input_formatter.c` resets input formatters, reports alignment, toggles FIFO blocking, and snapshots input formatter/input-switch/stream2mem hardware state..

## Important APIs, Types, And Data

Key includes: `system_global.h`, `input_formatter.h`, `type_support.h`, `gp_device.h`, `assert_support.h`, `input_formatter_private.h`. Important types include `return`. Important functions include `input_formatter_rst()`, `input_formatter_get_alignment()`, `input_formatter_set_fifo_blocking_mode()`, `input_formatter_get_switch_state()`, `input_formatter_get_state()`, `input_formatter_bin_get_state()`.

## Control Flow

`input_formatter_rst()` selects the reset offset and mask for the formatter ID and skips reset for the stream2mem/bin-copy block. State readers issue a sequence of register loads for crop, decimation, padding, VMEM, sync polarity, FIFO, FSM, and stream2mem status fields, while `input_formatter_get_switch_state()` reads LUT state from the GP device.

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
