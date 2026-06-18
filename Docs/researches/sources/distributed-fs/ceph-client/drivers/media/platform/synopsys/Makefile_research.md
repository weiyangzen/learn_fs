# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Makefile

Purpose: descends into Synopsys HDMI RX support and builds the DesignWare MIPI CSI-2 receiver object when enabled.

Important APIs and entries: `obj-y += hdmirx/` always descends into the HDMI RX child directory. `obj-$(CONFIG_VIDEO_DW_MIPI_CSI2RX) += dw-mipi-csi2rx.o` maps the Kconfig symbol to its object.

Control flow: kbuild evaluates child HDMI RX objects through that directory and conditionally compiles the CSI-2 receiver.

State and persistence: no runtime state.

Dependencies and integration points: mirrors the Synopsys Kconfig source relationship and links the DW CSI-2 receiver into the media platform build.

Risks: child directory traversal and Kconfig sourcing must remain synchronized. If `dw-mipi-csi2rx.c` is split, this Makefile must be updated.

Test signals: media platform build with `VIDEO_DW_MIPI_CSI2RX` enabled and disabled, plus HDMI RX child build traversal.
