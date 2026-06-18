# sources/distributed-fs/ceph-client/include/dt-bindings/arm/qcom,ids.h

Purpose: defines Qualcomm SoC and board identifiers used by bootloaders, older `qcom,msm-id`/`qcom,board-id` device-tree properties, and the socinfo driver.

Important APIs/types/functions: `QCOM_ID_*` constants map many MSM/APQ/MDM/IPQ/SDM/SM/SC/SA/QCM/QCS/X1/QDU/QRU/QCF/CQ product names to numeric chipset IDs. `QCOM_BOARD_ID(a, major, minor)` encodes board type plus major/minor revision. Board type constants include MTP, DragonBoard, QRD, and SBC.

Control flow: firmware or DT provides numeric IDs; platform code and socinfo match them to SoC/board revisions for compatibility handling.

State and persistence: IDs are ABI with boot firmware and DTBs. They must not be renumbered once published.

Dependencies and integration: standalone DT binding included by Qualcomm DTS files and referenced by socinfo/platform code.

Risks and test signals: duplicate or wrong numeric values can select wrong compatibility data. Test duplicate-ID scans, dt-schema validation for legacy properties, socinfo output, and boot on representative old/new Qualcomm boards.
