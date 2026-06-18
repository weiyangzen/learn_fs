# sources/distributed-fs/ceph-client/drivers/rpmsg/mtk_rpmsg.c

Purpose: MediaTek SCP RPMsg bridge that uses SCP IPI channels to create RPMsg devices and endpoints, including name-service handling.

Important APIs/types/functions: `mtk_rpmsg_rproc_subdev` tracks the platform device, transport callbacks, NS endpoint, work item, and channel list. `__mtk_create_ept()` registers an IPI handler and builds an endpoint. `mtk_rpmsg_ns_cb()` creates channels from name-service messages. `mtk_rpmsg_create_rproc_subdev()` exports a remoteproc subdevice with prepare/stop/unprepare hooks.

Control flow: remoteproc prepare creates the NS endpoint if configured. Incoming NS IPI messages enqueue channel info and schedule work to register rpmsg devices. Stop destroys the NS endpoint, cancels registration work, unregisters devices, and frees channel records.

State and persistence: channel list tracks discovered services and registered status for the remoteproc lifetime. Endpoints are kref-counted and freed on destroy.

Dependencies and integration: remoteproc subdevices, MediaTek SCP IPI callbacks from `mtk_rpmsg_info`, RPMsg core, OF child matching by `mediatek,rpmsg-name`, and workqueues.

Risks and test signals: duplicate NS announcements are not deduplicated before list insertion. `trysend` is currently blocking-equivalent. Test malformed NS messages, remoteproc crash/stop cleanup, duplicate service announcements, endpoint destroy/unregister paths, and OF subnode matching.
