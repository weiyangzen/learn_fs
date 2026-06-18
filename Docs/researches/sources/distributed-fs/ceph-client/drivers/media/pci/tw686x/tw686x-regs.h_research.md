# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-regs.h

## Purpose
`tw686x-regs.h` is the register map and bit-definition header for the TW686x driver. It translates the chip's DMA controller and video decoder register layout into symbolic offsets used by `tw686x-core.c`, `tw686x-video.c`, and the audio driver. It also provides per-channel register-array macros for devices with up to eight channels.

## Important APIs, Types, And Functions
There are no functions or types, only macros. `REG8_1`, `REG8_2`, and `REG8_8` build constant eight-element register arrays for contiguous, two-step, and eight-step channel register blocks. `VDREG8` and `VDREG2` build video-decoder register arrays. Named register offsets include `INT_STATUS`, `PB_STATUS`, `DMA_CMD`, `VIDEO_FIFO_STATUS`, `DMA_CHANNEL_ENABLE`, `DMA_TIMER_INTERVAL`, `VDMA_CHANNEL_CONFIG`, `VDMA_P_ADDR`, `VDMA_B_ADDR`, `DMA_PAGE_TABLE0_ADDR`, `DMA_PAGE_TABLE1_ADDR`, `SDT`, `SDT_EN`, and per-channel scaler/crop/status registers. Important bit and mode macros include `DMA_CMD_ENABLE`, `INT_STATUS_DMA_TOUT`, `TW686X_VIDSTAT_HLOCK`, `TW686X_VIDSTAT_VDLOSS`, standard IDs, `TW686X_FIELD_MODE`, `TW686X_FRAME_MODE`, `TW686X_SG_MODE`, and `TW686X_FIFO_ERROR()`.

## Control Flow
This header does not execute. Its definitions drive all MMIO control flow: the core IRQ path reads `INT_STATUS`, `PB_STATUS`, and `VIDEO_FIFO_STATUS`; video setup writes `VDMA_CHANNEL_CONFIG`, `VDMA_WHP`, `PHASE_REF`, `SDT`, `VIDEO_FIELD_CTRL`, and control registers; DMA mode setup writes either direct frame-buffer addresses or SG page-table addresses. The array macros allow the same video code to index channel-specific offsets by `vc->ch`.

## State And Persistence
No runtime state is stored here. The header is a compile-time contract between C code and hardware. Mistakes in constants persist as wrong hardware programming until rebuilt, which is riskier than ordinary software state because register writes can corrupt DMA or freeze affected systems.

## Dependencies And Integration Points
The header assumes Linux bit helpers such as `BIT()` and size macros like `SZ_512`/`SZ_4K` are available through including translation units. It is included by `tw686x.h`, which then makes register helpers visible to the rest of the TW686x module. It is tightly coupled to chip datasheet semantics and to the `struct tw686x_dev` MMIO pointer arithmetic in `reg_read()`/`reg_write()`.

## Risks
Register arrays are compound literals, so callers should use them as immediate constants and not persist pointers beyond expression lifetimes. The `TW686X_FIFO_ERROR(x)` macro treats any non-low-byte bits as FIFO error state; code using it must preserve the device-specific encoding. Header comments and core comments indicate DMA programming mistakes can trigger severe hardware failure modes.

## Test Signals
Validation is indirect: correct standards detection, frame sizes, DMA modes, frame parity, FIFO reset behavior, audio DMA period sizing, and video controls all demonstrate that register offsets and bit masks match the hardware. Compile coverage also catches missing macro dependencies, but not semantic register mistakes.
