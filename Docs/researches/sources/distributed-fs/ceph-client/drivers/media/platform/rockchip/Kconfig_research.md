# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Kconfig

Purpose: top-level Kconfig include file for Rockchip media platform drivers.

Important content: emits the menu comment "Rockchip media platform drivers" and sources the per-driver Kconfig files for RGA, RK CIF, RKISP1, and RKVDEC.

Control flow/state: no runtime behavior or persisted state; it only influences kernel configuration menu visibility and dependency resolution.

Dependencies/integration: included by the parent media platform Kconfig. It delegates actual option definitions to child directories.

Risks and test signals: path mistakes break Kconfig traversal and hide drivers. Test with `make menuconfig`/`olddefconfig` and config fragments enabling Rockchip media drivers.
