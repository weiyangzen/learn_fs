# sources/distributed-fs/ceph-client/drivers/rpmsg/Kconfig

Purpose: Kconfig menu for RPMsg core, user interfaces, name service, MediaTek SCP, Qualcomm GLINK/SMD, and Virtio RPMsg transports.

Important APIs/types/functions: key symbols include `RPMSG`, `RPMSG_CHAR`, `RPMSG_CTRL`, `RPMSG_NS`, `RPMSG_MTK_SCP`, `RPMSG_QCOM_GLINK`, `RPMSG_QCOM_GLINK_RPM`, `RPMSG_QCOM_GLINK_SMEM`, `RPMSG_QCOM_SMD`, and `RPMSG_VIRTIO`. Dependencies select transport prerequisites such as NET, MTK_SCP, MAILBOX, QCOM_SMEM, VIRTIO, and RPMSG_NS.

Control flow: build-time feature selection only; transport and bus behavior lives in C files.

State and persistence: generated kernel config controls which RPMsg modules are built.

Dependencies and integration: hides `RPMSG` as a selected core and exposes transport/user API options to platform configs.

Risks and test signals: dependency changes can silently drop user APIs or transports. Test allmodconfig, minimal RPMSG transport configs, `RPMSG_CTRL` with and without `RPMSG_CHAR`, and Qualcomm/virtio dependency matrices.
