# subset-b-005402 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_defs.h

## Purpose

`css_receiver_2400_defs.h` defines the ISP2400 CSS CSI-2 receiver and backend register layout, data widths, port offsets, interrupt bits, compression fields, RAW16/RAW18 controls, and backend soft-reset fields.

## Important APIs, Types, And Data

Key includes: `css_receiver_2400_common_defs.h`. Important macros/constants include `_css_receiver_2400_defs_h_`, `CSS_RECEIVER_DATA_WIDTH`, `CSS_RECEIVER_RX_TRIG`, `CSS_RECEIVER_RF_WORD`, `CSS_RECEIVER_IMG_PROC_RF_ADDR`, `CSS_RECEIVER_CSI_RF_ADDR`, `CSS_RECEIVER_DATA_OUT`, `CSS_RECEIVER_CHN_NO`, `CSS_RECEIVER_DWORD_CNT`, `CSS_RECEIVER_FORMAT_TYP`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_receiver_2400_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_trace.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_trace.h

## Purpose

`css_trace.h` defines the shared SP/ISP trace buffer ABI: trace item/header layouts, trace-buffer partitioning, trace command encodings, circular index helpers, and bit-packing macros for regular, quick, formatted, and 24-bit trace points.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `sh_css_internal.h`. Important macros/constants include `__CSS_TRACE_H_`, `MAX_SCRATCH_DATA`, `MAX_CMD_DATA`, `HDR_HDR_OFFSET`, `HDR_COMMAND_OFFSET`, `HDR_DATA_OFFSET`, `HDR_DEBUG_SIGNATURE_OFFSET`, `HDR_DEBUG_POINTER_OFFSET`, `HDR_STATUS_OFFSET`, `HDR_STATUS_OFFSET_BYTE`. Important types include `DBG_commands`.

## Control Flow

The file is macro-only support code. Control flow appears at expansion sites in callers, so tests need to exercise both valid and invalid macro inputs in the surrounding CSS host code.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- `FIELD_FORMAT_MASK` is derived from `FIELD_MAJOR_W_FMT_WIDTH` rather than `FIELD_FORMAT_WIDTH`; because both are small constants this deserves review before changing trace format width.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/dma_v2_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/dma_v2_defs.h

## Purpose

`dma_v2_defs.h` defines the DMA v2 command word, parameter word, register selection, command IDs, no-ack variants, channel parameter IDs, and debug status field indexes used by the higher-level DMA API.

## Important APIs, Types, And Data

Important macros/constants include `_dma_v2_defs_h`, `_DMA_V2_NUM_CHANNELS_ID`, `_DMA_V2_CONNECTIONS_ID`, `_DMA_V2_DEV_ELEM_WIDTHS_ID`, `_DMA_V2_DEV_FIFO_DEPTH_ID`, `_DMA_V2_DEV_FIFO_RD_LAT_ID`, `_DMA_V2_DEV_FIFO_LAT_BYPASS_ID`, `_DMA_V2_DEV_NO_BURST_ID`, `_DMA_V2_DEV_RD_ACCEPT_ID`, `_DMA_V2_DEV_SRMD_ID`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/dma_v2_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gdc_v2_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gdc_v2_defs.h

## Purpose

`gdc_v2_defs.h` defines the geometric distortion correction v2 token protocol, LUT dimensions, interpolation coefficient formats, register indexes, fixed-point limits, and mode constants.

## Important APIs, Types, And Data

Important macros/constants include `HRT_GDC_v2_defs_h_`, `HRT_GDC_IS_V2`, `HRT_GDC_N`, `HRT_GDC_FRAC_BITS`, `HRT_GDC_BLI_FRAC_BITS`, `HRT_GDC_BLI_COEF_ONE`, `HRT_GDC_BCI_COEF_BITS`, `HRT_GDC_BCI_COEF_ONE`, `HRT_GDC_BCI_COEF_MASK`, `HRT_GDC_LUT_BYTES`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gdc_v2_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gp_timer_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gp_timer_defs.h

## Purpose

`gp_timer_defs.h` defines the GP timer register index formulae for reset, global enable, per-timer enable/value/count-type/signal-select, IRQ trigger/timer-select/enable, and count-type constants.

## Important APIs, Types, And Data

Important macros/constants include `_gp_timer_defs_h`, `_HRT_GP_TIMER_REG_ALIGN`, `HIVE_GP_TIMER_RESET_REG_IDX`, `HIVE_GP_TIMER_OVERALL_ENABLE_REG_IDX`, `HIVE_GP_TIMER_ENABLE_REG_IDX`, `HIVE_GP_TIMER_VALUE_REG_IDX`, `HIVE_GP_TIMER_COUNT_TYPE_REG_IDX`, `HIVE_GP_TIMER_SIGNAL_SELECT_REG_IDX`, `HIVE_GP_TIMER_IRQ_TRIGGER_VALUE_REG_IDX`, `HIVE_GP_TIMER_IRQ_TIMER_SELECT_REG_IDX`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gp_timer_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gpio_block_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gpio_block_defs.h

## Purpose

`gpio_block_defs.h` defines the tiny GPIO block register index map for data output enable, data output select, and two data output registers.

