
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/meson-ge2d/ge2d-regs.h

## Purpose

`ge2d-regs.h` defines the MMIO register offsets, bitfields, hardware color format maps, ALU blend/logic constants, and field-prep helper macros used by the Meson GE2D V4L2 mem2mem driver.

## Important APIs, Types, And Functions

The header's central offset macro is `GE2D_REG(x)`, which maps logical GE2D register indices to byte offsets starting at hardware base index `0x8a0 * 4`. It defines control/status registers such as `GE2D_GEN_CTRL0..4`, `GE2D_CMD_CTRL`, `GE2D_STATUS0..2`, source/destination clip/window/canvas/base/stride registers, scale coefficient registers, matrix registers, and ALU registers.

Color format constants include `GE2D_FORMAT_8BIT/16BIT/24BIT/32BIT` and many `GE2D_COLOR_MAP_*` values for RGB/YUV layouts. ALU helpers `GE2D_ALU_COLOR_OP()`, `GE2D_ALU_DO_COLOR_OPERATION_LOGIC()`, `GE2D_ALU_ALPHA_OP()`, and `GE2D_ALU_DO_ALPHA_OPERATION_LOGIC()` combine operation and factor fields using `FIELD_PREP()`.

## Control Flow

There is no executable flow. `ge2d.c` consumes these constants when resetting hardware, programming source/destination base and stride, configuring source/destination pixel formats, writing clipping and window bounds, selecting ALU copy/alpha behavior, and issuing `GE2D_CBUS_CMD_WR`.

## State And Persistence

The file contains no variables. It describes volatile hardware state fields. Correctness depends on matching GE2D silicon documentation and the regmap configuration in `ge2d.c`.

## Dependencies And Integration Points

The header depends on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`) supplied through including C files. It is tightly integrated with the `struct ge2d_fmt` table in `ge2d.c`, where V4L2 formats map to `GE2D_FORMAT_*` and `GE2D_COLOR_MAP_*` constants.

## Risks

`GE2D_REG(x)` bakes in a base offset; using the header with a differently based MMIO region would program the wrong addresses. Many color-map constants alias between RGB and YUV names, so format-table mistakes can silently reinterpret channels. The ALU factor constants distinguish color and alpha spaces but share some numeric values; wrong helper use can generate invalid blending behavior.

## Test Signals

Build tests should ensure all `FIELD_PREP()` masks are valid for their constants. Runtime register tracing during a simple blit should show `GEN_CTRL2`, clip/window registers, `ALU_OP_CTRL`, and `CMD_CTRL` values matching the selected V4L2 formats and transform controls. Format tests should verify every `ge2d.c` format maps to a defined hardware format/map pair.
