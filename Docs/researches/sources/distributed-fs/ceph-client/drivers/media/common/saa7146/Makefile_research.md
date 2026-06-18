# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Makefile

Purpose: maps SAA7146 configuration symbols to composite kernel objects.

Important build artifacts: `saa7146.o` is built from `saa7146_i2c.o` and `saa7146_core.o`; `saa7146_vv.o` is built from `saa7146_fops.o`, `saa7146_video.o`, `saa7146_hlp.o`, and `saa7146_vbi.o`.

Control flow: `obj-$(CONFIG_VIDEO_SAA7146)` and `obj-$(CONFIG_VIDEO_SAA7146_VV)` include the base and video/VBI modules according to Kconfig.

State/persistence: no runtime state.

Dependencies/integration: mirrors the Kconfig split and keeps exported base symbols separate from optional V4L2/VB2 capture support.

Risks/test signals: object ordering matters for composite modules only at link/export level. Build tests should ensure all referenced symbols between base and VV parts resolve for both module and built-in configurations.