## Important APIs, Types, And Data

Important macros/constants include `_gpio_block_defs_h_`, `_gpio_block_reg_do_e`, `_gpio_block_reg_do_select`, `_gpio_block_reg_do_0`, `_gpio_block_reg_do_1`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/gpio_block_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/debug_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/debug_global.h

## Purpose

`debug_global.h` defines the shared `debug` contract for the AtomISP CSS common layer, covering shared debug-buffer ABI and DDR/DMEM offsets.

## Important APIs, Types, And Data

Key includes: `type_support.h`. Important macros/constants include `__DEBUG_GLOBAL_H_INCLUDED__`, `DEBUG_BUF_SIZE`, `DEBUG_BUF_MASK`, `DEBUG_DATA_ENABLE_ADDR`, `DEBUG_DATA_BUF_MODE_ADDR`, `DEBUG_DATA_HEAD_ADDR`, `DEBUG_DATA_TAIL_ADDR`, `DEBUG_DATA_BUF_ADDR`, `DEBUG_DATA_ENABLE_DDR_ADDR`, `DEBUG_DATA_BUF_MODE_DDR_ADDR`. Important types include `debug_buf_mode_t`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/debug_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/dma_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/dma_global.h

## Purpose

`dma_global.h` defines the shared `dma` contract for the AtomISP CSS common layer, covering DMA channel/connection enums, token packing helpers, transfer/config enums, and channel configuration structs.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `dma_v2_defs.h`. Important macros/constants include `__DMA_GLOBAL_H_INCLUDED__`, `IS_DMA_VERSION_2`, `HIVE_ISP_NUM_DMA_CONNS`, `HIVE_ISP_NUM_DMA_CHANNELS`, `N_DMA_CHANNEL_ID`, `_DMA_PACKING_SETUP_PARAM`, `_DMA_HEIGHT_PARAM`, `_DMA_STRIDE_A_PARAM`, `_DMA_ELEM_CROPPING_A_PARAM`, `_DMA_WIDTH_A_PARAM`. Important types include `unsigned`, `dma_connection`, `dma_extension`, `dma_transfer_type_t`, `dma_config_type_t`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/dma_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/event_fifo_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/event_fifo_global.h

## Purpose

`event_fifo_global.h` defines the shared `event fifo` contract for the AtomISP CSS common layer, covering event FIFO interface marker for the common CSS event FIFO block.

## Important APIs, Types, And Data

Important macros/constants include `__EVENT_FIFO_GLOBAL_H`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/event_fifo_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/fifo_monitor_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/fifo_monitor_global.h

## Purpose

`fifo_monitor_global.h` defines the shared `fifo monitor` contract for the AtomISP CSS common layer, covering stream FIFO monitor channel, switch, state, and handshake types.

## Important APIs, Types, And Data

Important macros/constants include `__FIFO_MONITOR_GLOBAL_H_INCLUDED__`, `IS_FIFO_MONITOR_VERSION_2`, `HIVE_ISP_CSS_STREAM_SWITCH_NONE`, `HIVE_ISP_CSS_STREAM_SWITCH_SP`, `HIVE_ISP_CSS_STREAM_SWITCH_ISP`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/fifo_monitor_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gdc_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gdc_global.h

## Purpose

`gdc_global.h` defines the shared `gdc` contract for the AtomISP CSS common layer, covering GDC parameter-memory layouts, bit-depth choices, coordinate scale, and channel identifiers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `gdc_v2_defs.h`. Important macros/constants include `__GDC_GLOBAL_H_INCLUDED__`, `IS_GDC_VERSION_2`, `GDC_PARAM_ICX_LEFT_ROUNDED_IDX`, `GDC_PARAM_OXDIM_FLOORED_IDX`, `GDC_PARAM_OXDIM_LAST_IDX`, `GDC_PARAM_WOIX_LAST_IDX`, `GDC_PARAM_IY_TOPLEFT_IDX`, `GDC_PARAM_CHUNK_CNT_IDX`, `GDC_PARAM_BPP_IDX`, `GDC_PARAM_BLOCK_HEIGHT_IDX`. Important types include `gdc_scale_param_mem_s`, `gdc_warp_param_mem_s`, `gdc_channel_ID_t`, `gdc_bits_per_pixel_t`, `gdc_scale_param_mem_t`, `gdc_warp_param_mem_t`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gdc_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_device_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_device_global.h

## Purpose

`gp_device_global.h` defines the shared `gp device` contract for the AtomISP CSS common layer, covering GP-device register addresses for software IRQs, input switch LUTs, sync generator, input selector, PRBS/test-pattern generator, and soft reset.

## Important APIs, Types, And Data

Important macros/constants include `__GP_DEVICE_GLOBAL_H_INCLUDED__`, `IS_GP_DEVICE_VERSION_2`, `_REG_GP_IRQ_REQ0_ADDR`, `_REG_GP_IRQ_REQ1_ADDR`, `_REG_GP_IRQ_REQUEST0_ADDR`, `_REG_GP_IRQ_REQUEST1_ADDR`, `_REG_GP_SWITCH_IF_ADDR`, `_REG_GP_SWITCH_GDC1_ADDR`, `_REG_GP_SWITCH_GDC2_ADDR`, `_REG_GP_IFMT_input_switch_lut_reg0`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_device_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_timer_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_timer_global.h

