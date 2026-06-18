# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.h

## Purpose
This header defines Atmel ISI v2 register offsets, bit masks, DMA control bits, status bits, data-width flags, and `struct isi_platform_data` used by `atmel-isi.c`.

## Important APIs, Types, and Functions
Important definitions include `ISI_CFG1`, `ISI_CFG2`, `ISI_PSIZE`, `ISI_CTRL`, `ISI_STATUS`, interrupt registers, DMA descriptor registers for preview and codec paths, polarity bits, frame-rate divisors, grayscale/YCC swap controls, reset/disable bits, transfer-done flags, overflow/error flags, and `ISI_DMA_CTRL_*`. `struct isi_platform_data` carries embedded-sync, polarity, full-mode, data-width, and frame-rate configuration.

## Control Flow
The header has no executable control flow. The C driver uses these constants to program bus configuration, image dimensions, preview size, DMA descriptor fetch/writeback, interrupt enables/disables, reset, disable, and status polling.

## State and Persistence
No state is stored in the header. It defines the names and bit encodings used for volatile hardware state.

## Dependencies and Integration Points
It includes only `linux/types.h` and is tightly coupled to the Atmel ISI hardware register map and the driver logic in `atmel-isi.c`.

## Risks and Edge Cases
Incorrect bit definitions can silently corrupt capture setup, DMA routing, interrupt handling, or bus polarity. Width/height masks encode limited field sizes, so driver validation must stay within hardware limits.

## Test Signals
Compile the Atmel ISI driver and validate register programming on hardware or register traces for reset, disable, bus polarity, frame dimensions, and both DMA paths.
