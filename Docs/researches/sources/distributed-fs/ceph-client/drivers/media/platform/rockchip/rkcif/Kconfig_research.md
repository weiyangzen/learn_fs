# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Kconfig

Purpose: defines the Rockchip Camera Interface (`VIDEO_ROCKCHIP_CIF`) Kconfig option.

Important content: tristate option depending on `VIDEO_DEV`, `ARCH_ROCKCHIP || COMPILE_TEST`, `V4L_PLATFORM_DRIVERS`, and `PM && COMMON_CLK`. It selects media controller support, `VIDEOBUF2_DMA_CONTIG`, `V4L2_FWNODE`, and `VIDEO_V4L2_SUBDEV_API`. Help text describes CIF variants including PX30 VIP and RK3568 VICAP with DVP and MIPI CSI-2 receiver support; module name is `rockchip-cif`.

Control flow/state: no runtime state; it gates whether the CIF capture driver is built.

Dependencies/integration: sourced by Rockchip top-level Kconfig and paired with `rkcif/Makefile`.

Risks and test signals: dependency selection must cover subdevice, fwnode, PM, clocks, and DMA-contig requirements. Test allmodconfig/allyesconfig, non-Rockchip COMPILE_TEST, and module build naming.
