# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.c

## Purpose
Implements the Synopsys DesignWare HDMI receiver capture driver for Rockchip RK3588-style integrations. It exposes a V4L2 video capture node backed by vb2 contiguous DMA, controls HDMI RX PHY/controller/packet/DMA blocks, manages HPD and EDID, reports DV timings and input status, surfaces AVI infoframes through debugfs, and registers a CEC adapter through the companion CEC file.

## Important APIs, Types, And Functions
Primary state is `struct snps_hdmirx_dev`, which owns the V4L2 device, controls, timings, GPIO, delayed work, CEC handle, regmaps, completions, IRQ numbers, EDID cache, current pixel format/depth, locks, clocks, resets, and MMIO base. `struct hdmirx_stream` owns the video node, vb2 queue, current/next buffers, format, queue locks, stopping state, sequence, and DMA interrupt counters. `struct hdmirx_buffer` wraps `vb2_v4l2_buffer` plus DMA plane addresses.

Key user APIs are the V4L2 ioctl table: querycap, input enumeration, EDID get/set, DV timing query/get/set/caps/enumeration, stream parameters, format enum/get/set, vb2 buffer ioctls, event subscription, and control logging. Important internals include `hdmirx_phy_config()`, `hdmirx_controller_init()`, `hdmirx_dma_config()`, `hdmirx_wait_signal_lock()`, `hdmirx_start_streaming()`, `hdmirx_stop_streaming()`, `hdmirx_hdmi_irq_handler()`, and `hdmirx_dma_irq_handler()`.

## Control Flow
Probe sets a 32-bit DMA mask, parses clocks/resets/GPIO/syscon/reserved memory, requests HDMI/DMA/5V IRQs with `IRQ_NOAUTOEN`, maps MMIO, initializes locks/completions/work items, enables clocks/resets, validates interrupt functionality through a PHY register read, disables stale interrupts, registers the V4L2 device and video node, registers CEC, optionally loads default EDID, enables IRQs, and creates debugfs infoframe support.

Hotplug starts at the 5V GPIO IRQ, which schedules `hdmirx_delayed_work_hotplug()`. That work samples 5V, updates `V4L2_CID_DV_RX_POWER_PRESENT`, tears down prior plug state, and if present initializes submodules, asserts `POWERPROVIDED`, configures PHY, and enables HDMI interrupts. Signal-change IRQs schedule `hdmirx_delayed_work_res_change()`, which reinitializes controller/PHY, waits for lock and AVI packet reception, updates pixel format/color depth/AVI controls, configures DMA, and re-enables interrupts.

Streaming uses vb2. Queued buffers store physical addresses for Y and chroma planes. `start_streaming` picks the first buffer, writes DMA address registers, configures line-flag position and DMA interrupt masks, clears status, and enables DMA. The DMA IRQ uses line-flag interrupts to program the next buffer and idle interrupts to complete the previous buffer, skipping early frames with `FILTER_FRAME_CNT` and handling interlaced field cadence. Stop sets `stopping`, waits for the IRQ to acknowledge, disables DMA, and returns all buffers.

## State And Persistence
Persistent runtime state includes EDID bytes and block count, current DV timings, current fourcc, HDMI pixel format/color depth, 5V plug state, tmds clock ratio, V4L2 controls, vb2 queue contents, current/next buffers, and debugfs infoframe object. Suspend disables IRQs, CEC IRQ, HPD, plug state, clocks, and pinctrl state; resume restores clocks/resets, rewrites cached EDID, restores HPD, reenables CEC/IRQs, and schedules hotplug work. No filesystem persistence exists.

## Dependencies And Integration Points
Integrates with platform resources named `hdmi`, `dma`, `cec`, and HPD GPIO; Rockchip `grf` and `vo1-grf` syscon regmaps; clocks and resets; optional reserved memory/CMA; V4L2 controls/events/ioctls; videobuf2 DMA-contig; HDMI infoframe helpers; CEC core via `snps_hdmirx_cec_register()`; debugfs infoframe helpers; pinctrl PM; and RK3588 device tree compatible `rockchip,rk3588-hdmirx-ctrler`.

## Risks
The driver is strongly tied to RK3588 register layout and firmware behavior; it explicitly detects a broken downstream TF-A interrupt remap and requires open-source TF-A behavior. Many operations depend on hardware timing, completions, and delayed work, so plug/unplug races are controlled mostly by `work_lock` and IRQ disable ordering. EDID writes temporarily force HPD low and must not race with plug work. DMA buffer handoff is interrupt-driven and sensitive to missing line-flag/idle interrupts. The DMA path assumes 32-bit physical addresses. Suspend notes TODOs for CEC state save/restore. The built-in default EDID is limited to lower compatibility modes and is not production identity.

## Test Signals
Use `v4l2-compliance`, `v4l2-ctl --query-dv-timings`, EDID get/set, event subscription for source changes, hotplug plug/unplug testing, CEC adapter discovery and transmit/receive tests, DMA streaming with mmap and dmabuf, interlaced/progressive modes, RGB/YUV formats, high TMDS clock ratio transitions, suspend/resume with EDID retained, and debugfs AVI infoframe reads. Kernel logs around lock waits, PHY register completions, DMA underrun/overflow, and interrupt-not-handled messages are key bring-up signals.
