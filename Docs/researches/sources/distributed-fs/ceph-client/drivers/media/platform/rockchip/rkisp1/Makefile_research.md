# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/Makefile

Purpose: build manifest for the `rockchip-isp1` composite kernel module.

Important APIs/types/functions: `rockchip-isp1-y` includes capture, common, CSI, platform device, ISP subdev, resizer, stats, and params objects. `rockchip-isp1-$(CONFIG_DEBUG_FS)` conditionally adds `rkisp1-debug.o`. `obj-$(CONFIG_VIDEO_ROCKCHIP_ISP1)` attaches the module to the Kconfig option.

Control flow: Kbuild links all listed objects into one module, so internal symbols declared in `rkisp1-common.h` can be shared without exporting to other modules.

State and persistence: build-time only.

Dependencies/integration: matches the Kconfig symbol and the driver’s internal source layout.

Risks: forgetting a new entity object here would build declarations but fail at link or omit runtime functionality. Debugfs code is intentionally conditional.

Test signals: module build with and without `CONFIG_DEBUG_FS`, link-time validation of all internal symbols, and `modinfo rockchip-isp1`.