## Purpose

`gp_timer_global.h` defines the shared `gp timer` contract for the AtomISP CSS common layer, covering GP timer interface marker for timer block IDs supplied by the platform headers.

## Important APIs, Types, And Data

Key includes: `hive_isp_css_defs.h`. Important macros/constants include `__GP_TIMER_GLOBAL_H_INCLUDED__`, `GP_TIMER_COUNT_TYPE_HIGH`, `GP_TIMER_COUNT_TYPE_LOW`, `GP_TIMER_COUNT_TYPE_POSEDGE`, `GP_TIMER_COUNT_TYPE_NEGEDGE`, `GP_TIMER_COUNT_TYPE_TYPES`, `GP_TIMER_SEL`, `GP_TIMER_SIGNAL_SELECT`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gp_timer_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gpio_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gpio_global.h

## Purpose

`gpio_global.h` defines the shared `gpio` contract for the AtomISP CSS common layer, covering GPIO interface marker for the common CSS GPIO block.

## Important APIs, Types, And Data

Key includes: `gpio_block_defs.h`. Important macros/constants include `__GPIO_GLOBAL_H_INCLUDED__`, `HIVE_GPIO_STROBE_TRIGGER_PIN`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/gpio_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/hmem_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/hmem_global.h

## Purpose

`hmem_global.h` defines the shared `hmem` contract for the AtomISP CSS common layer, covering host-memory interface marker and shared HMEM type surface.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `isp.h`. Important macros/constants include `__HMEM_GLOBAL_H_INCLUDED__`, `IS_HMEM_VERSION_1`, `ISP_HIST_ADDRESS_BITS`, `ISP_HIST_ALIGNMENT`, `ISP_HIST_COMP_IN_PREC`, `ISP_HIST_DEPTH`, `ISP_HIST_WIDTH`, `ISP_HIST_COMPONENTS`, `ISP_HIST_ALIGNMENT_LOG2`, `HMEM_SIZE_LOG2`. Important types include `u32`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/hmem_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug.c

## Purpose

`debug.c` initializes and changes the CSS debug circular/linear buffer by storing enable, mode, head, tail, and DDR pointer fields into SP-visible memory..

## Important APIs, Types, And Data

Key includes: `debug.h`, `hmm.h`, `debug_private.h`, `sp.h`, `assert_support.h`. Important macros/constants include `__INLINE_SP__`. Important functions include `debug_buffer_init()`, `debug_buffer_ddr_init()`, `debug_buffer_setmode()`.

## Control Flow

The init paths store the debug buffer base or DDR pointer and clear the control fields. `debug_buffer_setmode()` changes the buffer mode field while leaving data ownership to SP/ISP firmware and host readers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_local.h

## Purpose

`debug_local.h` is the local include layer for the `debug` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `debug_global.h`. Important macros/constants include `__DEBUG_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_private.h

## Purpose

`debug_private.h` is the private include layer for the `debug` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `debug_public.h`, `sp.h`, `isp.h`, `assert_support.h`. Important macros/constants include `__DEBUG_PRIVATE_H_INCLUDED__`, `__INLINE_ISP__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/debug_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma.c

## Purpose

`dma.c` provides the non-inline compilation unit for DMA helpers; the active operations are supplied by the included private header depending on inline configuration..

## Important APIs, Types, And Data

Key includes: `linux/kernel.h`, `dma.h`, `assert_support.h`, `dma_private.h`. Important functions include `dma_set_max_burst_size()`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_local.h

## Purpose

`dma_local.h` is the local include layer for the `dma` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `dma_global.h`, `bits.h`, `hive_isp_css_defs.h`, `dma_v2_defs.h`. Important macros/constants include `__DMA_LOCAL_H_INCLUDED__`, `_DMA_FSM_GROUP_CMD_IDX`, `_DMA_FSM_GROUP_ADDR_A_IDX`, `_DMA_FSM_GROUP_ADDR_B_IDX`, `_DMA_FSM_GROUP_CMD_CTRL_IDX`, `_DMA_FSM_GROUP_FSM_CTRL_IDX`, `_DMA_FSM_GROUP_FSM_CTRL_STATE_IDX`, `_DMA_FSM_GROUP_FSM_CTRL_REQ_DEV_IDX`, `_DMA_FSM_GROUP_FSM_CTRL_REQ_ADDR_IDX`, `_DMA_FSM_GROUP_FSM_CTRL_REQ_STRIDE_IDX`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_private.h

## Purpose

