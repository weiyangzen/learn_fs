# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/nwl-dsi.h

## Purpose

This header defines the register offsets and bitfield helpers for the Northwest Logic MIPI DSI host used by `nwl-dsi.c`. It is the hardware contract for host configuration, DPI video timing, packet TX/RX, interrupt status/masks, packet-control fields, RX header decoding, video mode selection, and pixel-format encoding.

## Important APIs, Types, And Macros

Register groups include `NWL_DSI_CFG_*` host timing/control registers, DPI registers such as `NWL_DSI_PIXEL_PAYLOAD_SIZE`, `NWL_DSI_INTERFACE_COLOR_CODING`, `NWL_DSI_PIXEL_FORMAT`, sync polarity, video mode, porch/sync sizes, BLLP/null-packet controls, and virtual channel. Packet registers include `NWL_DSI_TX_PAYLOAD`, `NWL_DSI_PKT_CONTROL`, `NWL_DSI_SEND_PACKET`, FIFO levels, `NWL_DSI_RX_PAYLOAD`, and `NWL_DSI_RX_PKT_HEADER`.

IRQ definitions cover status/mask bits for TX completion, DPHY direction, FIFO overflow/underflow, RX header/payload, BTA/LP/HS timeouts, and ECC/CRC errors. `NWL_DSI_WC()`, `NWL_DSI_TX_VC()`, `NWL_DSI_TX_DT()`, `NWL_DSI_HS_SEL()`, `NWL_DSI_BTA_TX()`, and `NWL_DSI_BTA_NO_TX()` compose packet-control fields. `NWL_DSI_RX_DT()` and `NWL_DSI_RX_VC()` decode RX headers.

## Control Flow

The header has no runtime flow. `nwl-dsi.c` uses these constants to program host timing from DPHY settings, DPI timing from DRM modes, send/receive MIPI DSI packets, mask interrupts, and decode IRQ/RX status.

## State And Persistence

No software state is stored here. The named registers represent hardware state that persists while the DSI block remains powered and out of reset.

## Dependencies And Integration Points

The header relies on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`, `FIELD_GET`) from including translation units. It is tightly coupled to `nwl-dsi.c` and the MMIO regmap stride/max register setup.

## Risks And Edge Cases

Incorrect offsets or field masks break low-level hardware programming with little compile-time visibility. Packet-control field helpers assume input values fit their field widths. IRQ bits include error classes not all handled by the current driver. The comment typo around DPI color coding is harmless but indicates generated/manual mixed content.

## Test Signals

Validation is indirect through `nwl-dsi.c`: register writes in trace/debug, packet TX/RX, interrupt masking, video mode programming, pixel format mapping, and static review against the NWL hardware manual.
