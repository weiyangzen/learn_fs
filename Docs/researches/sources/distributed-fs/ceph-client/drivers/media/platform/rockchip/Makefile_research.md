# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/Makefile

Purpose: top-level Rockchip media platform build dispatch.

Important content: unconditionally descends into `rga/`, `rkcif/`, `rkisp1/`, and `rkvdec/` via `obj-y`; each subdirectory Makefile gates objects on its own Kconfig symbols.

Control flow/state: no runtime state; it controls kbuild traversal.

Dependencies/integration: relies on child Makefiles defining module/object rules. It is paired with the top-level Rockchip Kconfig includes.

Risks and test signals: missing child directories or bad object names cause build failures. Test with all Rockchip media configs disabled/enabled and with `COMPILE_TEST`.
