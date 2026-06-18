# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.h

Purpose: top-level private header for the sun6i CSI driver, tying together platform resources, V4L2/media state, bridge state, and capture state.

Important APIs and types: defines `SUN6I_CSI_NAME`, `SUN6I_CSI_DESCRIPTION`, port enum values for parallel, MIPI CSI-2, and ISP graph ports, `struct sun6i_csi_buffer`, `struct sun6i_csi_v4l2`, `struct sun6i_csi_device`, and `struct sun6i_csi_variant`. Declares `sun6i_csi_isp_complete`.

Control flow: included by platform, bridge, and capture implementation files. The platform file owns allocation and resource setup; bridge and capture files operate on the embedded substructures.

State and persistence: `struct sun6i_csi_device` is the persistent per-device driver object. It holds both standalone V4L2/media objects and pointers to the active V4L2/media ownership, allowing ISP-backed and standalone modes to share capture setup.

Dependencies and integration points: includes V4L2 device and vb2 V4L2 headers plus the bridge/capture private headers. It is the internal ABI between the three sun6i CSI objects.

Risks: because bridge and capture are embedded in one object, initialization order matters. The `isp_available` mode changes who owns V4L2/media devices and makes async completion paths more sensitive to duplicate bound callbacks.

Test signals: compile coverage for cross-file type use, ISP and no-ISP probe paths, and static analysis for initialization before use of `v4l2_dev` and `media_dev`.
