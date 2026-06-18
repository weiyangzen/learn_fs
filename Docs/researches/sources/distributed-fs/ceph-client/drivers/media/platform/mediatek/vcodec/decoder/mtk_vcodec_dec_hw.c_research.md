# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_hw.c

## Purpose
This file implements child hardware platform drivers for decoder LAT/core subdevices used by newer MediaTek decoder architectures.

## Important APIs, Types, And Functions
`mtk_vdec_hw_match` maps compatible strings to hardware IDs for LAT0, CORE, and LAT_SOC. `mtk_vdec_hw_probe()` obtains the parent decoder device, initializes clocks/runtime PM, records subdevice state in the parent bitmap, maps the subdevice MISC registers, and optionally installs an IRQ. `mtk_vdec_hw_prob_done()` verifies all present compatible subdevices have probed. `mtk_vdec_hw_irq_handler()` checks active status, validates decode-success IRQ status, clears the interrupt, and wakes the current context for that hardware index.

## Control Flow
The parent decoder probe populates child platform devices. Each child probe attaches itself to the parent. Open checks `subdev_prob_done()` before allowing contexts. During decode, PM code enables the selected child hardware and IRQ; IRQ completion wakes the waiting context.

## State, Persistence, And Dependencies
State lives in `struct mtk_vdec_hw_dev`: platform device, parent pointer, register bases, current context, IRQ, PM, and hardware index. Dependencies include OF platform, PM runtime, decoder PM, common interrupt helpers, and current-context utility functions.

## Integration Points
Parent driver stores subdevice pointers and bitmap. PM uses subdevice PM/IRQ data. Codec workers use hardware indexes that correspond to these subdevices.

## Risks
IRQ handler calls logging macros with `ctx` from current-context lookup; if no current context is set, null handling is fragile. Subdevice readiness scans global compatible nodes, so multiple decoder instances in a system could complicate readiness. LAT_SOC intentionally has no IRQ.

## Test Signals
Device-tree child population, all subdevice combinations, IRQ success/ignored-status paths, PM runtime enablement, and open before all subdevices probe.
