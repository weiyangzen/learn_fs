# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_v4l2.h

Purpose: declares the top-level atomisp V4L2/PCI helpers used by other atomisp components.

Important APIs/types/functions: forward declares `atomisp_video_pipe`, `v4l2_device`, `atomisp_device`, and `firmware`, and declares `atomisp_video_init()`, `atomisp_video_unregister()`, `atomisp_load_firmware()`, `atomisp_csi_lane_config()`, and `atomisp_register_device_nodes()`.

Control flow: no direct runtime flow; it is the shared interface for video device setup, firmware selection, CSI lane programming, and node registration implemented in `atomisp_v4l2.c`.

State and persistence: the header stores no state. All persistent runtime effects occur through `atomisp_device` and hardware touched by the implementation.

Dependencies and integration: included by subdevice and command layers that need to initialize the video pipe or register the complete media graph without including the full PCI implementation.

Risks and test signals: prototype drift is the main risk. Compile tests across atomisp translation units catch signature mismatches; runtime graph registration tests validate the declared lifecycle contract.
