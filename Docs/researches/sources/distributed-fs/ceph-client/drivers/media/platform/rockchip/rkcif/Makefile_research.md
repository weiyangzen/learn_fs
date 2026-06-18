# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/Makefile

Purpose: kbuild rules for the Rockchip CIF capture driver.

Important content: builds `rockchip-cif.o` when `CONFIG_VIDEO_ROCKCHIP_CIF` is enabled. The composite object includes `rkcif-capture-dvp.o`, `rkcif-capture-mipi.o`, `rkcif-dev.o`, `rkcif-interface.o`, and `rkcif-stream.o`.

Control flow/state: no runtime behavior; it controls which implementation units are linked into the module/built-in object.

Dependencies/integration: paired with `rkcif/Kconfig` and the source files named in the object list.

Risks and test signals: object list drift creates unresolved symbols or missing capture paths. Test module and built-in builds for DVP and MIPI paths.
