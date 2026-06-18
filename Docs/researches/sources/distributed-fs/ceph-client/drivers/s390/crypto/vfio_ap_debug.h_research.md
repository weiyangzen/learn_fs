# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_debug.h

Purpose: supplies the VFIO AP driver's s390 debug feature levels and convenience macros. It centralizes calls to `debug_sprintf_event()` so driver code can emit structured debug records through the shared `vfio_ap_dbf_info` handle.

Important APIs and functions: defines debug levels `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, and `DBF_DEBUG`, plus `DBF_MAX_SPRINTF_ARGS`. Macros `VFIO_AP_DBF`, `VFIO_AP_DBF_ERR`, `VFIO_AP_DBF_WARN`, `VFIO_AP_DBF_INFO`, and `VFIO_AP_DBF_DBG` wrap `debug_sprintf_event()` with fixed levels. The header declares external `debug_info_t *vfio_ap_dbf_info`.

Control flow: no executable control flow beyond macro expansion. Runtime behavior depends on `vfio_ap_drv.c` registering the debug area before VFIO AP operations call the macros.

State and persistence: this header owns no state. The debug area pointer is allocated, configured, and unregistered by the driver module.

Dependencies and integration: includes `asm/debug.h` and is consumed by VFIO AP driver and operations files. It integrates kernel debug feature logging with mdev, queue, interrupt, and configuration paths.

Risks: macros assume `vfio_ap_dbf_info` is valid. Calls before debug initialization or after unregister would be unsafe, so module init/exit ordering matters. `DBF_MAX_SPRINTF_ARGS` must stay aligned with registered debug entry size.

Test signals: build coverage for all macro users, module init failure paths that avoid later macro use, and dynamic debug level checks through s390 debugfs/sprintf view.
