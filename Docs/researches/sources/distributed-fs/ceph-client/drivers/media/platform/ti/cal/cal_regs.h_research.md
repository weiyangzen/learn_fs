<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h

## Purpose

This header defines CAL and CSI2/CAMERARX register offsets, bit masks, enum values, interrupt masks, and the DRA72 pre-ES2 LDO erratum flag used by the CAL implementation.

## Important APIs, types, and functions

- `DRA72_CAL_PRE_ES2_LDO_DISABLE` documents and flags erratum i913 handling for affected DRA72 devices.
- Register offset macros cover high-level CAL control/IRQ registers, pixel processors, read/write DMA, CSI2 PPI/ComplexIO/VC/context/status, CSI2 PHY registers, and control-module CAMERARX control.
- Bit masks and field values cover revision decoding, HWINFO, IRQ status/enable, pixel extraction/packing, global control, DMA geometry/mode, CSI2 lane/PHY status, CSI2 virtual-channel IRQs, context DT/VC/CPORT/line fields, and CAMERARX control bits.

## Control flow

There is no direct control flow. The implementation composes these macros with `cal_set_field()` and `cal_write_field()` to program CAL context registers in `cal_ctx_*` functions, decode hardware revision in `cal_get_hwinfo()`, enable/clear interrupts in IRQ paths, and apply CAMERARX PHY errata.

## State and persistence behavior

The header itself has no state. It describes volatile MMIO state held by the hardware. Register writes affect active capture configuration and are reset by hardware/module lifecycle rather than persisted by software.

## Dependencies and integration points

It depends on Linux `BIT()`/`GENMASK()` definitions through including code. It is included by `cal.c` and must remain synchronized with the TI CAL hardware reference and the register helper functions in `cal.h`.

## Risks and edge cases

Incorrect bit masks or field constants can silently program wrong DMA sizes, data types, pixel packing, or interrupt enables. Several width/height fields are bounded by register width, which is why `cal-video.c` clamps formats. The erratum comment is operationally important: skipping LDO disable on affected silicon can cause high current draw.

## Test signals

Signals include successful probe revision/HWINFO reads, valid register dumps with `debug >= 4`, correct frame sizes/strides across 8/10/12/16 bpp formats, interrupt delivery for WDMA start/end, and hardware tests on affected DRA72 silicon for erratum handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal_regs.h -->
