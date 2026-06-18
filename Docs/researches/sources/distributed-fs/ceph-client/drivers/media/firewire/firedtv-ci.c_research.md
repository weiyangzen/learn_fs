# sources/distributed-fs/ceph-client/drivers/media/firewire/firedtv-ci.c

Purpose: Implements DVB Conditional Access device support for FireDTV. It exposes a DVB CA device, maps CA ioctls to FireDTV AV/C CA commands, parses EN50221 message tags, and reports CI slot capability/status.

Important APIs/types/functions: `fdtv_ca_ready()` and `fdtv_get_ca_flags()` translate tuner-status CA bits. `fdtv_ca_get_caps()`, `fdtv_ca_get_slot_info()`, `fdtv_ca_get_msg()`, and `fdtv_ca_send_msg()` implement CA ioctl operations. `fdtv_ca_pmt()` strips the EN50221 length wrapper and forwards PMT payloads to `avc_ca_pmt()`. `fdtv_ca_ioctl()` dispatches `CA_RESET`, `CA_GET_CAP`, `CA_GET_SLOT_INFO`, `CA_GET_MSG`, and `CA_SEND_MSG`. `fdtv_ca_register()` conditionally registers `DVB_DEVICE_CA`, and `fdtv_ca_release()` unregisters it.

Control flow: During DVB registration, FireDTV queries tuner status and registers CA only when the module is present, initialized, error-free, and marked DVB. Userspace sends CA messages through DVB generic ioctl; the driver stores the last EN50221 tag in `fdtv->ca_last_command`, performs immediate actions for CA PMT/menu/reset, and defers app-info/CA-info response generation until `CA_GET_MSG`. Poll always reports readable.

State and persistence: Per-device state includes `fdtv->cadev`, `ca_last_command`, and `ca_time_interval`. State is runtime only. CA readiness comes from live tuner-status descriptors; no CAM data is persisted.

Dependencies/integration: Depends on Linux DVB CA uAPI, DVB device registration, FireDTV AV/C CA helpers, and `struct firedtv_tuner_status`. Integrated into `fdtv_dvb_register()`/`fdtv_dvb_unregister()`.

Risks and test signals: Test module absent/not-ready cases, slot number validation, CA PMT short/extended length parsing and bounds, unknown message/ioctl rejection, app-info and CA-info request/response ordering, date-time request handling, poll behavior, and unregister when `cadev` is absent. `fdtv_ca_release()` unconditionally calls `dvb_unregister_device(fdtv->cadev)`, so failed CA registration paths should be checked for NULL-safe behavior in the DVB core or guarded by callers.
