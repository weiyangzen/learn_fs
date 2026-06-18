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
