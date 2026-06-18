# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_sai.h

## Purpose
Defines the Rockchip SAI register map, bit fields, helper macros, version constants, path-selection encodings, FIFO/status fields, and frame-sync timeout controls used by `rockchip_sai.c`.

## Important APIs, Types, And Functions
This header exposes macros rather than functions. Important groups include `SAI_XCR_*` for TX/RX control fields, `SAI_FSCR_*` for frame sync width and pulse width, `SAI_XFER_*` for clock/frame/stream start and idle bits, `SAI_CKR_*` for master/slave and clock polarity, `SAI_DMACR_*` for DMA enable/thresholds, `SAI_INTCR_*`/`SAI_INTSR_*` for interrupt control/status, `SAI_RX_PATH()` and `SAI_TX_PATH()` for lane routing, version constants `SAI_VER_2307` through `SAI_VER_2403`, and register offsets through `SAI_LOOPBACK_LR`.

## Control Flow
There is no runtime control flow. The macros encode register programming contracts consumed by the driver when translating ASoC formats, PCM parameters, runtime PM, path routing, IRQ handling, and mixer controls into hardware writes.

## State And Persistence
No state is stored in the header. The macros describe hardware state persisted in MMIO registers and cached by the driver's regmap.

## Dependencies And Integration Points
Requires kernel bit helpers such as `BIT()` and `GENMASK()` from including source context. It is tightly coupled to `rockchip_sai.c` and the RK3576 SAI register layout. Version comments document feature gates such as FSXN, FSE, FSLOST, forced clear, chained SAI, TX auto gate, and loopback LR selection.

## Risks And Edge Cases
- Several macros subtract one from user values; callers must avoid zero for fields like slot width or frame width unless explicitly allowed.
- `SAI_CLR_FCR` has a `TODO` comment, so forced-clear semantics are not fully documented in the code.
- Register bit meanings change around `SAI_VER_2307` and `SAI_VER_2311`; driver code must keep version checks aligned with this header.
- Path macros assume lane indexes in range and do not validate values.

## Test Signals
Compile coverage is the main signal. Runtime tests should confirm that macro-derived register values match hardware documentation for I2S, DSP, TDM, lane route, and interrupt scenarios.