`dma_private.h` is the private include layer for the `dma` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `dma_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__DMA_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/dma_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo.c

## Purpose

`event_fifo.c` provides the event FIFO compilation unit; functionality is supplied by the private inline accessors selected by the build..

## Important APIs, Types, And Data

Key includes: `event_fifo.h`, `event_fifo_private.h`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_local.h

## Purpose

`event_fifo_local.h` is the local include layer for the `event fifo` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `event_fifo_global.h`. Important macros/constants include `_EVENT_FIFO_LOCAL_H`, `EVENT_QUERY_BIT`. Important types include `event_ID_t`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_private.h

## Purpose

`event_fifo_private.h` is the private include layer for the `event fifo` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `event_fifo_public.h`, `device_access.h`, `assert_support.h`, `bits.h`. Important macros/constants include `__EVENT_FIFO_PRIVATE_H`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/event_fifo_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor.c

## Purpose

`fifo_monitor.c` samples stream handshake state for every modeled FIFO channel and reads switch-selection registers from the GP device..

## Important APIs, Types, And Data

Key includes: `fifo_monitor.h`, `type_support.h`, `device_access.h`, `bits.h`, `gp_device.h`, `assert_support.h`, `fifo_monitor_private.h`. Important macros/constants include `STORAGE_CLASS_FIFO_MONITOR_DATA`. Important types include `break`, `return`. Important functions include `fifo_monitor_status_valid()`, `fifo_monitor_status_accept()`, `fifo_channel_get_state()`, `fifo_switch_get_state()`, `fifo_monitor_get_state()`.

## Control Flow

`fifo_monitor_get_state()` walks every `fifo_channel_t` and `fifo_switch_t`. Each channel case maps a logical source/fifo/sink direction to a GP stream-status register and port index; `fifo_monitor_status_valid()` and `fifo_monitor_status_accept()` decode the two-bit valid/accept pair. Host-facing channels use hard-coded device-access addresses for FIFO-empty state where no normal stream monitor is connected.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- Some host FIFO states use hard-coded device addresses and several channel cases carry legacy comments, making platform migration risky.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_local.h

## Purpose

`fifo_monitor_local.h` is the local include layer for the `fifo monitor` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `fifo_monitor_global.h`, `hive_isp_css_defs.h`. Important macros/constants include `__FIFO_MONITOR_LOCAL_H_INCLUDED__`, `_hive_str_mon_valid_offset`, `_hive_str_mon_accept_offset`, `FIFO_CHANNEL_SP_VALID_MASK`, `FIFO_CHANNEL_SP_VALID_B_MASK`, `FIFO_CHANNEL_ISP_VALID_MASK`, `FIFO_CHANNEL_MOD_VALID_MASK`. Important types include `fifo_switch`, `fifo_channel`, `fifo_switch_t`, `fifo_channel_t`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_private.h

## Purpose

`fifo_monitor_private.h` is the private include layer for the `fifo monitor` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `fifo_monitor_public.h`, `gp_device.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__FIFO_MONITOR_PRIVATE_H_INCLUDED__`, `__INLINE_GP_DEVICE__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/fifo_monitor_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc.c

## Purpose

`gdc.c` writes GDC LUT data, converts LUTs to packed ISP format, and reports the unity scale constant used by GDC programming..

## Important APIs, Types, And Data

Key includes: `gdc_device.h`, `device_access.h`, `assert_support.h`, `gdc_private.h`. Important types include `return`. Important functions include `gdc_reg_store()`, `gdc_lut_store()`, `gdc_lut_convert_to_isp_format()`, `gdc_get_unity()`.

## Control Flow

GDC register writes are sent as packed command tokens through `gdc_reg_store()`. `gdc_lut_store()` walks LUT entries and writes paired coefficients to the LUT register window, while `gdc_lut_convert_to_isp_format()` reorganizes four input coefficient planes into the ISP/GDC packed layout consumed by the device.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_local.h

## Purpose

`gdc_local.h` is the local include layer for the `gdc` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `gdc_global.h`. Important macros/constants include `__GDC_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_private.h

## Purpose

`gdc_private.h` is the private include layer for the `gdc` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `gdc_public.h`. Important macros/constants include `__GDC_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gdc_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device.c

## Purpose

`gp_device.c` provides the GP-device compilation unit that exposes register access helpers through the private header..

## Important APIs, Types, And Data

Key includes: `assert_support.h`, `gp_device.h`, `gp_device_private.h`. Important functions include `gp_device_get_state()`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_local.h

## Purpose

`gp_device_local.h` is the local include layer for the `gp device` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `gp_device_global.h`. Important macros/constants include `__GP_DEVICE_LOCAL_H_INCLUDED__`, `_REG_GP_SDRAM_WAKEUP_ADDR`, `_REG_GP_IDLE_ADDR`, `_REG_GP_SP_STREAM_STAT_ADDR`, `_REG_GP_SP_STREAM_STAT_B_ADDR`, `_REG_GP_ISP_STREAM_STAT_ADDR`, `_REG_GP_MOD_STREAM_STAT_ADDR`, `_REG_GP_SP_STREAM_STAT_IRQ_COND_ADDR`, `_REG_GP_SP_STREAM_STAT_B_IRQ_COND_ADDR`, `_REG_GP_ISP_STREAM_STAT_IRQ_COND_ADDR`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_private.h

## Purpose

