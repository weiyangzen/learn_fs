<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/imx-media.h -->
# sources/distributed-fs/ceph-client/include/linux/imx-media.h

Purpose: Provides small public definitions for i.MX media pipeline controls and private V4L2 events.

Important APIs/types/functions: `V4L2_EVENT_IMX_CLASS` and `V4L2_EVENT_IMX_FRAME_INTERVAL_ERROR` define a private event class. `enum imx_ctrl_id` reserves i.MX-specific control ids starting at `V4L2_CID_USER_IMX_BASE`, including frame interval controls.

Control flow: i.MX media drivers and userspace-facing V4L2 code use these identifiers when registering controls or emitting events.

State/persistence: No state is owned; ids are ABI-facing constants.

Dependencies/integration: Integrates with V4L2 control and event namespaces.

Risks: Numeric id stability matters for userspace; collisions with other private controls would be ABI bugs.

Test signals: V4L2 control enumeration, frame interval error event delivery, and compile checks for include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/imx-media.h -->
