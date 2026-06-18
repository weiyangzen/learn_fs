# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.c

Purpose: implements the platform-driver, resource management, runtime PM, interrupt dispatch, and optional ISP/V4L2 media-device ownership for the sun6i CSI block.

Important APIs and functions: exported integration hook is `sun6i_csi_isp_complete`. Main local functions include `sun6i_csi_probe`, `sun6i_csi_remove`, `sun6i_csi_resources_setup`, `sun6i_csi_v4l2_setup`, `sun6i_csi_interrupt`, `sun6i_csi_resume`, and `sun6i_csi_suspend`. Variant data sets module clock rate per compatible.

Control flow: probe allocates `struct sun6i_csi_device`, maps registers through regmap, acquires module/RAM clocks and shared reset, sets an exclusive module-clock rate, requests a shared IRQ, enables runtime PM, detects an optional ISP graph endpoint, registers its own media/V4L2 devices if no ISP is present, sets up the bridge subdevice, and sets up capture immediately or later through ISP completion. The IRQ reads channel status and enables, ignores unrelated or disabled status, resets CSI on FIFO/HB overflow, dispatches frame-done to sequence update, dispatches VS to buffer sync, then clears status.

State and persistence: `struct sun6i_csi_device` stores device resources, regmap, clocks, reset, V4L2/media ownership, bridge state, capture state, and `isp_available`. Hardware state is volatile and rebuilt when the bridge starts streaming. The exclusive clock-rate reservation persists between resources setup and cleanup.

Dependencies and integration points: depends on regmap MMIO with bus clock, runtime PM, media/V4L2 core, V4L2 async bridge/capture setup, and device tree compatibles for A31, A83T, H3, V3s, and A64. Optional ISP integration reuses the remote subdevice's V4L2/media devices and registers capture after async binding.

Risks: IRQ overflow recovery toggles the CSI enable bit and can drop frames. Shared IRQ handling must return `IRQ_NONE` only for truly unrelated status. ISP detection is graph-based and warns if the kernel lacks `CONFIG_VIDEO_SUN6I_ISP`, but then proceeds without ISP support. Cleanup calls capture cleanup even when capture setup never completed, relying on setup guards.

Test signals: probe/remove for each compatible clock rate, runtime PM resume/suspend, shared IRQ behavior, FIFO overflow recovery, no-ISP standalone media graph, ISP-connected graph completion, and streaming with frame/VS interrupts.