`gp_device_private.h` is the private include layer for the `gp device` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `gp_device_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__GP_DEVICE_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_device_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer.c

## Purpose

`gp_timer.c` implements GP timer reset, enable, value, count-type, signal-select, and IRQ trigger/timer-select/enable programming..

## Important APIs, Types, And Data

Key includes: `type_support.h`, `gp_timer.h`, `gp_timer_private.h`, `system_local.h`. Important functions include `gp_timer_reg_store()`, `gp_timer_init()`.

## Control Flow

Each API computes the register index from `gp_timer_defs.h` and stores or loads a single timer/IRQ field. Reset and global enable affect the whole block; timer enable/value/count-type/signal-select calls address a specific counter; IRQ calls program trigger value, timer source, and enable state.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_local.h

## Purpose

`gp_timer_local.h` is the local include layer for the `gp timer` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `gp_timer_global.h`, `gp_timer_defs.h`, `hive_isp_css_defs.h`. Important macros/constants include `__GP_TIMER_LOCAL_H_INCLUDED__`, `_REG_GP_TIMER_RESET_REG`, `_REG_GP_TIMER_OVERALL_ENABLE`, `_REG_GP_TIMER_ENABLE_ID`, `_REG_GP_TIMER_VALUE_ID`, `_REG_GP_TIMER_COUNT_TYPE_ID`, `_REG_GP_TIMER_SIGNAL_SELECT_ID`, `_REG_GP_TIMER_IRQ_TRIGGER_VALUE_ID`, `_REG_GP_TIMER_IRQ_TIMER_SELECT_ID`, `_REG_GP_TIMER_IRQ_ENABLE_ID`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_private.h

## Purpose

`gp_timer_private.h` is the private include layer for the `gp timer` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `gp_timer_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__GP_TIMER_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gp_timer_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gpio_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gpio_private.h

## Purpose

`gpio_private.h` is the private include layer for the `gpio` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `assert_support.h`, `device_access.h`. Important macros/constants include `__GPIO_PRIVATE_H_INCLUDED__`. Important functions include `gpio_reg_store()`, `gpio_reg_load()`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/gpio_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem.c

## Purpose

`hmem.c` provides the HMEM compilation unit whose accessors are selected through the private inline header..

## Important APIs, Types, And Data

Key includes: `hmem.h`, `hmem_private.h`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_local.h

## Purpose

`hmem_local.h` is the local include layer for the `hmem` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `hmem_global.h`. Important macros/constants include `__HMEM_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_private.h

## Purpose

`hmem_private.h` is the private include layer for the `hmem` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `hmem_public.h`, `assert_support.h`. Important macros/constants include `__HMEM_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/hmem_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_local.h

## Purpose

`input_formatter_local.h` is the local include layer for the `input formatter` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `input_formatter_global.h`, `isp.h`. Important macros/constants include `__INPUT_FORMATTER_LOCAL_H_INCLUDED__`, `HIVE_IF_FSM_SYNC_STATUS`, `HIVE_IF_FSM_SYNC_COUNTER`, `HIVE_IF_FSM_DEINTERLEAVING_IDX`, `HIVE_IF_FSM_DECIMATION_H_COUNTER`, `HIVE_IF_FSM_DECIMATION_V_COUNTER`, `HIVE_IF_FSM_DECIMATION_BLOCK_V_COUNTER`, `HIVE_IF_FSM_PADDING_STATUS`, `HIVE_IF_FSM_PADDING_ELEMENT_COUNTER`, `HIVE_IF_FSM_VECTOR_SUPPORT_ERROR`. Important types include `input_formatter_switch_state_s`, `input_formatter_state_s`, `input_formatter_bin_state_s`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_private.h

## Purpose

`input_formatter_private.h` is the private include layer for the `input formatter` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `input_formatter_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__INPUT_FORMATTER_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_formatter_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_system.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/input_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq.c

## Purpose

`irq.c` programs IRQ controller masks, enables, edge/pulse behavior, clears, software IRQ raising, nested virtual IRQ mapping, and IRQ status collection..

## Important APIs, Types, And Data

Key includes: `assert_support.h`, `irq.h`, `gp_device.h`, `irq_private.h`. Important macros/constants include `__INLINE_GP_DEVICE__`. Important types include `return`. Important functions include `irq_wait_for_write_complete()`, `any_irq_channel_enabled()`, `irq_clear_all()`, `irq_enable_channel()`, `irq_enable_pulse()`, `irq_disable_channel()`, `irq_get_channel_id()`, `irq_raise()`, `any_virq_signal()`, `cnd_virq_enable_channel()`, `virq_clear_all()`, `virq_get_channel_signals()`.

## Control Flow

`irq_enable_channel()` reads mask/enable/edge registers, masks the target bit, programs rising-edge input behavior, enables output, clears stale status, unmasks the bit, and forces completion with a readback. `irq_disable_channel()` clears enable/mask bits and clears status. Virtual IRQ helpers map the flat `enum virq_id` space into nested IRQ controllers, enable or disable parent IRQ0 routes when nested controllers become active or empty, and collect or clear status from all enabled controllers.

## State And Persistence Behavior

Software state is limited to static mapping tables for channel counts, ID offsets, and nesting routes. Persistent state is held in IRQ controller mask, enable, edge, edge-not-pulse, clear/status registers and in GP-device software IRQ request registers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_local.h

## Purpose

`irq_local.h` is the local include layer for the `irq` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `irq_global.h`, `irq_controller_defs.h`, `hive_isp_css_defs.h`, `input_formatter_subsystem_defs.h`, `input_system_defs.h`, `input_selector_defs.h`. Important macros/constants include `__IRQ_LOCAL_H_INCLUDED__`, `HIVE_GP_DEV_IRQ_NUM_IRQS`, `HIVE_IFMT_IRQ_NUM_IRQS`, `IRQ_ID_OFFSET`, `IRQ0_ID_OFFSET`, `IRQ1_ID_OFFSET`, `IRQ2_ID_OFFSET`, `IRQ3_ID_OFFSET`, `IRQ_END_OFFSET`, `IRQ0_ID_N_CHANNEL`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_private.h

## Purpose

`irq_private.h` is the private include layer for the `irq` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `irq_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__IRQ_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/irq_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp.c

