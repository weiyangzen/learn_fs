# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/Makefile

Purpose: kbuild rules for the Rockchip RGA driver.

Important content: builds `rockchip-rga.o` from `rga.o`, `rga-hw.o`, and `rga-buf.o` when `CONFIG_VIDEO_ROCKCHIP_RGA` is enabled.

Control flow/state: no runtime behavior. The object grouping defines the module link unit and internal symbol visibility.

Dependencies/integration: used by the parent Rockchip Makefile. Source files share `rga.h` and `rga-hw.h`.

Risks and test signals: missing object entries create unresolved symbols such as `rga_qops` or `rga_hw_start`. Test module and built-in builds.
