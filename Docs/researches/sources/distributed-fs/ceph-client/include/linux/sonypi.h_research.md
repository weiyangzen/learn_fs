<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonypi.h -->
# sources/distributed-fs/ceph-client/include/linux/sonypi.h

Purpose: This legacy Sony Programmable I/O header preserves kernel-private command IDs used for communication between the VAIO sonypi driver and video/camera-related code.

Important APIs/types/functions: It includes `uapi/linux/sonypi.h` and defines `SONYPI_COMMAND_*` numeric constants for camera configuration. Many `GET*` commands are marked obsolete; `SET*` commands cover camera enable, brightness, contrast, hue, color, sharpness, picture, and AGC.

Control flow: Consumers pass these integer command IDs through the sonypi communication path; no functions are declared here.

State and persistence: There is no local state. Persistent effects are device-specific firmware/hardware camera settings controlled elsewhere.

Dependencies/integration: Integrates with legacy VAIO platform support and V4L-era camera glue. Depends on UAPI sonypi definitions for shared constants.

Risks and test signals: Risks are mostly compatibility and dead-code related: changing numbers can break old glue, and obsolete commands may not be handled. Test signal is compile coverage for sonypi/V4L integration and runtime command behavior on supported VAIO hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sonypi.h -->
