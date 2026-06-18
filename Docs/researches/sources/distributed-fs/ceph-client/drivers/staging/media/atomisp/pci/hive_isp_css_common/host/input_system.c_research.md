# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_system.c

## Purpose

`input_system.c` owns ISP2400 input-system configuration state and commits CSI receiver, input buffer, multicast, acquisition, controller, input selector, and input-switch programming..

## Important APIs, Types, And Data

Key includes: `system_global.h`, `input_system.h`, `type_support.h`, `gp_device.h`, `assert_support.h`, `input_system_private.h`. Important macros/constants include `ZERO`, `ONE`. Important types include `break`. Important functions include `input_system_configure_channel()`, `input_system_configure_channel_sensor()`, `input_buffer_configuration()`, `configuration_to_registers()`, `receiver_rst()`, `input_system_network_rst()`, `capture_unit_configure()`, `acquisition_unit_configure()`, `ctrl_unit_configure()`, `input_system_network_configure()`, `set_csi_cfg()`, `set_source_type()`.

## Control Flow

The main flow starts with `input_system_configuration_reset()`, which disables receiver ports, resets the input network, clears GP-device/input-switch state, and marks all in-memory configuration flags as reset. Channel helper APIs build a `channel_cfg_t`, validate it through `input_system_configure_channel_sensor()`, merge input-switch LUT fields, and record target ISP/SP/stream2mem settings. `input_system_configuration_commit()` first partitions input-buffer SRAM in `input_buffer_configuration()`, then `configuration_to_registers()` translates the resulting model into multicast, mux, capture-unit, acquisition-unit, controller-unit, input-selector, and input-switch register writes.

## State And Persistence Behavior

This file has one important software state object, the static `input_system_cfg2400_t config`. Reset initializes flag fields and resource counters; channel configuration mutates it incrementally; commit consumes it to program hardware. Hardware state also persists in CSI receiver ports, GP-device input selector/switch registers, input-system multicast/mux registers, capture/acquisition units, and controller units.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- Only a subset of source types and buffering modes is supported; several comments mark reset/programming paths as temporary or unsafe, so unsupported modes should fail loudly.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