## Purpose

`isp.c` provides ISP control-memory access compilation support; active inline operations are supplied by the private header..

## Important APIs, Types, And Data

Key includes: `linux/delay.h`, `system_global.h`, `isp.h`, `isp_private.h`, `assert_support.h`. Important types include `return`. Important functions include `cnd_isp_irq_enable()`, `isp_is_ready()`, `isp_is_sleeping()`, `isp_start()`, `isp_wake()`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_local.h

## Purpose

`isp_local.h` is the local include layer for the `isp` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `isp_global.h`, `isp2400_support.h`. Important macros/constants include `__ISP_LOCAL_H_INCLUDED__`, `HIVE_ISP_VMEM_MASK`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_private.h

## Purpose

`isp_private.h` is the private include layer for the `isp` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `hrt/api.h`, `isp_public.h`, `device_access.h`, `assert_support.h`, `type_support.h`. Important macros/constants include `__ISP_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/isp_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu.c

## Purpose

`mmu.c` provides MMU compilation support for inline/private accessors used by the CSS MMU wrapper..

## Important APIs, Types, And Data

Key includes: `mmu_device.h`. Important functions include `mmu_set_page_table_base_index()`, `mmu_get_page_table_base_index()`, `mmu_invalidate_cache()`, `mmu_invalidate_cache_all()`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu_local.h

## Purpose

`mmu_local.h` is the local include layer for the `mmu` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `mmu_global.h`. Important macros/constants include `__MMU_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/mmu_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp.c

## Purpose

`sp.c` provides scalar-processor compilation support for private SP accessors..

## Important APIs, Types, And Data

Key includes: `sp.h`, `sp_private.h`, `assert_support.h`. Important functions include `cnd_sp_irq_enable()`.

## Control Flow

This compilation unit mainly selects the out-of-line version of helpers that are also available as private static inline functions. Runtime control is therefore the register or memory accessor flow defined by the corresponding public/private headers.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_local.h

## Purpose

`sp_local.h` is the local include layer for the `sp` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `sp_global.h`. Important macros/constants include `__SP_LOCAL_H_INCLUDED__`, `sp_address_of`, `store_sp_int`, `store_sp_ptr`, `load_sp_uint`, `load_sp_array_uint8`, `load_sp_array_uint16`, `load_sp_array_uint`, `store_sp_var`, `store_sp_array_uint8`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_private.h

## Purpose

`sp_private.h` is the private include layer for the `sp` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `sp_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__SP_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/sp_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl.c

## Purpose

`timed_ctrl.c` programs the timed-controller soft reset, enable bits, event state, condition state, IRQ masks, and selected input signals..

## Important APIs, Types, And Data

Key includes: `timed_ctrl.h`, `timed_ctrl_private.h`, `assert_support.h`. Important functions include `timed_ctrl_snd_commnd()`, `timed_ctrl_snd_sp_commnd()`, `timed_ctrl_snd_gpio_commnd()`.

## Control Flow

The functions are direct timed-controller register operations: reset, enable or disable event inputs, select signal sources, set condition state, and mask or unmask IRQ generation through the private register accessor.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_local.h

## Purpose

`timed_ctrl_local.h` is the local include layer for the `timed ctrl` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `timed_ctrl_global.h`. Important macros/constants include `__TIMED_CTRL_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_private.h

## Purpose

