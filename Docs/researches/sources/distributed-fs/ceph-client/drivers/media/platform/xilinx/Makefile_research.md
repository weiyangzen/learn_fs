# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/Makefile

Purpose: maps Xilinx media Kconfig symbols to build objects. The composite `xilinx-video` module is built from `xilinx-dma.o`, `xilinx-vip.o`, and `xilinx-vipp.o`.

Important build outputs: `obj-$(CONFIG_VIDEO_XILINX) += xilinx-video.o`, `obj-$(CONFIG_VIDEO_XILINX_CSI2RXSS) += xilinx-csi2rxss.o`, `obj-$(CONFIG_VIDEO_XILINX_TPG) += xilinx-tpg.o`, and `obj-$(CONFIG_VIDEO_XILINX_VTC) += xilinx-vtc.o`.

Control flow/state: no runtime state; this file controls link composition. Integration risk is mostly symbol linkage: `xilinx-dma.c`, `xilinx-vip.c`, and `xilinx-vipp.c` must be linked together because the composite driver calls exported/shared helper routines. Test signals are module build success for each enabled symbol and modpost verification of exported symbol use.
