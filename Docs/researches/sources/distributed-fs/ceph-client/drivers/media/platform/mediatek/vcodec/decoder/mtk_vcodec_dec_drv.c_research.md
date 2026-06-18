# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.c

## Purpose
This file is the parent MediaTek V4L2 decoder platform driver. It probes the decoder device, maps resources, selects firmware, creates V4L2/media/mem2mem devices, handles opens/releases, manages context lists, and services single-core interrupts.

## Important APIs, Types, And Functions
`mtk_vcodec_probe()` is the main device setup path. `mtk_vcodec_get_reg_bases()` supports both legacy named register mapping plus syscon VDEC_SYS and newer indexed mapping. `mtk_vcodec_init_dec_resources()` maps registers, installs IRQs for non-subdevice platforms, initializes clocks, and enables runtime PM. `fops_vcodec_open()` allocates per-instance contexts, checks subdevice readiness, creates controls and mem2mem queues, loads firmware on the first open, queries capabilities, initializes pdata-specific parameters, links debugfs, and adds the context to the list. `fops_vcodec_release()` tears the context down. `mtk_vcodec_dec_irq_handler()` wakes the current core context.

## Control Flow
Probe allocates device state, identifies chip and firmware backend from device tree, maps resources, creates optional LAT/core workqueues, initializes locks, registers V4L2 and video devices, creates mem2mem and decode workqueues, populates subdevices when supported, registers media controller for stateless APIs, and initializes debugfs. Open prepares per-instance state and firmware. Remove reverses registration and releases firmware.

## State, Persistence, And Dependencies
Device state includes register bases, firmware handler, context list, current context, locks, workqueues, IRQs, PM state, capability bits, subdevice bitmap, racing-info snapshot, media device, and debugfs. No persistence. Dependencies include OF, syscon/regmap, runtime PM, V4L2/mem2mem/media controller, firmware abstraction, and decoder PM/hardware helpers.

## Integration Points
OF match selects pdata from stateful/stateless files. Hardware subdevices attach through child platform population. Common firmware and util modules provide backend and current-context helpers.

## Risks
Probe error paths are long and architecture-dependent. Firmware loading only on singular first open means capability-dependent format tables initialize lazily. Subdevice readiness must be complete before opening. IRQ handler assumes a valid current context. Media controller cleanup is conditional on registration state.

## Test Signals
Probe/remove on all compatibles, legacy and syscon register layouts, VPU/SCP firmware paths, first and concurrent opens, subdevice population failures, interrupt completion, and stateless media controller registration.