`timed_ctrl_private.h` is the private include layer for the `timed ctrl` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `timed_ctrl_public.h`, `device_access.h`, `assert_support.h`. Important macros/constants include `__TIMED_CTRL_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/timed_ctrl_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vamem_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vamem_local.h

## Purpose

`vamem_local.h` is the local include layer for the `vamem` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `vamem_global.h`. Important macros/constants include `__VAMEM_LOCAL_H_INCLUDED__`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vamem_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem.c

## Purpose

`vmem.c` loads and stores ISP VMEM/BAMEM vectors, including bit packing/unpacking between host words and ISP vector element widths..

## Important APIs, Types, And Data

Key includes: `isp.h`, `vmem.h`, `vmem_local.h`, `ia_css_device_access.h`, `assert_support.h`. Important macros/constants include `uedge_bits`, `move_lower_bits`, `move_upper_bits`, `move_word`. Important types include `unsigned`, `hive_uedge`. Important functions include `move_subword()`, `hive_sim_wide_unpack()`, `hive_sim_wide_pack()`, `load_vector()`, `store_vector()`, `isp_vmem_load()`, `isp_vmem_store()`, `isp_vmem_2d_load()`, `isp_vmem_2d_store()`.

## Control Flow

The low-level helpers move arbitrary bit ranges between 64-bit host words so vectors can be packed or unpacked according to `ISP_VEC_ELEMBITS`. Public load/store APIs assert vector alignment and widths, step through 1D or 2D VMEM rows in `ISP_NWAY` chunks, and use either `ia_css_device_load/store()` or HRT master-port access depending on `HRT_MEMORY_ACCESS`.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- The bit-moving helpers use shifts near word width boundaries; malformed element widths or non-vector-aligned pointers can corrupt adjacent vector data.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_local.h

## Purpose

`vmem_local.h` is the local include layer for the `vmem` host wrapper. In this snapshot it is intentionally small and mostly provides the include guard used by public/private wrapper headers.

## Important APIs, Types, And Data

Key includes: `type_support.h`, `vmem_global.h`. Important macros/constants include `__VMEM_LOCAL_H_INCLUDED__`, `VMEM_ARRAY`, `SVMEM_ARRAY`. Important types include `u16`, `s16`. Important functions include `isp_vmem_load()`, `isp_vmem_store()`, `isp_vmem_2d_load()`, `isp_vmem_2d_store()`.

## Control Flow

This local header has no runtime branch of its own. It participates in the include graph so the public facade can present a stable subsystem API while the build decides whether helper bodies are inline or out-of-line.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_private.h

## Purpose

`vmem_private.h` is the private include layer for the `vmem` host wrapper. It supplies static inline register or memory accessors when the subsystem is built inline, and is included by the matching `.c` file for out-of-line builds.

## Important APIs, Types, And Data

Key includes: `vmem_public.h`. Important macros/constants include `__VMEM_PRIVATE_H_INCLUDED__`.

## Control Flow

The private accessors are designed to be included either as `static inline` helpers or by the matching `.c` file. Callers typically validate an ID, derive a base address from platform arrays such as `*_BASE`, then load or store `hrt_data` through `ia_css_device_access`/HRT accessors.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/input_formatter_global.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/input_formatter_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/irq_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/irq_global.h

## Purpose

`irq_global.h` defines the shared `irq` contract for the AtomISP CSS common layer, covering IRQ controller version selection and virtual IRQ ID mapping entry point.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `irq_types_hrt.h`. Important macros/constants include `__IRQ_GLOBAL_H_INCLUDED__`, `IS_IRQ_VERSION_2`, `IS_IRQ_MAP_VERSION_2`, `IRQ_SW_CHANNEL_OFFSET`. Important types include `irq_sw_channel_id_t`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/irq_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/isp_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/isp_global.h

## Purpose

`isp_global.h` defines the shared `isp` contract for the AtomISP CSS common layer, covering ISP PMEM/vector widths, scalar-control register indexes, status bits, sink bits, and ISP2401 BAMEM aliases.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `mamoiada_params.h`. Important macros/constants include `__ISP_GLOBAL_H_INCLUDED__`, `ISP_PMEM_WIDTH_LOG2`, `ISP_PMEM_SIZE`, `ISP_NWAY_LOG2`, `ISP_VEC_NELEMS_LOG2`, `PIPEMEM`, `ISP_NWAY`, `ISP_VEC_BYTES`, `ISP_SC_REG`, `ISP_PC_REG`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/isp_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/mmu_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/mmu_global.h

## Purpose

`mmu_global.h` defines the shared `mmu` contract for the AtomISP CSS common layer, covering MMU interface marker for page/TLB constants supplied elsewhere.

## Important APIs, Types, And Data

Key includes: `mmu_defs.h`. Important macros/constants include `__MMU_GLOBAL_H_INCLUDED__`, `IS_MMU_VERSION_2`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/mmu_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/sp_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/sp_global.h

## Purpose

`sp_global.h` defines the shared `sp` contract for the AtomISP CSS common layer, covering scalar processor PMEM/DMEM sizes, control registers, status bits, icache controls, and sink bits.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `scalar_processor_2400_params.h`. Important macros/constants include `__SP_GLOBAL_H_INCLUDED__`, `SP_PMEM_WIDTH_LOG2`, `SP_PMEM_SIZE`, `SP_DMEM_SIZE`, `SP_PC_REG`, `SP_SC_REG`, `SP_START_ADDR_REG`, `SP_ICACHE_ADDR_REG`, `SP_IRQ_READY_REG`, `SP_IRQ_CLEAR_REG`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/sp_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/timed_ctrl_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/timed_ctrl_global.h

## Purpose

`timed_ctrl_global.h` defines the shared `timed ctrl` contract for the AtomISP CSS common layer, covering timed-controller signal selection and state types used for timed GPIO/CSS event routing.

## Important APIs, Types, And Data

Key includes: `timed_controller_defs.h`. Important macros/constants include `__TIMED_CTRL_GLOBAL_H_INCLUDED__`, `IS_TIMED_CTRL_VERSION_1`, `HIVE_TIMED_CTRL_GPIO_PIN_0_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_1_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_2_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_3_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_4_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_5_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_6_BIT_ID`, `HIVE_TIMED_CTRL_GPIO_PIN_7_BIT_ID`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/timed_ctrl_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vamem_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vamem_global.h

## Purpose

`vamem_global.h` defines the shared `vamem` contract for the AtomISP CSS common layer, covering VAMEM interface marker for ISP vector auxiliary memory access.

## Important APIs, Types, And Data

Key includes: `type_support.h`. Important macros/constants include `__VAMEM_GLOBAL_H_INCLUDED__`, `IS_VAMEM_VERSION_2`, `VAMEM_INTERP_STEP_LOG2`, `VAMEM_INTERP_STEP`, `VAMEM_TABLE_UNIT_SIZE`, `VAMEM_TABLE_UNIT_STEP`, `VAMEM_TABLE_UNIT_COUNT`. Important types include `u16`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vamem_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vmem_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vmem_global.h

## Purpose

`vmem_global.h` defines the shared `vmem` contract for the AtomISP CSS common layer, covering VMEM interface marker for ISP vector memory access.

## Important APIs, Types, And Data

Key includes: `isp.h`. Important macros/constants include `__VMEM_GLOBAL_H_INCLUDED__`, `VMEM_SIZE`, `VMEM_ELEMBITS`, `VMEM_ALIGN`. Important types include `tvector`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/vmem_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_defs.h

## Purpose

`hive_isp_css_defs.h` centralizes ISP2400 CSS fabric constants: bus widths, DDR/page geometry, DMA connections, GP register indexes, reset bits, IRQ/timed-controller signal ordering, GP timer signal IDs, streaming-monitor port IDs, and testbench registers.

## Important APIs, Types, And Data

Important macros/constants include `_hive_isp_css_defs_h__`, `HIVE_ISP_CTRL_DATA_WIDTH`, `HIVE_ISP_CTRL_ADDRESS_WIDTH`, `HIVE_ISP_CTRL_MAX_BURST_SIZE`, `HIVE_ISP_DDR_ADDRESS_WIDTH`, `HIVE_ISP_HOST_MAX_BURST_SIZE`, `HIVE_ISP_NUM_GPIO_PINS`, `HIVE_ISP_DDR_DMA_SPECS`, `HIVE_ISP_DDR_WORD_BITS`, `HIVE_ISP_DDR_WORD_BYTES`.

## Control Flow

There is no executable control flow in this definition header. Consumers use the constants to compute register addresses, pack command fields, decode status fields, and keep host-side programming in sync with the hardware RTL layout.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

The header is consumed by the corresponding global/private wrappers and by input-system or device-specific programming code. It must match adjacent generated RTL definition headers and platform base-address arrays; otherwise register-index math and command packing drift away from hardware.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/assert_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/assert_support.h

## Purpose

`assert_support.h` provides low-level CSS support macros used throughout the AtomISP CSS host code.

## Important APIs, Types, And Data

Key includes: `linux/bug.h`. Important macros/constants include `__ASSERT_SUPPORT_H_INCLUDED__`, `CT_ASSERT`, `assert`, `OP___assert`. Important functions include `compile_time_assert()`.

## Control Flow

The file is macro-only support code. Control flow appears at expansion sites in callers, so tests need to exercise both valid and invalid macro inputs in the surrounding CSS host code.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/assert_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/bitop_support.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/bitop_support.h

## Purpose

`bitop_support.h` provides low-level CSS support macros used throughout the AtomISP CSS host code.

## Important APIs, Types, And Data

Important macros/constants include `__BITOP_SUPPORT_H_INCLUDED__`, `bitop_setbit`, `bitop_getbit`, `bitop_clearbit`.

## Control Flow

The file is macro-only support code. Control flow appears at expansion sites in callers, so tests need to exercise both valid and invalid macro inputs in the surrounding CSS host code.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/bitop_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/csi_rx.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/csi_rx.h

## Purpose

`csi_rx.h` is the public facade include for the `csi rx.h` API, selecting local/public/private headers depending on inline build macros.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `csi_rx_local.h`, `csi_rx_public.h`, `csi_rx_private.h`. Important macros/constants include `__CSI_RX_H_INCLUDED__`.

## Control Flow

The facade branches at preprocessing time. Without the subsystem inline macro it declares extern/public functions; with the inline macro it includes private static inline bodies. Runtime behavior is delegated to the selected public/private implementation.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/csi_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/debug.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/debug.h

## Purpose

`debug.h` is the public facade include for the `debug.h` API, selecting local/public/private headers depending on inline build macros.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `debug_local.h`, `debug_public.h`, `debug_private.h`. Important macros/constants include `__DEBUG_H_INCLUDED__`, `STORAGE_CLASS_DEBUG_H`, `STORAGE_CLASS_DEBUG_C`.

## Control Flow

The facade branches at preprocessing time. Without the subsystem inline macro it declares extern/public functions; with the inline macro it includes private static inline bodies. Runtime behavior is delegated to the selected public/private implementation.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/debug.h -->
