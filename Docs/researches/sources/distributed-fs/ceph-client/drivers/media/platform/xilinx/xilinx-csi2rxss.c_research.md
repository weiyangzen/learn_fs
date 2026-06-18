# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-csi2rxss.c

Purpose: V4L2 subdevice driver for the Xilinx MIPI CSI-2 Rx Subsystem. It accepts a CSI-2 sensor stream on a sink pad, converts it to AXI4-Stream on a source pad, manages reset/clock/interrupt resources, validates device-tree data type/lane configuration, and exposes status logging.

Important types and APIs: `struct xcsi2rxss_state` stores subdev, active/default formats, interrupt counters, remote subdev, reset GPIO, bulk clocks, MMIO base, max lanes, configured CSI-2 data type, mutex, pads, and streaming flags. Key routines include register helpers, `xcsi2rxss_soft_reset/hard_reset`, `xcsi2rxss_irq_handler`, `xcsi2rxss_s_stream`, format get/set/enumeration, `xcsi2rxss_log_status`, `xcsi2rxss_parse_of`, `probe`, and `remove`.

Control flow: probe validates OF properties such as `xlnx,csi-pxl-format`, `xlnx,vfb`, `xlnx,en-csi-v2-0`, `xlnx,en-vcx`, active lanes, and both graph endpoints; maps registers; requests an IRQ; gets and enables `lite_aclk` and `video_aclk`; resets the core; initializes two media pads and the default format; then registers the subdevice. Stream-on enables the core, soft-resets, enables interrupt masks, marks streaming, finds the remote sensor subdev, and starts it. Stream-off calls remote `s_stream(0)`, disables IRQs/core, clears streaming, and hard-resets through GPIO.

State and persistence: active format is stored in `state->format`; TRY formats live in subdev state. Event counters accumulate IRQ events until reset at stream-on and are printed by `log_status`. Hardware state lives in CSI-2 registers and is not persisted across driver unload.

Dependencies and integration: uses V4L2 fwnode CSI-2 endpoint parsing, MIPI CSI-2 data type constants, media entity link validation, GPIO reset, bulk clocks, platform MMIO/IRQ, and Xilinx VIP pad IDs. It registers for compatible `xlnx,mipi-csi2-rx-subsystem-5.0`.

Risks: `rsubdev` can be NULL if no remote subdev is linked when streaming starts, yet the stream path calls it. Lane/data-type properties are strict, and operation without video frame buffer is rejected. Stream-line-buffer-full disables core/interrupts in IRQ context and relies on stream-off reset for recovery. Test signals include DT validation failures, `media-ctl` graph links, `v4l2-compliance` subdev formats, IRQ counter/status logging under error injection, and sensor-to-DMA streaming with RAW/YUV/RGB formats.
