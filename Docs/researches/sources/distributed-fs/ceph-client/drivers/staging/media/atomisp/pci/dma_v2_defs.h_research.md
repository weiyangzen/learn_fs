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
