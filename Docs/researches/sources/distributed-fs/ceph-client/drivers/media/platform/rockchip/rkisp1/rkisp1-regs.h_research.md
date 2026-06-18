# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-regs.h

## Purpose

`rkisp1-regs.h` is the register and bitfield contract for the RKISP1 driver. It defines ISP control bits, interrupt masks, memory-interface format fields, resizer and dual-crop control bits, MIPI/SMIA status fields, ISP statistics layout, image-processing block masks, and the absolute register offsets used by the C source files. It contains no executable code, but every register read/write in the RKISP1 driver depends on these definitions being accurate for the supported ISP variants.

## Important APIs, Types, And Macros

The header exports macros only. The first half defines field values and masks, including `RKISP1_CIF_ISP_CTRL_*`, acquisition property values, `RKISP1_CIF_ISP_*` interrupt bits, MI control format bits and masks, `RKISP1_CIF_RSZ_CTRL_*`, clock/reset bits, dual-crop modes, MIPI error masks, histogram packing helpers, AWB/AEC extraction and packing helpers, LSC table packing helpers, DPCC masks, BLS modes, AFM window packing, DPF flags, compand control bits, and WDR masks.

The second half defines the address map. Major bases include control (`0x00000000`), image effects (`0x00000200`), ISP core (`0x00000400`), color processing (`0x00000800`), dual crop (`0x00000880`), main/self resizers (`0x00000c00` and `0x00001000`), memory interface (`0x00001400`), SMIA (`0x00001a00`), MIPI (`0x00001c00`), AFM (`0x00002000`), LSC (`0x00002200`), image stabilization (`0x00002300`), v10 histogram (`0x00002400`), filter/CAC/AEC/BLS/DPF/DPCC/WDR (`0x00002500` through `0x00002a00`), v12 histogram (`0x00002c00`), VSM (`0x00002f00`), compand (`0x00003200`), and CSI0 (`0x00007000`).

## Control Flow

There is no runtime control flow in the header. Its definitions are consumed by control flow in the params, stats, resizer, capture, ISP, and CSI/MIPI portions of the driver. A common pattern is: a C file computes a register value with these masks, writes it with `rkisp1_write()`, and triggers a shadow update bit such as `RKISP1_CIF_ISP_CTRL_ISP_CFG_UPD`, `RKISP1_CIF_RSZ_CTRL_CFG_UPD`, or `RKISP1_CIF_DUAL_CROP_CFG_UPD`.

The header encodes variant-specific control flow indirectly. v10 and v12 use different histogram and AEC layouts, different LSC table element widths, different gamma output packing, and different AWB register aliases. Source files select the right macro families by checking the ISP version and dispatching through ops tables.

## State And Persistence

The header itself has no state. It describes persistent hardware register state: enable bits, shadow registers, interrupt status/clear registers, DMA address registers, format registers, measurement accumulators, and table memories. Several definitions refer to shadow registers (`*_SHD`) or update bits, reflecting that hardware state is double-buffered and only applied at defined synchronization points.

## Dependencies And Integration Points

The macros rely on kernel bit helpers such as `BIT()` and `GENMASK()` being available through includers. Integration is broad: `rkisp1-params.c` uses ISP processing block registers, `rkisp1-stats.c` reads measurement output registers, `rkisp1-resizer.c` uses RSZ and dual-crop offsets, capture code uses MI registers, and ISP/MIPI code uses interrupt and input-format definitions. Because this header is included through `rkisp1-common.h`, changes can affect most of the RKISP1 driver.

## Risks

The main risk is silent hardware misprogramming. Wrong masks, shifts, or offsets compile cleanly but can corrupt image data, break DMA, lose interrupts, or report invalid statistics. Overlapping v10/v12 aliases are especially sensitive because the same numeric offsets can mean different layouts. Macros that pack multiple samples per register must match the hardware bit width exactly. Register update bits are also easy to misuse; failing to assert the correct synchronous or asynchronous update bit can leave software state diverged from active hardware state.

## Test Signals

Good signals include compile coverage across RKISP1 users, sparse/build warnings for macro use, camera streaming smoke tests, media graph format negotiation, frame capture validation for raw and YUV formats, v10/v12 statistics sanity checks, interrupt error-counter monitoring, and register traces around params/resizer reconfiguration. Hardware bring-up should compare written offsets and bitfields against the datasheet for each supported ISP revision.
