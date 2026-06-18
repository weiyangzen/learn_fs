# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.h

Purpose: declares the BE2 iSCSI transport-facing API implemented by `be_iscsi.c` and consumed by the driver's transport template/main code.

Important APIs/types/functions: prototypes cover default iface create/destroy, iface parameter get/set and visibility, connection/session creation and binding, endpoint connect/poll/disconnect/get-param, host parameter retrieval, MAC formatting, connection parameter setting/start/statistics, and offload helper entry points `beiscsi_offload_connection()` and `beiscsi_offload_iscsi()`.

Control flow: this header has no runtime flow. It lets `be_main.c` register transport callbacks and lets other driver components invoke offload or session failure helpers without depending on `be_iscsi.c` internals.

State and persistence: no state is stored here. The declared functions operate on `beiscsi_hba`, `beiscsi_conn`, `iscsi_cls_session`, `iscsi_cls_conn`, and `iscsi_endpoint` objects owned by the main driver, libiscsi, and transport class.

Dependencies and integration: includes `be_main.h` and `be_mgmt.h`, binding transport declarations to the driver-private structures and firmware management types. It is the local API boundary between iSCSI transport code and the broader BE2 driver.

Risks and test signals: prototype drift affects the transport template and cross-file calls at build time. Because several functions are invoked by SCSI transport class callbacks, return semantics must stay aligned with libiscsi expectations. Test signals are full driver builds, transport registration, iface sysfs visibility, endpoint lifecycle operations, and connection start/stat callbacks through open-iscsi.
