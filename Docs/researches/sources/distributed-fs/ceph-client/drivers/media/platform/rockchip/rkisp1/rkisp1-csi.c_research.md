# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-csi.c

Purpose: internal MIPI CSI-2 receiver subdev for RKISP1 variants with `RKISP1_FEATURE_MIPI_CSI2`. It links sensors to the CSI receiver, configures CSI/MIPI registers and D-PHY timing, forwards streaming to the source sensor, handles MIPI interrupts, and registers the CSI media entity.

Important APIs/types/functions: exports `rkisp1_csi_link_sensor()`, `rkisp1_csi_register()`, `rkisp1_csi_unregister()`, `rkisp1_csi_init()`, and `rkisp1_csi_cleanup()`, plus ISR `rkisp1_csi_isr()` declared in common. Key internals are `rkisp1_csi_config()`, `rkisp1_csi_start()`, `rkisp1_csi_stop()`, pad format ops, and `rkisp1_csi_s_stream()`.

Control flow: platform notifier binds a sensor and calls `rkisp1_csi_link_sensor()`, which requires a `V4L2_CID_PIXEL_RATE` control and creates a sensor-to-CSI link. During stream-on, the CSI subdev finds its unique remote source, retrieves async sensor metadata, validates CSI2 D-PHY bus type, gets active sink format, configures lane count/data type/interrupt masks, computes D-PHY timing from pixel rate, powers on the D-PHY, enables CSI output, waits briefly, and starts the sensor. Stream-off stops the sensor, disables/masks CSI interrupts, synchronizes the MIPI IRQ, clears status, disables output, and powers off the PHY.

State and persistence: `struct rkisp1_csi` stores D-PHY handle, `is_dphy_errctrl_disabled`, subdev/pads, source pointer, and parent device. Active pad formats live in subdev state. No persistent storage.

Dependencies/integration: uses generic PHY MIPI D-PHY APIs, V4L2 controls/fwnode/media links, `rkisp1_mbus_info` for data types and bus widths, and platform IRQ/PM state from `rkisp1-dev.c`. The CSI source pad links to the ISP sink in `rkisp1_create_links()`.

Risks: no pixel-rate control means sensor link fails; sensors must expose accurate `V4L2_CID_PIXEL_RATE`. DPHY error-control interrupts can remain asserted for a long time, so the ISR masks them until a clean frame-end; errors after masking are counted but may not interrupt until re-enabled. Lane count is limited to 1..4. Stream-off assumes `csi->source` was set by stream-on.

Test signals: sensor binding with pixel-rate control, CSI stream-on/off ordering, D-PHY lane/pixel-clock configuration, MIPI data type selection for RAW/YUV formats, injected DPHY/CSI errors and `mipi_error` counter behavior, and pad format propagation sink to source.
