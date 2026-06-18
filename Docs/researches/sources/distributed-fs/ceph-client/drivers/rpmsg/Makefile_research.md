# sources/distributed-fs/ceph-client/drivers/rpmsg/Makefile

Purpose: Kbuild object map for RPMsg core, character/control/name-service helpers, and platform transports.

Important APIs/types/functions: builds core files based on `CONFIG_RPMSG*`. `qcom_glink-objs` composes `qcom_glink_native.o` and `qcom_glink_ssr.o`; `CFLAGS_qcom_glink_native.o := -I$(src)` lets trace/header includes resolve locally.

Control flow: no runtime flow; Kbuild links transport modules from selected objects.

State and persistence: build graph only.

Dependencies and integration: maps Kconfig symbols to the RPMsg bus implementation, MediaTek SCP, Qualcomm GLINK/SMD, and Virtio transport objects.

Risks and test signals: composite object drift can omit native or SSR pieces. Test modular and built-in builds for each transport and trace include generation for `qcom_glink_native.o`.
