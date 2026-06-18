<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h

Purpose: Generated-style register map for the FPGA video measurement block used to detect timing stability and active/blanking dimensions.

Important APIs/types: `struct m00233_video_measure_regmap` maps IRQ status, vertical/horizontal timing counters, control, IRQ triggers, hsync timeout, and status registers. Macros define register offsets and bit masks for timing IRQ status/triggers, polarity, measure enable, interrupt enable, update-on-hsync, hsync timeout, and init-done.

Control flow: Cobalt capture start clears/enables measurement, writes `hsync_timeout_val`, and enables selected active-area IRQ triggers. IRQ handling reads `irq_status`, `status`, `vactive_area`, and `hactive_area` to decide whether frames are stable and whether CVI/freewheel can be enabled.

State/persistence: Hardware counters and status bits reflect current video signal timing. Software keeps no cache beyond values read into stream stability decisions.

Dependencies/integration: Included by `cobalt-driver.h`; used in V4L2 log-status/start and IRQ stability handling.

Risks: Struct layout must match FPGA register layout exactly. Timing masks are hard-coded and must match the bitstream. Incorrect measurements lead to skipped/error frames or false lock.

Test signals: Log-status timing values, stable/unstable frame transitions, active-area IRQs on signal changes, and hsync timeout detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/m00233_video_measure_memmap_package.h -->
